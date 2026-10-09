from importlib import import_module
from .catalog import CATALOG
def create_exercise(exercise_id):
    if exercise_id not in CATALOG: raise ValueError('Unknown exercise')
    cls=getattr(import_module(f'app.exercises.{exercise_id}'),''.join(x.title() for x in exercise_id.split('_')))
    return cls()
