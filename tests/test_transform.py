import pandas as pd
import pytest
from src.transform.cleaner import flatten_pokemon, _get_generation

MOCK_RAW = {
    "id": 1, "name": "bulbasaur", "height": 7, "weight": 69,
    "base_experience": 64,
    "types": [{"slot": 1, "type": {"name": "grass"}}, {"slot": 2, "type": {"name": "poison"}}],
    "stats": [
        {"base_stat": 45, "stat": {"name": "hp"}},
        {"base_stat": 49, "stat": {"name": "attack"}},
        {"base_stat": 49, "stat": {"name": "defense"}},
        {"base_stat": 65, "stat": {"name": "special-attack"}},
        {"base_stat": 65, "stat": {"name": "special-defense"}},
        {"base_stat": 45, "stat": {"name": "speed"}},
    ],
    "abilities": [{"ability": {"name": "overgrow"}}],
}


def test_flatten_pokemon_fields():
    record = flatten_pokemon(MOCK_RAW)
    assert record["id"] == 1
    assert record["name"] == "bulbasaur"
    assert record["type_primary"] == "grass"
    assert record["type_secondary"] == "poison"
    assert record["bst"] == 45 + 49 + 49 + 65 + 65 + 45
    assert record["generation"] == 1


def test_generation_boundaries():
    assert _get_generation(1) == 1
    assert _get_generation(151) == 1
    assert _get_generation(152) == 2
    assert _get_generation(898) == 8
    assert _get_generation(9999) is None
