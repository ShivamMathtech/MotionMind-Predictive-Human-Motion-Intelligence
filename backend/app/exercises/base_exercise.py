from collections import deque
import math
from app.config import MIN_CONFIDENCE, MIN_REP_SECONDS, FEEDBACK_COOLDOWN
from app.vision.landmarks import PoseSmoother, extract
from app.exercises.catalog import required
from app.prediction.movement_predictor import MovementPredictor

class BaseExercise:
    """Guided, deterministic 2D exercise analysis. Scores are heuristics, not accuracy estimates."""
    def __init__(self,spec):
        self.spec=spec; self.smoother=PoseSmoother(); self.predictor=MovementPredictor()
        self.reps=0; self.hold_seconds=0.; self.phase='ready'; self.armed=False; self.peak=False
        self.start=None; self.bottom=None; self.last_t=None; self.last_progress=0.
        self.minimum=math.inf; self.maximum=-math.inf; self.cycle_min=math.inf; self.cycle_max=-math.inf
        self.roms=[]; self.tempos=[]; self.scores=[]; self.last_feedback=-99.; self.feedback='Move into position.'
        self.last_side=None; self.history=deque(maxlen=10); self.events=[]
    def reset_tracking(self):
        self.armed=False; self.peak=False; self.start=None; self.bottom=None; self.last_t=None
        self.minimum=math.inf; self.maximum=-math.inf; self.cycle_min=math.inf; self.cycle_max=-math.inf
        self.smoother.reset(); self.predictor.reset(); self.history.clear(); self.last_side=None
    def calculate_angles(self,p,aspect): return extract(p,aspect)
    def detect_phase(self,progress,delta):
        if progress<=.15: return 'top'
        if progress>=.85: return 'bottom'
        return 'toward peak' if delta>0 else 'returning'
    def count_rep(self,p,t,angle):
        event=None
        if p<=.15:
            if self.armed and self.peak and self.start is not None and self.bottom is not None:
                duration=t-self.start
                if MIN_REP_SECONDS<=duration<=20:
                    self.reps+=1
                    event={'number':self.reps,'rom':round(self.cycle_max-self.cycle_min,1),
                        'out_seconds':round(self.bottom-self.start,2),'back_seconds':round(t-self.bottom,2),'duration':round(duration,2)}
                    self.roms.append(event['rom']); self.tempos.append((event['out_seconds'],event['back_seconds']))
                    self.events.append(event)
            self.armed=True; self.peak=False; self.start=None; self.bottom=None
            self.cycle_min=angle; self.cycle_max=angle
        elif self.armed:
            if self.start is None: self.start=t
            self.cycle_min=min(self.cycle_min,angle); self.cycle_max=max(self.cycle_max,angle)
            if p>=.85 and not self.peak: self.peak=True; self.bottom=t
            if t-self.start>20: self.armed=False; self.peak=False
        return event
    def calculate_rom(self):
        return {'current':round(max(0,self.maximum-self.minimum),1) if math.isfinite(self.minimum) else 0,
          'average':round(sum(self.roms)/len(self.roms),1) if self.roms else None,'best':max(self.roms,default=None)}
    def calculate_tempo(self): return list(self.tempos[-1]) if self.tempos else None
    def evaluate_form(self,angles,side,pose,dt):
        a=angles[side]; other=angles['right' if side=='left' else 'left']; s=self.spec
        metric=a[s.metric]; tips=[]; alignment=100.
        if s.id in ('plank','pushup','mountain_climber'):
            alignment=max(0,100-abs(180-a['body'])*2)
            if a['body']<155: tips.append('Try maintaining a more neutral body line.')
        elif s.id in ('bicep_curl','lateral_raise','shoulder_press','tricep_extension'):
            alignment=max(0,100-max(0,a['torso']-15)*2)
            if a['torso']>25: tips.append('Try keeping your torso steadier.')
        else:
            alignment=max(0,100-max(0,a['torso']-55)*1.2)
            if a['torso']>65 and s.category=='Lower body': tips.append('Consider a more upright torso within a comfortable range.')
        bilateral=all(pose[i]['visibility']>=MIN_CONFIDENCE for i in required(s)+[i+1 for i in required(s)])
        symmetry=max(0,100-abs(metric-other[s.metric])*2) if bilateral and other[s.metric] is not None else None
        # Asymmetry is expected for alternating exercises.
        if s.id in ('lunge','reverse_lunge','mountain_climber'): symmetry=None
        self.history.append(metric)
        acceleration=abs(self.history[-1]-2*self.history[-2]+self.history[-3]) if len(self.history)>2 else 0
        stability=max(0,100-acceleration*3)
        rom=min(100,(self.maximum-self.minimum)/max(1,abs(s.rest-s.peak))*100) if s.id!='plank' else alignment
        tempo=None
        if self.tempos:
            duration=sum(self.tempos[-1]); tempo=max(0,100-max(0,1.5-duration)*60-max(0,duration-8)*8)
            if duration<1.2: tips.append('Slow down and move with control.')
        return {'alignment':round(alignment),'rom':round(rom),'stability':round(stability),
          'tempo':round(tempo) if tempo is not None else None,'symmetry':round(symmetry) if symmetry is not None else None},tips
    def calculate_score(self,parts):
        weights={'alignment':.30,'rom':.25,'stability':.20,'tempo':.15,'symmetry':.10}
        available={k:v for k,v in parts.items() if v is not None}
        return round(sum(v*weights[k] for k,v in available.items())/sum(weights[k] for k in available))
    def generate_feedback(self,t,tips,event):
        if t-self.last_feedback>=FEEDBACK_COOLDOWN:
            self.feedback=tips[0] if tips else 'Repetition complete. Keep moving with control.' if event else self.spec.instructions
            self.last_feedback=t
        return self.feedback
    def update(self,raw,t,aspect=16/9):
        if self.last_t is not None and t<=self.last_t: raise ValueError('Frame timestamps must increase.')
        if self.last_t is not None and t-self.last_t>.8: self.reset_tracking()
        ids=required(self.spec)
        sides={s:min(raw[i+o]['visibility'] for i in ids) for s,o in [('left',0),('right',1)]}
        side=max(sides,key=sides.get); confidence=sides[side]
        if confidence<MIN_CONFIDENCE:
            self.reset_tracking()
            return {'valid':False,'feedback':'Pose confidence low. Move into frame with the required joints visible.','reps':self.reps,'hold_seconds':round(self.hold_seconds,1),'confidence':round(confidence,2),'form_score':None,'phase':'no pose','pose':[],'prediction':None,'rep_event':None}
        # Preserve the tracked side unless it becomes occluded; switching cancels partial reps.
        if self.spec.id not in ('lunge','reverse_lunge','mountain_climber') and self.last_side and sides[self.last_side]>=MIN_CONFIDENCE: side=self.last_side
        if self.last_side and self.last_side!=side and self.spec.id not in ('lunge','reverse_lunge','mountain_climber'): self.reset_tracking()
        self.last_side=side
        p=self.smoother.apply(raw); angles=self.calculate_angles(p,aspect)
        if self.spec.id in ('lunge','reverse_lunge','mountain_climber'):
            good=[s for s in sides if sides[s]>=MIN_CONFIDENCE and angles[s][self.spec.metric] is not None]
            side=min(good,key=lambda s:angles[s][self.spec.metric]) if good else side
        a=angles[side]; value=a[self.spec.metric]
        if value is None or any(a[k] is None for k in ('body','torso')):
            self.reset_tracking(); return {'valid':False,'feedback':'Required joints overlap. Change your camera angle.','reps':self.reps,'hold_seconds':round(self.hold_seconds,1),'confidence':0,'form_score':None,'phase':'no pose','pose':[],'prediction':None,'rep_event':None}
        dt=min(.3,t-self.last_t) if self.last_t is not None else 0.; self.last_t=t
        self.minimum=min(self.minimum,value); self.maximum=max(self.maximum,value)
        progress=max(0,min(1,(value-self.spec.rest)/(self.spec.peak-self.spec.rest))) if self.spec.id!='plank' else 0.
        delta=progress-self.last_progress; self.last_progress=progress
        parts,tips=self.evaluate_form(angles,side,p,dt); event=None
        if self.spec.id=='plank':
            self.phase='holding' if a['body']>=155 and a['torso']>55 else 'adjust position'
            if self.phase=='holding': self.hold_seconds+=dt
            else: tips.insert(0,'Use a side view and keep your body roughly horizontal.')
        else:
            self.phase=self.detect_phase(progress,delta)
            # Horizontal exercise modes must not count standing elbow/hip bends.
            posture_ok=self.spec.id not in ('pushup','mountain_climber') or a['torso']>50
            if posture_ok: event=self.count_rep(progress,t,value)
            else: self.armed=False; self.peak=False; tips.insert(0,'Use a side view with your torso roughly horizontal.')
        score=self.calculate_score(parts); self.scores.append(score)
        if len(self.scores)>10000: self.scores=self.scores[-5000:]
        if event: event['form_score']=score
        feedback=self.generate_feedback(t,tips,event)
        return {'valid':True,'exercise':self.spec.id,'reps':self.reps,'hold_seconds':round(self.hold_seconds,1),
          'phase':self.phase,'confidence':round(confidence,2),'form_score':score,'score_parts':parts,
          'angle':round(value,1),'angles':{k:round(v,1) if v is not None else None for k,v in a.items()},
          'side':side,'rom':self.calculate_rom(),'tempo':self.calculate_tempo(),'feedback':feedback,
          'prediction':self.predictor.predict(t,p,progress),'pose':p,'rep_event':event,
          'recognition':'Squat pattern' if self.spec.id=='squat' and a['torso']<60 and .2<progress else 'Guided '+self.spec.name}
