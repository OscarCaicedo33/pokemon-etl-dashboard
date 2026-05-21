import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent

# API
POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
POKEMON_LIMIT = int(os.getenv("POKEMON_LIMIT", 151))
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", 0.3))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))

# Rutas
DATA_RAW_DIR = BASE_DIR / os.getenv("DATA_RAW_DIR", "data/raw")
DATA_PROCESSED_DIR = BASE_DIR / os.getenv("DATA_PROCESSED_DIR", "data/processed")
DATA_OUTPUT_DIR = BASE_DIR / os.getenv("DATA_OUTPUT_DIR", "data/output")
LOGS_DIR = BASE_DIR / os.getenv("LOGS_DIR", "logs")

# Archivos de salida
RAW_JSON_PATH = DATA_RAW_DIR / "pokemon_raw.json"
PROCESSED_CSV_PATH = DATA_PROCESSED_DIR / "pokemon_clean.csv"
SQLITE_DB_PATH = DATA_OUTPUT_DIR / "pokemon.db"
DASHBOARD_HTML_PATH = DATA_OUTPUT_DIR / "dashboard.html"
STATS_REPORT_PATH = DATA_OUTPUT_DIR / "stats_report.png"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Crear directorios si no existen
for directory in [DATA_RAW_DIR, DATA_PROCESSED_DIR, DATA_OUTPUT_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
