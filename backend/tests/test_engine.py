import json
from pathlib import Path
import pytest
from app.exercises import create_exercise
from app.exercises.catalog import CATALOG
from app.vision.landmarks import angle,PoseSmoother
FIXTURES=Path(__file__).resolve().parents[2]/'tests'/'fixtures'
def frames(exercise='squat'):return json.loads((FIXTURES/f'{exercise}.json').read_text())
def run_sequence(exercise='squat'):
 e=create_exercise(exercise);return e,[e.update(f['landmarks'],f['timestamp'],f['aspect']) for f in frames(exercise)]
def test_angle_and_degenerate():
 assert angle((1,0),(0,0),(0,1))==90
 assert angle((0,0),(0,0),(1,1)) is None
 assert angle((0,-1),(0,0),(0,1))==180
def test_smoothing():
 s=PoseSmoother(.5);p=[{'x':0.,'y':0.,'z':0.,'visibility':1.}]*33
 s.apply(p);assert s.apply([{**x,'x':1.} for x in p])[0]['x']==.5
 s.reset();assert s.apply(p)[0]['x']==0
@pytest.mark.parametrize('exercise',list(CATALOG))
def test_all_guided_modes(exercise):
 e,out=run_sequence(exercise);assert all(o['valid'] for o in out)
 if exercise=='plank':assert e.hold_seconds>8 and e.reps==0
 else:
  assert e.reps==2,(exercise,e.reps,[(o['angle'],o['phase']) for o in out[::12]])
  assert all(.6<=x['duration']<=20 for x in e.events)
  assert e.roms and min(e.roms)>20
 assert all(0<=o['form_score']<=100 for o in out)
 assert out[-1]['prediction']['method'].startswith('Trajectory baseline')
def test_low_visibility_cancels_partial_rep():
 e=create_exercise('squat');data=frames()
 for f in data[:28]:e.update(f['landmarks'],f['timestamp'])
 o=e.update([{**p,'visibility':.1} for p in data[28]['landmarks']],2.24)
 assert not o['valid'] and o['form_score'] is None and not o['pose']
 for f in data[29:58]:e.update(f['landmarks'],f['timestamp'])
 assert e.reps==0
def test_static_pose_cannot_count():
 e=create_exercise('squat');p=frames()[0]['landmarks']
 for i in range(100):e.update(p,i*.08)
 assert e.reps==0
def test_timestamps_and_long_gap():
 e=create_exercise('squat');data=frames()
 for f in data[:28]:e.update(f['landmarks'],f['timestamp'])
 with pytest.raises(ValueError):e.update(data[27]['landmarks'],2.)
 for f in data[28:58]:e.update(f['landmarks'],f['timestamp']+10)
 assert e.reps==0
def test_score_weights_renormalized():
 e=create_exercise('squat');assert e.calculate_score({'alignment':100,'rom':100,'stability':100,'tempo':None,'symmetry':None})==100
 assert e.calculate_score({'alignment':0,'rom':100,'stability':100,'tempo':100,'symmetry':100})==70
def test_rom_tempo_and_predictions_are_observed():
 e,out=run_sequence();assert e.calculate_rom()['best']>60 and len(e.calculate_tempo())==2
 assert any(o['prediction']['eta'] is not None for o in out[3:]) and len(out[-1]['prediction']['pose'])==33
