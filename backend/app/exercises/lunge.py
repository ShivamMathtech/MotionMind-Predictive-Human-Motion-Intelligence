from .base_exercise import BaseExercise
from .catalog import CATALOG
class Lunge(BaseExercise):
    def __init__(self): super().__init__(CATALOG['lunge'])
