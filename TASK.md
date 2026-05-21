# Pokemon ETL — Guía de Ejecución

## Descripción
Pipeline ETL que extrae datos de todos los Pokémon desde la PokéAPI pública, los limpia y normaliza con Pandas, y genera visualizaciones interactivas con Plotly. No requiere credenciales: la API es completamente pública.

## Cuándo usar este proyecto
- "Ejecuta el pipeline de Pokémon"
- "Descarga los datos de la PokéAPI"
- "Genera el análisis de Pokémon"
- "Corre el ETL completo"
- "Muestra las visualizaciones de Pokémon"

## Prerequisitos

### Variables de entorno
La PokéAPI no requiere API key. El `.env` solo controla parámetros de ejecución:
```
POKEMON_LIMIT=151        # Cuántos Pokémon extraer (151=Gen1, 898=todos)
REQUEST_DELAY=0.5        # Segundos entre requests (respetar rate limit)
LOG_LEVEL=INFO
```

### Dependencias
```bash
pip install -r requirements.txt
```

### Requisitos del sistema
- Python 3.10+
- Conexión a internet (para consumir la API)
- ~50MB de espacio en disco para los datos

## Instalación

```bash
# Desde la carpeta del proyecto
cd "Proyecto 2 CV"

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
```

## Uso

### Pipeline completo (recomendado)
```bash
python main.py
```

### Por fase individual
```bash
python main.py --phase extract     # Solo descarga de API → data/raw/
python main.py --phase transform   # Solo limpieza → data/processed/
python main.py --phase load        # Solo export y visualizaciones → data/output/
```

### Con parámetros personalizados
```bash
python main.py --limit 151         # Solo los 151 Pokémon de Gen 1
python main.py --limit 898         # Todos los Pokémon (más lento ~15min)
python main.py --no-viz            # Sin generar visualizaciones
```

### Tests
```bash
pytest tests/ -v
```

### Exploración interactiva
```bash
jupyter notebook notebooks/
```

## Parámetros

| Parámetro | Tipo | Descripción | Requerido | Default |
|-----------|------|-------------|-----------|---------|
| `--phase` | string | Fase a ejecutar: `extract`, `transform`, `load`, `all` | No | `all` |
| `--limit` | int | Número de Pokémon a extraer | No | Valor de `.env` |
| `--no-viz` | flag | Omite la generación de visualizaciones | No | False |
| `--output-dir` | string | Directorio de salida para reportes | No | `data/output/` |

## Outputs esperados

| Archivo | Descripción |
|---------|-------------|
| `data/raw/pokemon_raw.json` | JSON crudo de la API |
| `data/processed/pokemon_clean.csv` | Dataset limpio y enriquecido |
| `data/output/pokemon.db` | Base de datos SQLite para queries |
| `data/output/dashboard.html` | Dashboard interactivo Plotly |
| `data/output/stats_report.png` | Reporte estático de estadísticas |
| `logs/etl_YYYYMMDD_HHMMSS.log` | Log completo de la ejecución |

## Solución de problemas comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `ConnectionError` | Sin internet o API caída | Verificar conexión; PokéAPI status: https://pokeapi.co |
| `RateLimitError` | Demasiados requests | Aumentar `REQUEST_DELAY` en `.env` |
| `ModuleNotFoundError` | Dependencias faltantes | Correr `pip install -r requirements.txt` |
| `FileNotFoundError` en transform | Extract no corrió primero | Correr `python main.py --phase extract` primero |
