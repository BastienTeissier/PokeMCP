import os

from authlib.integrations.sqla_oauth2 import (
    create_query_client_func,
    create_save_token_func,
)
from authlib.oauth2 import AuthorizationServer
from authlib.oauth2.rfc6749.grants import AuthorizationCodeGrant, ClientCredentialsGrant
from authlib.oauth2.rfc7591 import ClientRegistrationEndpoint
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from sqlmodel import Session, SQLModel, create_engine
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

from .keymgr import RSA_KEY, public_jwks
from .models import OAuth2Client, OAuth2Token
from .oauth_google import setup_oauth_routes

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = (
    f"postgresql+asyncpg://{os.environ['POSTGRES_USER']}:"
    f"{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}:"
    f"{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"
)

engine = create_engine(DATABASE_URL, echo=False)

# FastAPI app
app = FastAPI(title="Pokemon MCP Auth Server", version="1.0.0")
app.add_middleware(SessionMiddleware, secret_key=os.environ["SESSION_SECRET"])

# Setup OAuth routes
google_router = setup_oauth_routes(engine)
app.include_router(google_router)


@app.on_event("startup")
def create_tables():
    """Create database tables on startup."""
    SQLModel.metadata.create_all(engine)


# OAuth2 Server Setup
query_client = create_query_client_func(engine, OAuth2Client)
save_token = create_save_token_func(engine, OAuth2Token)

server = AuthorizationServer(
    query_client=query_client,
    save_token=save_token,
    generate_token="jwt",
    jwt_config={
        "key": RSA_KEY,
        "alg": "RS256",
        "iss": os.environ.get("AUTH_SERVER_URL", "http://localhost:8000"),
        "aud": "mcp",
    },
)

# Register OAuth2 grants
server.register_grant(AuthorizationCodeGrant, [dict(require_nonce=True)])
server.register_grant(ClientCredentialsGrant)


class DynamicClientRegistration(ClientRegistrationEndpoint):
    """Dynamic client registration endpoint."""

    def save_client(self, client_info, client_metadata, request):
        with Session(engine) as db:
            client = OAuth2Client(**client_info, **client_metadata)
            db.add(client)
            db.commit()
            db.refresh(client)
        return client


server.register_endpoint(DynamicClientRegistration)


# OAuth2 Endpoints
@app.get("/.well-known/jwks.json")
def jwks():
    """Public key endpoint for JWT verification."""
    return public_jwks()


@app.post("/register")
async def register_client(request: Request):
    """Dynamic client registration endpoint."""
    return await server.create_endpoint_response("client_registration", request)


@app.post("/token")
async def issue_token(request: Request):
    """Token issuance endpoint."""
    return await server.create_token_response(request)


@app.get("/authorize")
async def authorize(request: Request):
    """Authorization endpoint for OAuth2 code flow."""
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login")

    return await server.create_authorization_response(request, grant_user=user["sub"])


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "auth-server"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=os.environ.get("AUTH_SERVER_HOST", "0.0.0.0"),
        port=int(os.environ.get("AUTH_SERVER_PORT", 8000)),
    )
