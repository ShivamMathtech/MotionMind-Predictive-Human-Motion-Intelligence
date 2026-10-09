from .base_exercise import BaseExercise
from .catalog import CATALOG
class Pushup(BaseExercise):
    def __init__(self): super().__init__(CATALOG['pushup'])
