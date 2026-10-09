from .base_exercise import BaseExercise
from .catalog import CATALOG
class LegRaise(BaseExercise):
    def __init__(self): super().__init__(CATALOG['leg_raise'])
