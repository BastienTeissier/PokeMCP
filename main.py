from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("pokedex")

# Constants
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
        except httpx.RequestError as e:
            print(f"An error occurred while fetching data: {e}")
            return None

@mcp.tool("pokedex")
async def pokedex_tool(pokemon_name: str) -> Any: 
    """
    Fetches data for a given Pokémon from the PokeAPI.
    
    Args:
        pokemon_name (str): The name of the Pokémon to fetch.
    
    Returns:
        dict: 
            - name: The name of the Pokémon.
            - id: The ID of the Pokémon.
            - types: A list of types the Pokémon has.
            - stats: The list of stats (PV, attack, defense, Spe attack, Spe def, speed) of the Pokémon has.
    """
    data = await fetch_pokeapi_data(f"pokemon/{pokemon_name.lower()}")
    if data:
        return {
            "name": data["name"],
            "id": data["id"],
            "types": [t["type"]["name"] for t in data["types"]],
            "stats": [{"name": s["stat"]["name"], "base": s["base_stat"]} for s in data["stats"]],
        }
    else:
        return {"error": "Pokémon not found."}

@mcp.tool("type_weakness")
async def type_weakness_tool(type_name: str) -> Any:
    """
    Fetches type weakness data for a given Pokémon type from the PokeAPI.
    
    Args:
        type_name (str): The name of the Pokémon type to fetch.
    
    Returns:
        dict: 
            - name: The name of the Pokémon type.
            - double_damage_from: A list of types that deal double damage to this type.
            - half_damage_from: A list of types that deal half damage to this type.
            - no_damage_from: A list of types that deal no damage to this type.
    """
    data = await fetch_pokeapi_data(f"type/{type_name.lower()}")
    if data:
        return {
            "name": data["name"],
            "double_damage_from": [t["name"] for t in data["damage_relations"]["double_damage_from"]],
            "half_damage_from": [t["name"] for t in data["damage_relations"]["half_damage_from"]],
            "no_damage_from": [t["name"] for t in data["damage_relations"]["no_damage_from"]],
        }
    else:
        return {"error": "Type not found."}

@mcp.tool("type_effectiveness")
async def type_effectiveness_tool(type_name: str) -> Any:
    """
    Fetches type weakness data for a given Pokémon type from the PokeAPI.
    
    Args:
        type_name (str): The name of the Pokémon type to fetch.
    
    Returns:
        dict: 
            - name: The name of the Pokémon type.
            - double_damage_from: A list of types that deal double damage to this type.
            - half_damage_from: A list of types that deal half damage to this type.
            - no_damage_from: A list of types that deal no damage to this type.
    """
    data = await fetch_pokeapi_data(f"type/{type_name.lower()}")
    if data:
        return {
            "name": data["name"],
            "double_damage_to": [t["name"] for t in data["damage_relations"]["double_damage_to"]],
            "half_damage_to": [t["name"] for t in data["damage_relations"]["half_damage_to"]],
            "no_damage_to": [t["name"] for t in data["damage_relations"]["no_damage_to"]],
        }
    else:
        return {"error": "Type not found."}
    
if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')