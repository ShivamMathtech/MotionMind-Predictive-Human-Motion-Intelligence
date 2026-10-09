import asyncio, json, logging, time, uuid, os
from contextlib import asynccontextmanager
from datetime import datetime,timezone,timedelta
from pathlib import Path
import psutil
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, delete
from pydantic import ValidationError
from app.config import ALLOWED_ORIGINS
from app.database.database import SessionLocal, initialize
from app.database.models import User, WorkoutPlan, WorkoutSession, ExerciseSession, Repetition, FormScore, MotionMetric, FeedbackEvent, ProgressMetric, now
from app.exercises.catalog import SPECS
from app.api.schemas import PlanInput, ProfileInput, StartInput, PoseInput
from app.analytics.insights import insights
from app.workout import Runtime

logging.basicConfig(level=logging.INFO,format='%(message)s')
log=logging.getLogger('motionmind'); runtimes:dict[str,Runtime]={}
def log_event(event,**fields): log.info(json.dumps({'event':event,**fields}))
@asynccontextmanager
async def lifespan(app):
    await asyncio.to_thread(initialize)
    log_event('startup',mode='local_single_user')
    yield
    for run in list(runtimes.values()):
        async with run.lock:
            def checkpoint():
                if run.status=='active': run.elapsed=run.duration()
                run.status='interrupted'
                with SessionLocal.begin() as db: run.save_segment(db)
            await asyncio.to_thread(checkpoint)
app=FastAPI(title='MotionMind Local API',version='1.0.0',lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=ALLOWED_ORIGINS,allow_methods=['GET','POST','PUT','DELETE'],allow_headers=['Content-Type'])
@app.get('/api/health')
def health(): return {'status':'ok','version':'1.0.0','pose_inference':'browser-worker','prediction':'deterministic trajectory baseline','storage':'local metrics only'}
@app.get('/api/exercises')
def exercises(): return [s.export() for s in SPECS]
@app.get('/api/profile')
def profile():
    with SessionLocal() as db:
        u=db.get(User,1); return {'name':u.name,'weight_kg':u.weight_kg,'settings':u.settings}
@app.put('/api/profile')
def update_profile(body:ProfileInput):
    with SessionLocal.begin() as db:
        u=db.get(User,1); u.name=body.name; u.weight_kg=body.weight_kg; u.settings=body.settings
    return body
@app.get('/api/workouts')
def plans():
    with SessionLocal() as db: return [{'id':p.id,'name':p.name,'items':p.items} for p in db.scalars(select(WorkoutPlan))]
@app.post('/api/workouts',status_code=201)
def new_plan(body:PlanInput):
    with SessionLocal.begin() as db:
        p=WorkoutPlan(name=body.name,items=[i.model_dump() for i in body.items]); db.add(p); db.flush()
        return {'id':p.id,'name':p.name,'items':p.items}
@app.get('/api/workouts/{pid}')
def get_plan(pid:int):
    with SessionLocal() as db:
        p=db.get(WorkoutPlan,pid)
        if not p: raise HTTPException(404,'Plan not found')
        return {'id':p.id,'name':p.name,'items':p.items}
@app.put('/api/workouts/{pid}')
def update_plan(pid:int,body:PlanInput):
    with SessionLocal.begin() as db:
        p=db.get(WorkoutPlan,pid)
        if not p: raise HTTPException(404,'Plan not found')
        p.name=body.name;p.items=[i.model_dump() for i in body.items]
        return {'id':p.id,'name':p.name,'items':p.items}
@app.delete('/api/workouts/{pid}')
def delete_plan(pid:int):
    if any(r.item and r.status not in ('finished','interrupted') for r in runtimes.values()): raise HTTPException(409,'Finish the active session first.')
    with SessionLocal.begin() as db:
        p=db.get(WorkoutPlan,pid)
        if not p: raise HTTPException(404,'Plan not found')
        for s in db.scalars(select(WorkoutSession).where(WorkoutSession.plan_id==pid)):s.plan_id=None
        db.delete(p)
    return {'deleted':True}
