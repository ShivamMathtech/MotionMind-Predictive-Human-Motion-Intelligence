import os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data'
DATA.mkdir(exist_ok=True)
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{DATA / "motionmind.db"}')
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://127.0.0.1:5173,http://localhost:5173,http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:8080,http://localhost:8080').split(',')
MIN_CONFIDENCE = float(os.getenv('MIN_CONFIDENCE','0.55'))
SMOOTHING_FACTOR = float(os.getenv('SMOOTHING_FACTOR','0.65'))
MIN_REP_SECONDS = float(os.getenv('MIN_REP_SECONDS','0.6'))
FEEDBACK_COOLDOWN = float(os.getenv('FEEDBACK_COOLDOWN','2'))
