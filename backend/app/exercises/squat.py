from .base_exercise import BaseExercise
from .catalog import CATALOG
class Squat(BaseExercise):
    def __init__(self): super().__init__(CATALOG['squat'])
