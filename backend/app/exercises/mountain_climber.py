from .base_exercise import BaseExercise
from .catalog import CATALOG
class MountainClimber(BaseExercise):
    def __init__(self): super().__init__(CATALOG['mountain_climber'])
