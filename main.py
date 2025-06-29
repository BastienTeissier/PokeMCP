import click
from fastmcp import FastMCP

from domains.pokemon import fetch_pokemon_data
from domains.type import fetch_type_effectiveness, fetch_type_weakness


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
@click.option("--port", default=8888, help="Port to listen on for SSE")
def fast(transport, port):
    # Initialize FastMCP server
    mcp = FastMCP("pokedex")

    @mcp.tool("pokedex")
    async def pokedex_tool(pokemon_name: str) -> dict:
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
        return await fetch_pokemon_data(pokemon_name)

    @mcp.tool("type_weakness")
    async def type_weakness_tool(type_name: str) -> dict:
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
        return await fetch_type_weakness(type_name)

    @mcp.tool("type_effectiveness")
    async def type_effectiveness_tool(type_name: str) -> dict:
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
        return await fetch_type_effectiveness(type_name)

    if transport == "sse":
        # If transport is SSE, run the server with the specified port
        mcp.run(transport=transport, host="127.0.0.1", port=port)
    else:
        mcp.run(transport=transport)


if __name__ == "__main__":
    # Initialize and run the server
    fast()
