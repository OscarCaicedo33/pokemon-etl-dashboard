#!/bin/bash
# setup.sh — Instalación única de Apache Superset (solo correr una vez)
# Uso: bash superset/setup.sh
# Ejecutar siempre desde la raiz del proyecto

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$SCRIPT_DIR/venv"
CONFIG_PATH="$SCRIPT_DIR/superset_config.py"

echo "=== Setup Apache Superset — Pokemon ETL ==="
echo ""

# 1. Entorno virtual Python 3.11
if [ ! -d "$VENV_DIR" ]; then
    echo "[1/5] Creando entorno virtual con Python 3.11..."
    python3.11 -m venv "$VENV_DIR"
else
    echo "[1/5] Entorno virtual ya existe, omitiendo."
fi

# 2. Instalar Superset
echo "[2/5] Instalando apache-superset 4.1.4 (puede tardar 2-3 min)..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet apache-superset==4.1.4

# 3-5. Inicializar desde la subcarpeta superset/ para evitar conflicto con app.py del ETL
echo "[3/5] Inicializando base de datos interna de Superset..."
cd "$SCRIPT_DIR"
SUPERSET_CONFIG_PATH="$CONFIG_PATH" FLASK_APP=superset "$VENV_DIR/bin/superset" db upgrade

echo "[4/5] Creando usuario administrador..."
SUPERSET_CONFIG_PATH="$CONFIG_PATH" FLASK_APP=superset "$VENV_DIR/bin/superset" fab create-admin \
    --username admin \
    --firstname Admin \
    --lastname Portfolio \
    --email admin@pokemon-etl.local \
    --password admin123

echo "[5/5] Inicializando roles y permisos..."
SUPERSET_CONFIG_PATH="$CONFIG_PATH" FLASK_APP=superset "$VENV_DIR/bin/superset" init

echo ""
echo "=== Setup completado ==="
echo ""
echo "Siguiente paso:  bash superset/start.sh"
echo "Luego abre:      http://localhost:8088"
echo "Usuario:         admin"
echo "Password:        admin123"
echo ""
echo "String de conexion a usar en Superset:"
echo "  sqlite:////$(realpath "$PROJECT_DIR/data/output/pokemon.db")"