@app.post('/api/workouts/{pid}/start',status_code=201)
async def start(pid:int,body:StartInput):
    if runtimes: raise HTTPException(409,'A workout is already active. Finish or resume it first.')
    def create():
        with SessionLocal.begin() as db:
            p=db.get(WorkoutPlan,pid); u=db.get(User,1)
            if not p: raise HTTPException(404,'Plan not found')
            sid=str(uuid.uuid4()); items=p.items; weight=u.weight_kg
            db.add(WorkoutSession(id=sid,plan_id=pid,mode=body.mode,status='active',summary={}))
        return Runtime(sid,items,body.mode,weight)
    # Local single-user app; serialize starts on the event loop using a reservation lock.
    async with start_lock:
        if runtimes: raise HTTPException(409,'A workout is already active.')
        run=await asyncio.to_thread(create); runtimes[run.id]=run
    log_event('session_started',session=run.id,mode=body.mode)
    return run.state()
start_lock=asyncio.Lock()
@app.get('/api/sessions/active')
def active(): return next(iter(runtimes.values())).state() if runtimes else None
@app.post('/api/sessions/{sid}/command')
async def command(sid:str,body:dict):
    run=runtimes.get(sid)
    if not run: raise HTTPException(404,'Session is not active')
    async with run.lock:
        try: return await asyncio.to_thread(run.command,body.get('command'))
        except ValueError as exc: raise HTTPException(409,str(exc))
@app.post('/api/workouts/{sid}/finish')
@app.post('/api/sessions/{sid}/finish')
async def finish(sid:str):
    run=runtimes.get(sid)
    if not run:
        with SessionLocal() as db:
            s=db.get(WorkoutSession,sid)
            if s and s.status=='finished': return session_dict(s)
        raise HTTPException(404,'Active session not found')
    async with run.lock:
        def save():
            if run.status=='active': run.elapsed=run.duration()
            run.status='finished'; current=run.summary()
            with SessionLocal.begin() as db:
                run.save_segment(db); s=db.get(WorkoutSession,sid); s.finished=now()
                previous=None
                for old in db.scalars(select(WorkoutSession).where(WorkoutSession.status=='finished',WorkoutSession.mode==run.mode,WorkoutSession.id!=sid).order_by(WorkoutSession.started.desc())):
                    if old.summary.get('exercise_sequence')==current['exercise_sequence']: previous=old.summary;break
                current['insights']=insights(current,previous); s.summary=current
                db.add(ProgressMetric(session_id=sid,metrics=current)); return session_dict(s)
        result=await asyncio.to_thread(save); runtimes.pop(sid,None)
    log_event('session_finished',session=sid);return result

def session_dict(s):
    return {'id':s.id,'plan_id':s.plan_id,'started':s.started.replace(tzinfo=timezone.utc).isoformat(),'finished':s.finished.replace(tzinfo=timezone.utc).isoformat() if s.finished else None,
        'mode':s.mode,'status':s.status,'duration':round(s.duration,1),'summary':s.summary}
@app.get('/api/history')
def history(mode:str='camera',days:int=0):
    with SessionLocal() as db:
        q=select(WorkoutSession).order_by(WorkoutSession.started.desc())
        if mode in ('camera','demo'):q=q.where(WorkoutSession.mode==mode)
        if days>0:q=q.where(WorkoutSession.started>=now()-timedelta(days=min(days,36500)))
        return [session_dict(s) for s in db.scalars(q)]
@app.get('/api/sessions/{sid}')
def session_detail(sid:str):
    with SessionLocal() as db:
        s=db.get(WorkoutSession,sid)
        if not s: raise HTTPException(404,'Session not found')
        result=session_dict(s); result['sets']=[]
        for seg in db.scalars(select(ExerciseSession).where(ExerciseSession.session_id==sid)):
            result['sets'].append({'exercise':seg.exercise_id,'set':seg.set_number,'metrics':seg.metrics,
                'repetitions':[r.metrics for r in db.scalars(select(Repetition).where(Repetition.exercise_session_id==seg.id))],
                'feedback':[{'elapsed':f.elapsed,'message':f.message} for f in db.scalars(select(FeedbackEvent).where(FeedbackEvent.exercise_session_id==seg.id))]})
        return result
