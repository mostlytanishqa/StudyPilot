from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

DB_PATH = DATA_DIR / "studypilot.db"
SUBJECTS_PATH = DATA_DIR / "subjects.json"

APP_NAME = "StudyPilot"
TAGLINE = "Learn Smarter. Practise Better. Improve Faster."

DIFFICULTY_WEIGHTS = {
    "Easy": 1,
    "Medium": 2,
    "Hard": 3
}

for folder in [DATA_DIR, ASSETS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)
    