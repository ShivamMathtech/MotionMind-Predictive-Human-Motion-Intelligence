from dataclasses import dataclass, asdict
@dataclass(frozen=True)
class ExerciseSpec:
    id: str
    name: str
    category: str
    muscles: str
    metric: str
    rest: float
    peak: float
    view: str
    instructions: str
    met: float
    difficulty: str = 'Beginner'
    sets: int = 3
    reps: int = 12
    def export(self):
        return {**asdict(self), 'required_landmarks': required(self),
          'form_rules':['Keep required joints visible.', 'Move with control.', self.instructions],
          'rep_logic':f'{self.metric}: rest {self.rest}° → peak {self.peak}° → rest; hysteresis + minimum duration',
          'tracking':'Rule-based guided mode; thresholds require individual calibration.'}

def required(s):
    return {'knee':[23,25,27],'elbow':[11,13,15], 'shoulder':[11,13,23], 'hip':[11,23,25], 'body':[11,23,27]}[s.metric]

SPECS=[
 ExerciseSpec('squat','Squat','Lower body','Quadriceps, glutes','knee',170,90,'Side view','Keep heels planted and use a comfortable squat depth.',5),
 ExerciseSpec('lunge','Lunge','Lower body','Quadriceps, glutes','knee',170,95,'Side view','Step forward under control. One return to standing is one rep.',5),
 ExerciseSpec('reverse_lunge','Reverse Lunge','Lower body','Glutes, hamstrings','knee',170,95,'Side view','Step back under control. Select this mode explicitly; direction is not inferred.',5),
 ExerciseSpec('pushup','Push-up','Upper body','Chest, triceps','elbow',170,85,'Side view','Maintain a long body line; bend and extend your elbows.',6),
 ExerciseSpec('bicep_curl','Bicep Curl','Upper body','Biceps','elbow',165,50,'Front or side','Keep upper arms steady; alternate sides are counted individually.',3.5),
 ExerciseSpec('tricep_extension','Tricep Extension','Upper body','Triceps','elbow',170,65,'Side view','Keep upper arms overhead and extend with control.',3.5),
 ExerciseSpec('shoulder_press','Shoulder Press','Upper body','Shoulders, triceps','elbow',85,165,'Front view','Start with bent elbows and press overhead without leaning back.',3.5),
 ExerciseSpec('lateral_raise','Lateral Raise','Upper body','Deltoids','shoulder',15,90,'Front view','Raise arms toward shoulder height; keep elbows softly bent.',3),
 ExerciseSpec('plank','Plank','Core','Core','body',175,175,'Side view','Hold a comfortable straight body line. This exercise tracks seconds.',3,reps=45),
 ExerciseSpec('situp','Sit-up','Core','Abdominals','hip',160,70,'Side view','Curl up under control; avoid pulling your neck.',3.8),
 ExerciseSpec('crunch','Crunch','Core','Abdominals','hip',170,135,'Side view','Small controlled movement. Camera angle strongly affects tracking.',3),
 ExerciseSpec('leg_raise','Leg Raise','Core','Abdominals, hip flexors','hip',175,90,'Side view','Raise and lower your legs slowly with a stable torso.',3.5),
 ExerciseSpec('jumping_jack','Jumping Jack','Cardio','Full body','shoulder',15,155,'Front view','Open arms and feet together; land softly.',8),
 ExerciseSpec('mountain_climber','Mountain Climber','Cardio','Core, shoulders','hip',170,75,'Side view','Draw one knee toward your chest, then return. Each drive is one rep.',8),
]
CATALOG={s.id:s for s in SPECS}
