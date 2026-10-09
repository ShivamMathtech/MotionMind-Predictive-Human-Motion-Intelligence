from .base_exercise import BaseExercise
from .catalog import CATALOG
class TricepExtension(BaseExercise):
    def __init__(self): super().__init__(CATALOG['tricep_extension'])
