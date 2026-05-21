#!/bin/bash
# start.sh — Inicia Apache Superset en http://localhost:8088
# Uso: bash superset/start.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_PATH="$SCRIPT_DIR/superset_config.py"
VENV_DIR="$SCRIPT_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Superset no esta instalado. Ejecuta primero: bash superset/setup.sh"
    exit 1
fi

echo "Iniciando Apache Superset en http://localhost:8088"
echo "Usuario: admin  |  Password: admin123"
echo "Presiona Ctrl+C para detener."
echo ""

# Correr desde superset/ para evitar conflicto con app.py del ETL
cd "$SCRIPT_DIR"

SUPERSET_CONFIG_PATH="$CONFIG_PATH" \
FLASK_APP=superset \
    "$VENV_DIR/bin/superset" run \
    --port 8088 \
    --with-threads \
    --reload \
    --debugger
