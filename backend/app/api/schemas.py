from typing import Literal
from pydantic import BaseModel, Field, field_validator
from app.exercises.catalog import CATALOG
class PlanItem(BaseModel):
    exercise:str
    sets:int=Field(default=3,ge=1,le=20)
    reps:int=Field(default=12,ge=1,le=300)
    @field_validator('exercise')
    @classmethod
    def exercise_exists(cls,v):
        if v not in CATALOG: raise ValueError('Unknown exercise')
        return v
class PlanInput(BaseModel):
    name:str=Field(min_length=1,max_length=100)
    items:list[PlanItem]=Field(min_length=1,max_length=30)
class StartInput(BaseModel): mode:Literal['camera','demo']='demo'
class ProfileInput(BaseModel):
    name:str=Field(min_length=1,max_length=80)
    weight_kg:float=Field(ge=20,le=350,allow_inf_nan=False)
    settings:dict=Field(default_factory=dict)
class Landmark(BaseModel):
    x:float=Field(ge=-5,le=5,allow_inf_nan=False)
    y:float=Field(ge=-5,le=5,allow_inf_nan=False)
    z:float=Field(ge=-10,le=10,allow_inf_nan=False)
    visibility:float=Field(ge=0,le=1,allow_inf_nan=False)
class PoseInput(BaseModel):
    type:Literal['pose']
    timestamp:float=Field(ge=0,allow_inf_nan=False)
    aspect:float=Field(default=16/9,ge=.3,le=4)
    landmarks:list[Landmark]=Field(min_length=33,max_length=33)
