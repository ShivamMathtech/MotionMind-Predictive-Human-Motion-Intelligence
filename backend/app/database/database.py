from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL
from .models import Base, User, Exercise, WorkoutPlan, WorkoutSession
from app.exercises.catalog import SPECS
engine=create_engine(DATABASE_URL,connect_args={'check_same_thread':False} if DATABASE_URL.startswith('sqlite') else {})
if DATABASE_URL.startswith('sqlite'):
    @event.listens_for(engine,'connect')
    def configure_sqlite(dbapi_connection,_):
        dbapi_connection.execute('PRAGMA foreign_keys=ON')
        dbapi_connection.execute('PRAGMA journal_mode=WAL')
        dbapi_connection.execute('PRAGMA busy_timeout=5000')
SessionLocal=sessionmaker(engine,expire_on_commit=False)
def initialize():
    Base.metadata.create_all(engine)
    with SessionLocal.begin() as db:
        if not db.get(User,1): db.add(User(id=1,name='Athlete',weight_kg=70,settings={}))
        for spec in SPECS:
            if not db.get(Exercise,spec.id): db.add(Exercise(id=spec.id,definition=spec.export()))
        if not db.scalar(select(WorkoutPlan)):
            db.add(WorkoutPlan(name='Full Body Foundations',items=[{'exercise':'squat','sets':3,'reps':12},{'exercise':'pushup','sets':3,'reps':10},{'exercise':'lunge','sets':2,'reps':12},{'exercise':'plank','sets':2,'reps':30}]))
        for s in db.scalars(select(WorkoutSession).where(WorkoutSession.status.in_(['active','paused','resting']))): s.status='interrupted'
