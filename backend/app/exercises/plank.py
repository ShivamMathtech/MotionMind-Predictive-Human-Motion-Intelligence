from .base_exercise import BaseExercise
from .catalog import CATALOG
class Plank(BaseExercise):
    def __init__(self): super().__init__(CATALOG['plank'])
