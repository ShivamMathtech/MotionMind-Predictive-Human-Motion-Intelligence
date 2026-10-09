from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, ForeignKey, JSON, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

def now(): return datetime.now(timezone.utc)
class Base(DeclarativeBase): pass
class User(Base):
    __tablename__='users'
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(80),default='Athlete')
    weight_kg:Mapped[float]=mapped_column(Float,default=70)
    settings:Mapped[dict]=mapped_column(JSON,default=dict)
class Exercise(Base):
    __tablename__='exercises'
    id:Mapped[str]=mapped_column(String(40),primary_key=True)
    definition:Mapped[dict]=mapped_column(JSON)
class WorkoutPlan(Base):
    __tablename__='workout_plans'
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(100))
    items:Mapped[list]=mapped_column(JSON)
class WorkoutSession(Base):
    __tablename__='workout_sessions'
    id:Mapped[str]=mapped_column(String(36),primary_key=True)
    plan_id:Mapped[int|None]=mapped_column(ForeignKey('workout_plans.id'))
    started:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    finished:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    mode:Mapped[str]=mapped_column(String(10))
    status:Mapped[str]=mapped_column(String(20),default='active')
    duration:Mapped[float]=mapped_column(Float,default=0)
    summary:Mapped[dict]=mapped_column(JSON,default=dict)
class ExerciseSession(Base):
    __tablename__='exercise_sessions'
    id:Mapped[int]=mapped_column(primary_key=True)
    session_id:Mapped[str]=mapped_column(ForeignKey('workout_sessions.id',ondelete='CASCADE'))
    exercise_id:Mapped[str]=mapped_column(ForeignKey('exercises.id'))
    set_number:Mapped[int]=mapped_column(Integer)
    metrics:Mapped[dict]=mapped_column(JSON,default=dict)
class Repetition(Base):
    __tablename__='repetitions'
    id:Mapped[int]=mapped_column(primary_key=True)
    exercise_session_id:Mapped[int]=mapped_column(ForeignKey('exercise_sessions.id',ondelete='CASCADE'))
    metrics:Mapped[dict]=mapped_column(JSON)
class FormScore(Base):
    __tablename__='form_scores'
    id:Mapped[int]=mapped_column(primary_key=True)
    exercise_session_id:Mapped[int]=mapped_column(ForeignKey('exercise_sessions.id',ondelete='CASCADE'))
    elapsed:Mapped[float]=mapped_column(Float)
    score:Mapped[float]=mapped_column(Float)
    components:Mapped[dict]=mapped_column(JSON)
class MotionMetric(Base):
    __tablename__='motion_metrics'
    id:Mapped[int]=mapped_column(primary_key=True)
    exercise_session_id:Mapped[int]=mapped_column(ForeignKey('exercise_sessions.id',ondelete='CASCADE'))
    elapsed:Mapped[float]=mapped_column(Float)
    metrics:Mapped[dict]=mapped_column(JSON)
class FeedbackEvent(Base):
    __tablename__='feedback_events'
    id:Mapped[int]=mapped_column(primary_key=True)
    exercise_session_id:Mapped[int]=mapped_column(ForeignKey('exercise_sessions.id',ondelete='CASCADE'))
    elapsed:Mapped[float]=mapped_column(Float)
    message:Mapped[str]=mapped_column(String(300))
class ProgressMetric(Base):
    __tablename__='progress_metrics'
    id:Mapped[int]=mapped_column(primary_key=True)
    session_id:Mapped[str]=mapped_column(ForeignKey('workout_sessions.id',ondelete='CASCADE'),unique=True)
    metrics:Mapped[dict]=mapped_column(JSON)
