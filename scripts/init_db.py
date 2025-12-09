import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ugc_backend.config import get_settings
from ugc_backend.db.session import Database

if __name__ == "__main__":
    settings = get_settings()
    db = Database(settings.database_url)
    db.init_db()
    print("database initialized successfully")
