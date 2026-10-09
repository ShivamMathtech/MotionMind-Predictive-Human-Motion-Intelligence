import os,tempfile
from pathlib import Path
_temp=tempfile.TemporaryDirectory(prefix='motionmind-tests-')
os.environ['DATABASE_URL']='sqlite:///'+str(Path(_temp.name)/'test.db')
import pytest
@pytest.fixture
def client():
 from fastapi.testclient import TestClient
 from app.main import app,runtimes
 from app.database.database import engine
 from app.database.models import Base
 runtimes.clear();Base.metadata.drop_all(engine)
 with TestClient(app) as c:yield c
 runtimes.clear()
