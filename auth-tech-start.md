# Auth Tech Start: MCP Server Authentication

## 1. Overview

This document outlines the technical strategy for implementing OAuth 2.0 authentication for the FastMCP server. The goal is to secure the MCP tools and API endpoints, ensuring that only authorized clients can access them.

This strategy is based on the reference architecture provided in `authentication-implementation.md` and adapted to the existing `poke-mcp` project structure.

## 2. Core Components

The implementation will consist of two main components:

1.  **Auth Server:** An OAuth 2.0 provider responsible for authenticating users and issuing access tokens.
2.  **MCP Server:** The existing FastMCP server, modified to validate access tokens and enforce authentication on its tools and API endpoints.

## 3. Auth Server Implementation

We will create a new `auth_server` directory to house the authentication server. This server will be a standalone FastAPI application.

### 3.1. Project Structure

```
poke-mcp/
├── auth_server/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── keymgr.py
│   └── oauth_google.py
├── ... (existing files)
```

### 3.2. Dependencies

The following dependencies will be added to `pyproject.toml`:

-   `authlib`
-   `sqlmodel`
-   `psycopg2-binary` (or `asyncpg` if we use an async driver)
-   `alembic`
-   `python-dotenv`
-   `uvicorn`

### 3.3. `auth_server/models.py`

This file will define the database models for storing OAuth 2.0 client and token information using `sqlmodel`.

-   `OAuth2Client`: Stores client information (client_id, client_secret, etc.).
-   `OAuth2Token`: Stores access and refresh tokens.

### 3.4. `auth_server/keymgr.py`

This file will be responsible for generating and managing the RSA key pair used for signing JWTs.

-   It will generate a private key and store it in a file if one doesn't exist.
-   It will provide a function to expose the public key as a JWKS (JSON Web Key Set).

### 3.5. `auth_server/oauth_google.py`

This file will handle the Google OAuth 2.0 login flow.

-   It will use `authlib` to register Google as an OAuth provider.
-   It will define the `/login` and `/auth/google` endpoints for initiating the login process and handling the callback from Google.
-   It will store the authenticated user's information in the session.

### 3.6. `auth_server/main.py`

This will be the main entry point for the auth server.

-   It will initialize the FastAPI application.
-   It will set up the database connection and create the tables on startup.
-   It will configure the `authlib` `AuthorizationServer` with the necessary grants (Authorization Code, Client Credentials).
-   It will expose the following endpoints:
    -   `/.well-known/jwks.json`: To publish the public key.
    -   `/register`: For dynamic client registration.
    -   `/token`: For issuing access tokens.
    -   `/authorize`: For the authorization code flow.

## 4. MCP Server Modifications

The existing MCP server (`main.py` and `api.py`) will be modified to enforce authentication.

### 4.1. `main.py`

-   The `fast` function will be updated to initialize the `FastMCP` server with a `BearerAuthProvider`.
-   The `BearerAuthProvider` will be configured with the JWKS URI and issuer of the auth server.

```python
from fastmcp.server.auth import BearerAuthProvider

# ...

def fast(transport, port):
    auth = BearerAuthProvider(
        jwks_uri="http://localhost:8000/.well-known/jwks.json",
        issuer="http://localhost:8000",
        audience="mcp"  # This should match the audience claim in the JWT
    )
    mcp = FastMCP("pokedex", auth=auth)
    # ...
```

### 4.2. `api.py`

-   The FastAPI application in `api.py` will be protected using a dependency that validates the JWT.
-   We will create a new `auth/api_auth.py` file to contain the authentication logic for the API.

```python
# auth/api_auth.py
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import httpx

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Logic to fetch JWKS, decode and validate the token
    # ...
    return user_payload
```

-   The `read_pokemon` endpoint in `api.py` will be updated to use this dependency.

```python
# api.py
from fastapi import FastAPI, Depends
from .auth.api_auth import get_current_user

# ...

@app.get("/pokemon/{pokemon_name}")
async def read_pokemon(pokemon_name: str, user: dict = Depends(get_current_user)):
    return await fetch_pokemon_data(pokemon_name)
```

## 5. Configuration and Setup

-   A `.env` file will be used to store configuration for both the auth and MCP servers (database credentials, Google client ID/secret, etc.).
-   A `docker-compose.yml` file will be created to orchestrate the auth server, MCP server, and a PostgreSQL database.
-   Alembic will be used to manage database migrations for the auth server.

## 6. Development and Testing Plan

1.  **Implement the Auth Server:**
    -   Create the `auth_server` directory and files.
    -   Implement the models, key manager, and Google OAuth flow.
    -   Implement the main auth server application.
2.  **Integrate Auth with MCP Server:**
    -   Update `main.py` to use `BearerAuthProvider`.
    -   Implement the API authentication logic in `auth/api_auth.py`.
    -   Update `api.py` to protect the endpoint.
3.  **Set up Docker Compose:**
    -   Create the `docker-compose.yml` file.
    -   Configure the services.
4.  **Write Smoke Tests:**
    -   Create a script to test the entire authentication flow, from logging in with Google to accessing a protected MCP tool.
5.  **Documentation:**
    -   Update the `README.md` with instructions on how to set up and run the authenticated application.
