from collections import deque
class MovementPredictor:
    """Constant-velocity extrapolation, not a trained or calibrated ML model."""
    def __init__(self): self.history=deque(maxlen=12)
    def reset(self): self.history.clear()
    def predict(self, t, pose, progress):
        self.history.append((t,pose,progress))
        if len(self.history)<3: return {'label':'Collecting motion','method':'Trajectory baseline','reliability':None,'eta':None,'pose':[]}
        old_t,old_pose,old_p=self.history[0]; dt=t-old_t
        if dt<=0: return {'label':'Pause','method':'Trajectory baseline','reliability':None,'eta':None,'pose':[]}
        velocity=(progress-old_p)/dt
        projected=[{**p,**{k:max(-2,min(3,p[k]+max(-1,min(1,(p[k]-q[k])/dt))*.25)) for k in ('x','y','z')}} for p,q in zip(pose,old_pose)]
        changes=[self.history[i][2]-self.history[i-1][2] for i in range(1,len(self.history))]
        consistent=sum(1 for d in changes if d*velocity>=0)/len(changes)
        eta=((1-progress)/velocity if velocity>.04 else -progress/velocity if velocity<-.04 else None)
        return {'label':'Continue toward peak' if velocity>.04 else 'Return to start' if velocity<-.04 else 'Pause / hold',
          'method':'Trajectory baseline · 0.25 s horizon','reliability':round(consistent*100),
          'eta':round(min(10,max(0,eta)),1) if eta is not None else None,'pose':projected}