@app.get('/api/progress')
@app.get('/api/analytics')
def progress(mode:str='camera',days:int=30):
    data=[s for s in history(mode,days) if s['status']=='finished']
    volume={}
    for s in data:
        for segment in s['summary'].get('segments',[]):
            key=segment['exercise'];v=volume.setdefault(key,{'exercise':key,'reps':0,'sets':0,'hold_seconds':0})
            v['reps']+=segment['reps']; v['sets']+=1;v['hold_seconds']+=segment['hold_seconds']
    return {'sessions':list(reversed(data)),'volume':list(volume.values()),'session_count':len(data),
      'total_reps':sum(s['summary'].get('total_reps',0) for s in data),'duration':sum(s['duration'] for s in data),
      'active_days':len({s['started'][:10] for s in data})}
@app.get('/api/export')
def export():
    return {'schema_version':1,'exported_at':now().isoformat(),'profile':profile(),'plans':plans(),
      'sessions':[session_detail(s['id']) for s in history('all')]}
@app.delete('/api/history')
def clear_history():
    if runtimes: raise HTTPException(409,'Finish the active session before deleting history.')
    with SessionLocal.begin() as db:
        for model in (FeedbackEvent,MotionMetric,FormScore,Repetition,ProgressMetric,ExerciseSession,WorkoutSession):db.execute(delete(model))
    return {'deleted':True}
@app.delete('/api/data')
def clear_data():
    clear_history()
    with SessionLocal.begin() as db:
        db.execute(delete(WorkoutPlan)); u=db.get(User,1);u.name='Athlete';u.weight_kg=70;u.settings={}
    initialize()
    return {'deleted':True}
@app.get('/api/diagnostics')
def diagnostics():
    cpu=None; memory=None
    try:
        cpu=psutil.cpu_percent(interval=None)
        memory=round(psutil.Process().memory_info().rss/1048576,1)
    except (psutil.Error,OSError):
        pass  # Sandboxed/container process statistics may be unavailable.
    return {'cpu_percent':cpu,'backend_memory_mb':memory,
      'active_sessions':len(runtimes),'note':'CPU is host utilization; memory is backend only. Null means unavailable in this environment.'}
@app.websocket('/ws/motion')
async def motion(ws:WebSocket):
    origin=ws.headers.get('origin')
    if origin and origin not in ALLOWED_ORIGINS:
        await ws.close(code=1008);return
    await ws.accept();run=None;attached=False
    try:
        hello=await asyncio.wait_for(ws.receive_json(),timeout=10)
        run=runtimes.get(hello.get('session_id'))
        if not run:
            await ws.send_json({'type':'error','message':'Session expired. Start a new workout.'});await ws.close(code=1008);return
        async with run.lock:
            if run.connected:
                await ws.send_json({'type':'error','message':'Session already connected in another tab.'});await ws.close(code=1008);return
            run.connected=True; attached=True;run.exercise.reset_tracking()
        await ws.send_json({'type':'state','state':run.state()})
        while True:
            raw=await ws.receive_text()
            if len(raw)>32768:
                await ws.send_json({'type':'error','message':'Pose payload is too large.'});continue
            try:
                message=json.loads(raw)
                if message.get('type')=='ping': await ws.send_json({'type':'pong'});continue
                frame=PoseInput.model_validate(message)
                async with run.lock:
                    if run.id not in runtimes:
                        await ws.close(code=1000);break
                    result=await asyncio.to_thread(run.process,frame)
                await ws.send_json(result)
            except (ValueError,ValidationError) as exc:
                await ws.send_json({'type':'error','message':str(exc)[:250]})
            except Exception:
                log.exception(json.dumps({'event':'frame_failed','session':run.id}))
                await ws.send_json({'type':'error','message':'Frame processing failed. Pause and retry; see backend logs.'})
    except (WebSocketDisconnect,asyncio.TimeoutError):pass
    finally:
        if run and attached:
            async with run.lock:
                run.connected=False
                if run.status=='active':await asyncio.to_thread(run.command,'pause')
        log_event('socket_closed',session=run.id if run else None)

DIST=Path(__file__).resolve().parents[2]/'frontend'/'dist'
if DIST.exists():app.mount('/',StaticFiles(directory=DIST,html=True),name='frontend')
