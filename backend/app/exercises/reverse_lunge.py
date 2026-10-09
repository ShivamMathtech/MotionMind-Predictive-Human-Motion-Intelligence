from .base_exercise import BaseExercise
from .catalog import CATALOG
class ReverseLunge(BaseExercise):
    def __init__(self): super().__init__(CATALOG['reverse_lunge'])
