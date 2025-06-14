from core.api_client import fetch_pokeapi_data


async def fetch_pokemon_data(pokemon_name: str) -> dict:
    data = await fetch_pokeapi_data(f"pokemon/{pokemon_name.lower()}")
    if data:
        return {
            "name": data["name"],
            "id": data["id"],
            "types": [t["type"]["name"] for t in data["types"]],
            "stats": [
                {"name": s["stat"]["name"], "base": s["base_stat"]}
                for s in data["stats"]
            ],
        }
    else:
        return {"error": "Pokémon not found."}
