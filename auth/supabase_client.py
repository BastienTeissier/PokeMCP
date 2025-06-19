import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


class SupabaseAuth:
    """Supabase authentication client for the Pokemon MCP server."""

    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not self.url or not self.key:
            raise ValueError(
                "Missing Supabase configuration. Please set SUPABASE_URL and "
                "SUPABASE_SERVICE_ROLE_KEY environment variables."
            )

        self.client: Client = create_client(self.url, self.key)

    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return user info.

        Args:
            token: JWT access token from Supabase

        Returns:
            User information dict if token is valid, None otherwise
        """
        try:
            user = self.client.auth.get_user(token)
            if user and user.user:
                return {
                    "id": user.user.id,
                    "email": user.user.email,
                    "metadata": user.user.user_metadata,
                    "created_at": user.user.created_at,
                }
            return None
        except Exception as e:
            print(f"Token validation failed: {e}")
            return None

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get additional user profile data from profiles table.

        Args:
            user_id: User UUID

        Returns:
            User profile dict if found, None otherwise
        """
        try:
            response = (
                self.client.table("profiles").select("*").eq("id", user_id).execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Failed to fetch user profile: {e}")
            return None

    async def create_user_profile(self, user_id: str, email: str) -> bool:
        """Create a new user profile in the profiles table.

        Args:
            user_id: User UUID
            email: User email

        Returns:
            True if profile created successfully, False otherwise
        """
        try:
            self.client.table("profiles").insert(
                {
                    "id": user_id,
                    "email": email,
                    "favorite_pokemon": [],
                    "battle_teams": {},
                    "usage_stats": {},
                }
            ).execute()
            return True
        except Exception as e:
            print(f"Failed to create user profile: {e}")
            return False
