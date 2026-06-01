# Apache Superset — Exploración SQL del dataset

Configuración opcional de Apache Superset como herramienta de exploración SQL sobre `pokemon.db`.  
**No es necesario para el dashboard principal** (`streamlit run app.py`). Es una capa adicional para demostrar integración con herramientas BI empresariales.

---

## ¿Para qué sirve?

Superset permite explorar el dataset con SQL, crear dashboards drag-and-drop y conectar múltiples fuentes de datos sin escribir código. Útil para demostrar:

- Conexión de SQLite a una herramienta BI estándar del mercado
- Queries SQL ad-hoc sobre `pokemon.db`
- Exportación de visualizaciones en formatos empresariales

---

## Setup

```bash
# Desde esta carpeta
cd superset

# Crear entorno virtual propio (no usa el del proyecto raíz)
python -m venv venv
source venv/bin/activate

# Instalar y configurar
bash setup.sh

# Iniciar el servidor
bash start.sh
```

Superset quedará disponible en `http://localhost:8088`.

---

## Conexión a la base de datos

En Superset → Settings → Database Connections → + Database:

| Campo | Valor |
|-------|-------|
| Database type | SQLite |
| SQLAlchemy URI | `sqlite:////ruta/absoluta/al/proyecto/data/output/pokemon.db` |

Tabla disponible: `pokemon` (151 filas × 21 columnas).

---

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `setup.sh` | Instalación de Superset y creación del admin |
| `start.sh` | Arranque del servidor en puerto 8088 |
| `superset_config.py` | Configuración personalizada (SECRET_KEY, rutas) |
| `superset_home/superset.db` | Base de datos interna de Superset (metadatos) |
