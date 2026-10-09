from .base_exercise import BaseExercise
from .catalog import CATALOG
class JumpingJack(BaseExercise):
    def __init__(self): super().__init__(CATALOG['jumping_jack'])
