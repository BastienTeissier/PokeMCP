from core.client import fetch_pokeapi_data


def parse_type_data(data: dict) -> dict:
    return {
        "name": data["name"],
        "double_damage_from": [
            t["name"] for t in data["damage_relations"]["double_damage_from"]
        ],
        "half_damage_from": [
            t["name"] for t in data["damage_relations"]["half_damage_from"]
        ],
        "no_damage_from": [
            t["name"] for t in data["damage_relations"]["no_damage_from"]
        ],
    }


async def fetch_type_weakness(type_name: str) -> dict:
    data = await fetch_pokeapi_data(f"type/{type_name.lower()}")
    if data:
        return parse_type_data(data)
    else:
        return {"error": "Type not found."}


async def fetch_type_effectiveness(type_name: str) -> dict:
    data = await fetch_pokeapi_data(f"type/{type_name.lower()}")
    if data:
        return parse_type_data(data)
    else:
        return {"error": "Type not found."}
