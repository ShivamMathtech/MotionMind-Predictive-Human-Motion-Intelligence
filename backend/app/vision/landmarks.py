import math
from app.config import SMOOTHING_FACTOR

def angle(a, b, c):
    u = [a[i]-b[i] for i in range(2)]; v = [c[i]-b[i] for i in range(2)]
    den = math.hypot(*u)*math.hypot(*v)
    if den < 1e-8: return None
    return math.degrees(math.acos(max(-1, min(1, sum(x*y for x,y in zip(u,v))/den))))

class PoseSmoother:
    def __init__(self, alpha=SMOOTHING_FACTOR): self.alpha=alpha; self.previous=None
    def reset(self): self.previous=None
    def apply(self, landmarks):
        if self.previous is None: self.previous=[dict(p) for p in landmarks]
        out=[{**p, **{k:self.alpha*p[k]+(1-self.alpha)*old[k] for k in ('x','y','z')}} for p,old in zip(landmarks,self.previous)]
        self.previous=out
        return out

def extract(landmarks, aspect=16/9):
    points=[(p['x']*aspect,p['y']) for p in landmarks]
    values={}
    for side,offset in [('left',0),('right',1)]:
        s,e,w,h,k,a = [i+offset for i in (11,13,15,23,25,27)]
        values[side]={
            'knee':angle(points[h],points[k],points[a]),
            'hip':angle(points[s],points[h],points[k]),
            'elbow':angle(points[s],points[e],points[w]),
            'shoulder':angle(points[h],points[s],points[e]),
            'body':angle(points[s],points[h],points[a]),
            'ankle':angle(points[k],points[a],points[31+offset]),
            'torso':math.degrees(math.atan2(abs(points[s][0]-points[h][0]),abs(points[s][1]-points[h][1])+1e-8)),
        }
    return values
