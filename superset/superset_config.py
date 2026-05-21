"""
Configuración de Apache Superset para el proyecto Pokemon ETL.
Este archivo es leído por Superset al iniciarse via SUPERSET_CONFIG_PATH.
"""

import os
from pathlib import Path

# ── Seguridad ──────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SUPERSET_SECRET_KEY", "pokemon-etl-portfolio-secret-key-change-in-prod")

# ── Permite conexión a SQLite como fuente de datos ─────────────────────────────
# Necesario para conectar pokemon.db desde la interfaz de Superset
PREVENT_UNSAFE_DB_CONNECTIONS = False

# ── Base de datos interna de Superset (metadatos, usuarios, charts) ────────────
SUPERSET_HOME = Path(__file__).parent / "superset_home"
SUPERSET_HOME.mkdir(exist_ok=True)
SQLALCHEMY_DATABASE_URI = f"sqlite:///{SUPERSET_HOME}/superset.db"

# ── Interfaz ───────────────────────────────────────────────────────────────────
APP_NAME = "Pokemon ETL — Dashboard"
SUPERSET_WEBSERVER_PORT = 8088

# ── Features habilitados ───────────────────────────────────────────────────────
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_NATIVE_FILTERS": True,
}

# Permite renderizar HTML en columnas de tabla (necesario para mostrar imágenes)
HTML_SANITIZATION = False

# Permite cargar imágenes externas desde GitHub (sprites de PokéAPI)
TALISMAN_ENABLED = False

# ── Cache simple en memoria (sin Redis) ───────────────────────────────────────
CACHE_CONFIG = {
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
}
DATA_CACHE_CONFIG = CACHE_CONFIG
