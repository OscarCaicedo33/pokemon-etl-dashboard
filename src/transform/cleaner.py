"""
Transformación y limpieza del dataset Pokémon.
Desanida JSON, normaliza campos y enriquece con métricas derivadas.
"""

import json
from typing import Any

import pandas as pd
from loguru import logger

from ..config import RAW_JSON_PATH, PROCESSED_CSV_PATH

GENERATION_RANGES = {
    1: (1, 151),
    2: (152, 251),
    3: (252, 386),
    4: (387, 493),
    5: (494, 649),
    6: (650, 721),
    7: (722, 809),
    8: (810, 905),
    9: (906, 1025),
}

STAT_NAMES = ["hp", "attack", "defense", "special_attack", "special_defense", "speed"]


def _extract_types(types: list[dict]) -> tuple[str, str | None]:
    sorted_types = sorted(types, key=lambda t: t["slot"])
    primary = sorted_types[0]["type"]["name"] if len(sorted_types) > 0 else None
    secondary = sorted_types[1]["type"]["name"] if len(sorted_types) > 1 else None
    return primary, secondary


def _extract_stats(stats: list[dict]) -> dict[str, int]:
    stat_map = {}
    for stat_entry in stats:
        name = stat_entry["stat"]["name"].replace("-", "_")
        stat_map[name] = stat_entry["base_stat"]
    return {s: stat_map.get(s, 0) for s in STAT_NAMES}


def _extract_abilities(abilities: list[dict]) -> list[str]:
    return [a["ability"]["name"] for a in abilities]


def _get_generation(pokemon_id: int) -> int | None:
    for gen, (low, high) in GENERATION_RANGES.items():
        if low <= pokemon_id <= high:
            return gen
    return None


def flatten_pokemon(raw: dict[str, Any]) -> dict[str, Any]:
    pokemon_id = raw["id"]
    type_primary, type_secondary = _extract_types(raw["types"])
    stats = _extract_stats(raw["stats"])
    abilities = _extract_abilities(raw["abilities"])
    bst = sum(stats.values())

    return {
        "id": pokemon_id,
        "name": raw["name"],
        "height_dm": raw["height"],
        "weight_hg": raw["weight"],
        "base_experience": raw.get("base_experience"),
        "type_primary": type_primary,
        "type_secondary": type_secondary,
        "abilities": ", ".join(abilities),
        "generation": _get_generation(pokemon_id),
        **stats,
        "bst": bst,
        "is_legendary": None,
    }


def run_transform(raw_data: list[dict[str, Any]] | None = None) -> pd.DataFrame:
    if raw_data is None:
        logger.info(f"Cargando datos crudos desde: {RAW_JSON_PATH}")
        with open(RAW_JSON_PATH, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

    logger.info(f"Transformando {len(raw_data)} registros...")
    records = [flatten_pokemon(p) for p in raw_data]
    df = pd.DataFrame(records)

    # Limpieza
    before = len(df)
    df.drop_duplicates(subset=["id"], inplace=True)
    df.dropna(subset=["name", "type_primary"], inplace=True)
    logger.info(f"Registros eliminados por limpieza: {before - len(df)}")

    # Métricas derivadas
    df["height_m"] = df["height_dm"] / 10
    df["weight_kg"] = df["weight_hg"] / 10
    df["bmi_index"] = (df["weight_kg"] / (df["height_m"] ** 2)).round(2)
    df["power_tier"] = pd.cut(
        df["bst"],
        bins=[0, 299, 399, 499, 599, 9999],
        labels=["Débil", "Bajo", "Medio", "Alto", "Legendario-tier"],
    )
    df["sprite_url"] = df["id"].apply(
        lambda pid: f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pid}.png"
    )

    df.sort_values("id", inplace=True)
    df.reset_index(drop=True, inplace=True)

    PROCESSED_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_CSV_PATH, index=False, encoding="utf-8")
    logger.success(f"Dataset limpio guardado en: {PROCESSED_CSV_PATH} ({len(df)} filas, {len(df.columns)} columnas)")

    return df
