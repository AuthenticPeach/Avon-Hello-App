import os
from pathlib import Path

APP_NAME = "AvonHello"
APPDATA_PATH = Path(os.getenv("APPDATA")) / APP_NAME
APPDATA_PATH.mkdir(parents=True, exist_ok=True)

DB_PATH = str(APPDATA_PATH / "avon_hello.db")
SETTINGS_FILE = str(APPDATA_PATH / "settings.conf")
LOG_FILE = str(APPDATA_PATH / "error_log.txt")
