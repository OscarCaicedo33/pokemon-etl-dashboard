import json
import pytest
import responses as rsps
from src.extract.api_client import PokeAPIClient

BASE = "https://pokeapi.co/api/v2"

MOCK_LIST = {"results": [{"name": "bulbasaur", "url": f"{BASE}/pokemon/1/"}]}
MOCK_DETAIL = {
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
    "abilities": [{"ability": {"name": "overgrow"}}, {"ability": {"name": "chlorophyll"}}],
}


@rsps.activate
def test_fetch_pokemon_list():
    rsps.add(rsps.GET, f"{BASE}/pokemon?limit=1&offset=0", json=MOCK_LIST)
    client = PokeAPIClient()
    result = client.fetch_pokemon_list(limit=1)
    assert len(result) == 1
    assert result[0]["name"] == "bulbasaur"


@rsps.activate
def test_fetch_pokemon_detail():
    rsps.add(rsps.GET, f"{BASE}/pokemon/bulbasaur", json=MOCK_DETAIL)
    client = PokeAPIClient()
    result = client.fetch_pokemon_detail("bulbasaur")
    assert result["id"] == 1
    assert result["name"] == "bulbasaur"
