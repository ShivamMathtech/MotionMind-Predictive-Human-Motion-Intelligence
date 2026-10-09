import time, asyncio
from statistics import mean
from app.exercises import create_exercise
from app.database.database import SessionLocal
from app.database.models import ExerciseSession, WorkoutSession, Repetition, FormScore, MotionMetric, FeedbackEvent

class Runtime:
    def __init__(self,sid,items,mode,weight):
        self.id=sid; self.items=items; self.mode=mode; self.weight=weight
        self.index=0; self.set_number=1; self.exercise=create_exercise(items[0]['exercise'])
        self.status='active'; self.lock=asyncio.Lock(); self.last_sample=0.; self.last_feedback=''
        self.started=time.monotonic(); self.active_since=self.started; self.elapsed=0.; self.segments=[]
        self.latest=None; self.set_complete=False; self.complete=False; self.connected=False; self.last_received=0.
        self.segment_id=self.new_segment()
    def new_segment(self):
        with SessionLocal.begin() as db:
            seg=ExerciseSession(session_id=self.id,exercise_id=self.item['exercise'],set_number=self.set_number,metrics={})
            db.add(seg); db.flush(); return seg.id
    @property
    def item(self): return self.items[self.index]
    def duration(self): return self.elapsed+(time.monotonic()-self.active_since if self.status=='active' else 0)
    def segment_summary(self):
        e=self.exercise
        return {'exercise':e.spec.id,'set':self.set_number,'reps':e.reps,'hold_seconds':round(e.hold_seconds,1),
          'average_form':round(mean(e.scores),1) if e.scores else None,
          'average_rom':round(mean(e.roms),1) if e.roms else None,
          'average_tempo':round(mean(sum(t) for t in e.tempos),2) if e.tempos else None}
    def summary(self):
        segments=self.segments+[self.segment_summary()]
        forms=[s['average_form'] for s in segments if s['average_form'] is not None]
        roms=[s['average_rom'] for s in segments if s['average_rom'] is not None]
        tempos=[s['average_tempo'] for s in segments if s['average_tempo'] is not None]
        # Approximate MET estimate, using session active duration and mean exercise MET.
        met=mean(create_exercise(x['exercise']).spec.met for x in self.items)
        return {'segments':segments,'total_reps':sum(s['reps'] for s in segments),
          'hold_seconds':round(sum(s['hold_seconds'] for s in segments),1),
          'average_form':round(mean(forms),1) if forms else None,'average_rom':round(mean(roms),1) if roms else None,
          'average_tempo':round(mean(tempos),2) if tempos else None,
          'calories_estimate':round(met*3.5*self.weight/200*self.duration()/60,1),
          'exercise_sequence':[x['exercise'] for x in self.items]}
    def state(self):
        e=self.exercise; item=self.item
        total_sets=sum(i['sets'] for i in self.items)
        current=min(1,(e.hold_seconds if item['exercise']=='plank' else e.reps)/item['reps'])
        progress=min(1,(len(self.segments)+current)/total_sets)*100
        return {'session_id':self.id,'status':self.status,'mode':self.mode,'exercise':item['exercise'],
          'exercise_name':e.spec.name,'exercise_index':self.index,'set':self.set_number,'sets':item['sets'],
          'target':item['reps'],'duration':round(self.duration(),1),'set_complete':self.set_complete,
          'complete':self.complete,'progress':round(progress,1),'summary':self.summary()}
    def save_segment(self,db):
        seg=db.get(ExerciseSession,self.segment_id); seg.metrics=self.segment_summary()
        sess=db.get(WorkoutSession,self.id); sess.summary=self.summary(); sess.duration=self.duration(); sess.status=self.status
    def process(self,frame):
        t0=time.perf_counter()
        if self.status!='active' or self.set_complete: return {'type':'motion',**(self.latest or {}),'state':self.state()}
        data=self.exercise.update([p.model_dump() for p in frame.landmarks],frame.timestamp,frame.aspect)
        data['processing_ms']=round((time.perf_counter()-t0)*1000,2)
        self.latest=data
        count=self.exercise.hold_seconds if self.item['exercise']=='plank' else self.exercise.reps
        if count>=self.item['reps']:
            self.set_complete=True
            self.complete=self.index==len(self.items)-1 and self.set_number==self.item['sets']
            self.elapsed=self.duration(); self.status='resting'; self.exercise.reset_tracking()
        now=time.monotonic()
        if data.get('rep_event') or now-self.last_sample>=1 or self.set_complete:
            with SessionLocal.begin() as db:
                if data.get('rep_event'): db.add(Repetition(exercise_session_id=self.segment_id,metrics=data['rep_event']))
                if data.get('valid') and now-self.last_sample>=1:
                    db.add(FormScore(exercise_session_id=self.segment_id,elapsed=self.duration(),score=data['form_score'],components=data['score_parts']))
                    db.add(MotionMetric(exercise_session_id=self.segment_id,elapsed=self.duration(),metrics={k:data[k] for k in ('angle','angles','rom','tempo','phase')}))
                if data.get('feedback')!=self.last_feedback:
                    db.add(FeedbackEvent(exercise_session_id=self.segment_id,elapsed=self.duration(),message=data['feedback']))
                    self.last_feedback=data['feedback']
                self.save_segment(db)
            self.last_sample=now
        return {'type':'motion',**data,'state':self.state()}
    def command(self,command):
        if command=='pause' and self.status=='active':
            self.elapsed=self.duration(); self.status='paused'; self.exercise.reset_tracking()
        elif command=='resume' and self.status=='paused':
            self.active_since=time.monotonic(); self.status='active'; self.exercise.reset_tracking()
        elif command=='next' and not self.complete:
            with SessionLocal.begin() as db: self.save_segment(db)
            self.segments.append(self.segment_summary())
            if self.set_number<self.item['sets']: self.set_number+=1
            else: self.index+=1; self.set_number=1
            self.exercise=create_exercise(self.item['exercise']); self.segment_id=self.new_segment(); self.latest=None
            self.set_complete=False
            if self.status!='active': self.active_since=time.monotonic()
            self.status='active'
        else: raise ValueError('This command is not available in the current state.')
        with SessionLocal.begin() as db: self.save_segment(db)
        return {'type':'state','state':self.state()}
