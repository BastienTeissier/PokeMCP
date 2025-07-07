import os
from typing import TYPE_CHECKING

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Request
from sqlmodel import Session
from starlette.responses import RedirectResponse

from .models import User

if TYPE_CHECKING:
    from sqlmodel import Engine

router = APIRouter()

# OAuth client setup
oauth = OAuth()
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=os.environ["GOOGLE_CLIENT_ID"],
    client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
    client_kwargs={"scope": "openid email profile"},
)


def setup_oauth_routes(engine: "Engine"):
    """Setup OAuth routes with database engine."""

    @router.get("/login")
    async def login(request: Request):
        """Initiate Google OAuth login."""
        redirect_uri = request.url_for("auth_google")
        return await oauth.google.authorize_redirect(request, redirect_uri)

    @router.get("/auth/google")
    async def auth_google(request: Request):
        """Handle Google OAuth callback."""
        token = await oauth.google.authorize_access_token(request)
        claims = await oauth.google.parse_id_token(request, token)

        # Store or update user in database
        with Session(engine) as db:
            user = db.query(User).filter(User.google_sub == claims["sub"]).first()
            if not user:
                user = User(
                    google_sub=claims["sub"],
                    email=claims.get("email", ""),
                    name=claims.get("name", ""),
                )
                db.add(user)
                db.commit()
                db.refresh(user)

        # Store user in session
        request.session["user"] = {
            "sub": claims["sub"],
            "email": claims.get("email", ""),
            "name": claims.get("name", ""),
        }

        return RedirectResponse(url="/me")

    @router.get("/me")
    def me(request: Request):
        """Get current user information."""
        user = request.session.get("user")
        if not user:
            return RedirectResponse("/login")
        return {"user": user}

    @router.get("/logout")
    def logout(request: Request):
        """Logout current user."""
        request.session.clear()
        return {"message": "Logged out successfully"}

    return router
