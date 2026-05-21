"""
Cliente HTTP para la PokéAPI.
Maneja rate limiting, reintentos automáticos y serialización a JSON.
"""

import json
import time
from typing import Any

import requests
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from tqdm import tqdm

from ..config import POKEAPI_BASE_URL, POKEMON_LIMIT, REQUEST_DELAY, MAX_RETRIES, RAW_JSON_PATH


class PokeAPIClient:
    def __init__(self, base_url: str = POKEAPI_BASE_URL, delay: float = REQUEST_DELAY):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.RequestException),
        before_sleep=lambda retry_state: logger.warning(
            f"Reintento {retry_state.attempt_number} — {retry_state.outcome.exception()}"
        ),
    )
    def _get(self, endpoint: str) -> dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        return response.json()

    def fetch_pokemon_list(self, limit: int = POKEMON_LIMIT) -> list[dict]:
        logger.info(f"Obteniendo lista de {limit} Pokémon...")
        data = self._get(f"pokemon?limit={limit}&offset=0")
        return data["results"]

    def fetch_pokemon_detail(self, name_or_id: str | int) -> dict[str, Any]:
        return self._get(f"pokemon/{name_or_id}")

    def fetch_all_pokemon(self, limit: int = POKEMON_LIMIT) -> list[dict[str, Any]]:
        pokemon_list = self.fetch_pokemon_list(limit)
        all_pokemon = []

        logger.info(f"Descargando detalles de {len(pokemon_list)} Pokémon...")
        for entry in tqdm(pokemon_list, desc="Extrayendo", unit="pokemon"):
            try:
                detail = self.fetch_pokemon_detail(entry["name"])
                all_pokemon.append(detail)
                time.sleep(self.delay)
            except Exception as exc:
                logger.error(f"Error al obtener {entry['name']}: {exc}")

        logger.success(f"Extracción completa: {len(all_pokemon)} Pokémon descargados.")
        return all_pokemon


def run_extract(limit: int = POKEMON_LIMIT) -> list[dict[str, Any]]:
    client = PokeAPIClient()
    pokemon_data = client.fetch_all_pokemon(limit)

    RAW_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RAW_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(pokemon_data, f, ensure_ascii=False, indent=2)

    logger.info(f"Datos crudos guardados en: {RAW_JSON_PATH}")
    return pokemon_data
