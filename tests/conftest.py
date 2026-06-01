"""
Configuración compartida para pytest.
Fixtures disponibles en todos los módulos de test sin necesidad de importarlas.
"""

import json
import pytest
import pandas as pd


MOCK_POKEMON_RAW = {
    "id": 1,
    "name": "bulbasaur",
    "height": 7,
    "weight": 69,
    "base_experience": 64,
    "types": [
        {"slot": 1, "type": {"name": "grass"}},
        {"slot": 2, "type": {"name": "poison"}},
    ],
    "stats": [
        {"base_stat": 45, "stat": {"name": "hp"}},
        {"base_stat": 49, "stat": {"name": "attack"}},
        {"base_stat": 49, "stat": {"name": "defense"}},
        {"base_stat": 65, "stat": {"name": "special-attack"}},
        {"base_stat": 65, "stat": {"name": "special-defense"}},
        {"base_stat": 45, "stat": {"name": "speed"}},
    ],
    "abilities": [
        {"ability": {"name": "overgrow"}},
        {"ability": {"name": "chlorophyll"}},
    ],
}


@pytest.fixture
def raw_pokemon():
    """Un registro crudo de la PokéAPI listo para pasar a flatten_pokemon."""
    return MOCK_POKEMON_RAW.copy()


@pytest.fixture
def raw_pokemon_list():
    """Lista de tres registros crudos para tests que requieren colección."""
    base = MOCK_POKEMON_RAW.copy()
    records = []
    for i, (name, hp) in enumerate([("bulbasaur", 45), ("ivysaur", 60), ("venusaur", 80)], start=1):
        rec = {**base, "id": i, "name": name, "stats": [
            {"base_stat": hp,  "stat": {"name": "hp"}},
            {"base_stat": 49,  "stat": {"name": "attack"}},
            {"base_stat": 49,  "stat": {"name": "defense"}},
            {"base_stat": 65,  "stat": {"name": "special-attack"}},
            {"base_stat": 65,  "stat": {"name": "special-defense"}},
            {"base_stat": 45,  "stat": {"name": "speed"}},
        ]}
        records.append(rec)
    return records


@pytest.fixture
def clean_dataframe():
    """DataFrame limpio mínimo equivalente al CSV procesado."""
    from src.transform.cleaner import flatten_pokemon
    record = flatten_pokemon(MOCK_POKEMON_RAW)
    return pd.DataFrame([record])
