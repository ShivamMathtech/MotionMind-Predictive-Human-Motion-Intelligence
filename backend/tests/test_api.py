from .test_engine import frames

def plan(c,sets=1,reps=2):
 r=c.post('/api/workouts',json={'name':'Test workout','items':[{'exercise':'squat','sets':sets,'reps':reps}]});assert r.status_code==201;return r.json()['id']
def test_crud_export_and_validation(client):
 c=client;assert c.get('/api/health').json()['status']=='ok';assert len(c.get('/api/exercises').json())==14
 pid=plan(c);assert c.get(f'/api/workouts/{pid}').json()['name']=='Test workout'
 assert c.post('/api/workouts',json={'name':'Bad','items':[{'exercise':'nonsense','sets':1,'reps':1}]}).status_code==422
 assert c.put('/api/profile',json={'name':'Test','weight_kg':71,'settings':{'skeleton':False}}).status_code==200
 assert c.get('/api/export').json()['profile']['name']=='Test'
 assert c.delete(f'/api/workouts/{pid}').status_code==200

def test_websocket_session_roundtrip(client):
 c=client;pid=plan(c);sid=c.post(f'/api/workouts/{pid}/start',json={'mode':'demo'}).json()['session_id']
 assert c.post(f'/api/workouts/{pid}/start',json={'mode':'demo'}).status_code==409
 with c.websocket_connect('/ws/motion') as ws:
  ws.send_json({'session_id':sid});assert ws.receive_json()['type']=='state'
  for f in frames():ws.send_json({'type':'pose',**f});r=ws.receive_json()
  assert r['state']['summary']['total_reps']==2 and r['state']['complete'] and r['state']['status']=='resting'
  assert c.delete('/api/history').status_code==409
  saved=c.post(f'/api/sessions/{sid}/finish').json()
 assert saved['status']=='finished' and saved['summary']['total_reps']==2
 assert c.get('/api/history').json()==[] and len(c.get('/api/history?mode=demo').json())==1
 detail=c.get(f'/api/sessions/{sid}').json();assert len(detail['sets'][0]['repetitions'])==2
 assert c.get('/api/progress?mode=demo').json()['total_reps']==2 and c.get('/api/progress?mode=camera').json()['total_reps']==0
 assert len(c.get('/api/export').json()['sessions'])==1
 assert c.post(f'/api/sessions/{sid}/finish').status_code==200
 assert c.delete('/api/history').json()['deleted'] and c.get('/api/history?mode=demo').json()==[]

def test_pause_disconnect_reconnect_and_next_set(client):
 c=client;sid=c.post(f'/api/workouts/{plan(c,2,2)}/start',json={'mode':'demo'}).json()['session_id']
 with c.websocket_connect('/ws/motion') as ws:
  ws.send_json({'session_id':sid});ws.receive_json()
  for f in frames()[:28]:ws.send_json({'type':'pose',**f});ws.receive_json()
 assert c.get('/api/sessions/active').json()['status']=='paused'
 with c.websocket_connect('/ws/motion') as ws:
  ws.send_json({'session_id':sid});assert ws.receive_json()['state']['status']=='paused'
  c.post(f'/api/sessions/{sid}/command',json={'command':'resume'})
  for f in frames():ws.send_json({'type':'pose',**{**f,'timestamp':f['timestamp']+20}});r=ws.receive_json()
  assert r['state']['summary']['total_reps']==2
  n=c.post(f'/api/sessions/{sid}/command',json={'command':'next'}).json()['state'];assert n['set']==2 and n['summary']['total_reps']==2
  c.post(f'/api/sessions/{sid}/command',json={'command':'pause'})
  for f in frames()[:3]:ws.send_json({'type':'pose',**f});r=ws.receive_json()
  assert r['state']['status']=='paused' and r['state']['summary']['total_reps']==2
  assert c.post(f'/api/sessions/{sid}/finish').status_code==200

def test_bad_frame_is_recoverable(client):
 c=client;sid=c.post(f'/api/workouts/{plan(c)}/start',json={'mode':'demo'}).json()['session_id']
 with c.websocket_connect('/ws/motion') as ws:
  ws.send_json({'session_id':sid});ws.receive_json();ws.send_json({'type':'pose','timestamp':1,'landmarks':[]});assert ws.receive_json()['type']=='error'
  ws.send_json({'type':'ping'});assert ws.receive_json()['type']=='pong'
 c.post(f'/api/sessions/{sid}/finish')
def test_data_reset(client):
 plan(client);assert client.delete('/api/data').status_code==200
 assert len(client.get('/api/workouts').json())==1 and client.get('/api/profile').json()['name']=='Athlete'

def test_prebuilt_dashboard_and_worker_mime(client):
 response=client.get('/')
 assert response.status_code==200 and 'MotionMind' in response.text
 assert client.get('/vendor/vision_bundle.js').headers['content-type'].startswith(('text/javascript','application/javascript'))
 assert client.get('/models/pose_landmarker_lite.task').status_code==200


def test_unavailable_process_metrics_do_not_break_settings(client,monkeypatch):
 import psutil
 def unavailable():raise psutil.NoSuchProcess(12345)
 monkeypatch.setattr(psutil,'Process',unavailable)
 r=client.get('/api/diagnostics')
 assert r.status_code==200 and r.json()['backend_memory_mb'] is None
