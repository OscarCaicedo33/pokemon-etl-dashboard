"""
Entry point del pipeline ETL de Pokémon.
Uso: python main.py [--phase extract|transform|load|all] [--limit N] [--no-viz]
"""

import argparse
import sys
from datetime import datetime

from loguru import logger

from src.config import LOGS_DIR, LOG_LEVEL, POKEMON_LIMIT


def setup_logger() -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"etl_{timestamp}.log"
    logger.remove()
    logger.add(sys.stderr, level=LOG_LEVEL, colorize=True,
               format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
    logger.add(str(log_file), level="DEBUG", rotation="10 MB",
               format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} | {message}")
    logger.info(f"Log guardado en: {log_file}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pipeline ETL — PokéAPI")
    parser.add_argument(
        "--phase",
        choices=["extract", "transform", "load", "all"],
        default="all",
        help="Fase del pipeline a ejecutar (default: all)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=POKEMON_LIMIT,
        help=f"Número de Pokémon a extraer (default: {POKEMON_LIMIT})",
    )
    parser.add_argument(
        "--no-viz",
        action="store_true",
        help="Omitir generación de visualizaciones",
    )
    return parser.parse_args()


def main() -> None:
    setup_logger()
    args = parse_args()

    logger.info(f"=== Pokemon ETL Pipeline | Fase: {args.phase} | Límite: {args.limit} ===")
    start = datetime.now()

    # Importaciones diferidas para no cargar módulos innecesarios
    raw_data = None
    df = None

    if args.phase in ("extract", "all"):
        from src.extract.api_client import run_extract
        raw_data = run_extract(limit=args.limit)

    if args.phase in ("transform", "all"):
        from src.transform.cleaner import run_transform
        df = run_transform(raw_data=raw_data)

    if args.phase in ("load", "all"):
        from src.load.exporter import run_load
        run_load(df=df, generate_viz=not args.no_viz)

    elapsed = (datetime.now() - start).total_seconds()
    logger.success(f"=== Pipeline completado en {elapsed:.1f}s ===")


if __name__ == "__main__":
    main()
