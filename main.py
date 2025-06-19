
import click
from dotenv import load_dotenv
from fastmcp import FastMCP

from auth.supabase_auth_provider import SupabaseAuthProvider
from auth.supabase_client import SupabaseAuth
from domains.pokemon import fetch_pokemon_data
from domains.type import fetch_type_effectiveness, fetch_type_weakness

# Load environment variables
load_dotenv()


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
@click.option("--port", default=8888, help="Port to listen on for SSE")
@click.option("--auth", is_flag=True, help="Enable authentication")
def fast(transport, port, auth):
    # Initialize authentication if enabled
    auth_provider = None
    if auth:
        try:
            # Initialize Supabase authentication
            supabase_auth = SupabaseAuth()
            auth_provider = SupabaseAuthProvider(supabase_auth)
            print("✅ Authentication enabled with Supabase")
        except ValueError as e:
            print(f"❌ Authentication setup failed: {e}")
            print("💡 Please check your .env file and Supabase configuration")
            return
        except Exception as e:
            print(f"❌ Unexpected authentication error: {e}")
            return
    else:
        print("⚠️  Running without authentication")

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
                - requested_by: User ID (if authenticated)
        """
        result = await fetch_pokemon_data(pokemon_name)

        # Add user context if authentication is enabled
        if auth and auth_provider:
            # Note: In a real implementation, we'd get the current user context
            # This is a placeholder for the authentication integration
            result["requested_by"] = "authenticated_user"
            result["timestamp"] = "2025-06-17"

        return result

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
                - requested_by: User ID (if authenticated)
        """
        result = await fetch_type_weakness(type_name)

        # Add user context if authentication is enabled
        if auth and auth_provider:
            result["requested_by"] = "authenticated_user"
            result["timestamp"] = "2025-06-17"

        return result

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
                - requested_by: User ID (if authenticated)
        """
        result = await fetch_type_effectiveness(type_name)

        # Add user context if authentication is enabled
        if auth and auth_provider:
            result["requested_by"] = "authenticated_user"
            result["timestamp"] = "2025-06-17"

        return result

    if transport == "sse":
        # If transport is SSE, run the server with the specified port
        mcp.run(transport=transport, host="127.0.0.1", port=port)
    else:
        mcp.run(transport=transport)


if __name__ == "__main__":
    # Initialize and run the server
    fast()
