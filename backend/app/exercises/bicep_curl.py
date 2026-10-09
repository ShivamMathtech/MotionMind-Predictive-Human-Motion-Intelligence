from .base_exercise import BaseExercise
from .catalog import CATALOG
class BicepCurl(BaseExercise):
    def __init__(self): super().__init__(CATALOG['bicep_curl'])
