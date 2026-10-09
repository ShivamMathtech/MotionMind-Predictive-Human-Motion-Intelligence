from .base_exercise import BaseExercise
from .catalog import CATALOG
class Situp(BaseExercise):
    def __init__(self): super().__init__(CATALOG['situp'])
