from .base_exercise import BaseExercise
from .catalog import CATALOG
class ShoulderPress(BaseExercise):
    def __init__(self): super().__init__(CATALOG['shoulder_press'])
