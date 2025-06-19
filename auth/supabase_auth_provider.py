from typing import Any, Dict, Optional

import jwt

from .supabase_client import SupabaseAuth


class SupabaseAuthProvider:
    """Custom FastMCP auth provider for Supabase JWT validation."""

    def __init__(self, supabase_auth: SupabaseAuth):
        self.supabase_auth = supabase_auth

    async def authenticate(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate Supabase JWT token and return user info.

        Args:
            token: JWT access token from Supabase

        Returns:
            User info dict if valid, None otherwise
        """
        try:
            # Validate token with Supabase
            user_info = await self.supabase_auth.validate_token(token)
            if not user_info:
                return None

            # Extract token claims
            # Note: We decode without verification since Supabase already validated it
            decoded = jwt.decode(token, options={"verify_signature": False})

            return {
                "token": token,
                "user_id": user_info["id"],
                "email": user_info["email"],
                "scopes": decoded.get("scopes", []),
                "expires_at": decoded.get("exp"),
                "user_info": user_info,
            }
        except Exception as e:
            print(f"Authentication failed: {e}")
            return None

    async def get_user_context(self, token: str) -> Optional[Dict[str, Any]]:
        """Get additional user context for authenticated requests.

        Args:
            token: JWT access token

        Returns:
            User context dictionary
        """
        try:
            user_info = await self.supabase_auth.validate_token(token)
            if user_info:
                # Get user profile if it exists
                profile = await self.supabase_auth.get_user_profile(user_info["id"])
                return {"user": user_info, "profile": profile}
            return None
        except Exception as e:
            print(f"Failed to get user context: {e}")
            return None
