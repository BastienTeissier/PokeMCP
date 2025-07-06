import os
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from auth.client_auth import get_current_user
from domains.pokemon import fetch_pokemon_data

# Load environment variables
load_dotenv()

# Check if authentication should be enabled
AUTH_ENABLED = os.environ.get("API_AUTH_ENABLED", "false").lower() == "true"

app = FastAPI(
    title="Pokemon MCP API",
    description="API for Pokemon data with optional OAuth2 authentication",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def optional_auth(
    user: Dict[str, Any] = Depends(get_current_user) if AUTH_ENABLED else None,
):
    """Optional authentication dependency."""
    return user


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Pokemon MCP API",
        "version": "1.0.0",
        "authentication": "enabled" if AUTH_ENABLED else "disabled",
        "endpoints": ["/pokemon/{pokemon_name}", "/docs", "/redoc"],
    }


@app.get("/pokemon/{pokemon_name}")
async def read_pokemon(
    pokemon_name: str, user: Dict[str, Any] = Depends(optional_auth)
):
    """
    Get Pokemon data by name.

    Requires authentication if AUTH_ENABLED=true in environment.
    """
    try:
        data = await fetch_pokemon_data(pokemon_name)

        # Add user context if authenticated
        if user:
            data["requested_by"] = user.get("sub", "unknown")
            data["client_id"] = user.get("client_id")

        return data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "pokemon-mcp-api",
        "auth_enabled": AUTH_ENABLED,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
