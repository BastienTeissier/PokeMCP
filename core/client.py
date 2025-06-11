from typing import Any

import httpx

POKE_API_BASE = "https://pokeapi.co/api/v2/"


async def fetch_pokeapi_data(url: str) -> Any:
    """
    Fetches data for a given Pokémon from the PokeAPI.

    Args:
        pokemon_name (str): The name of the Pokémon to fetch.

    Returns:
        dict: The Pokémon data.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{POKE_API_BASE}{url}")
            response.raise_for_status()
            return response.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            print(f"An error occurred while fetching data: {e}")
            return None
