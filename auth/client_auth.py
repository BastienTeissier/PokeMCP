import json
import os
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


class ClientAuth:
    """Client-side authentication manager for Supabase integration."""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")

        if not self.supabase_url or not self.supabase_anon_key:
            raise ValueError(
                "Missing Supabase configuration. Please set SUPABASE_URL and "
                "SUPABASE_ANON_KEY environment variables."
            )

        self.supabase: Client = create_client(self.supabase_url, self.supabase_anon_key)
        self.token_file = Path.home() / ".poke-mcp-token"

    async def login(self, email: str, password: str) -> bool:
        """Login user and store token securely.

        Args:
            email: User email
            password: User password

        Returns:
            True if login successful, False otherwise
        """
        try:
            response = self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            if response.session:
                # Store token securely
                token_data = {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at,
                    "user_id": response.user.id if response.user else None,
                    "email": response.user.email if response.user else None,
                }

                # Create token file with restricted permissions
                self.token_file.touch(mode=0o600)
                with open(self.token_file, "w") as f:
                    json.dump(token_data, f, indent=2)

                print(f"✅ Login successful! Welcome {response.user.email}")
                return True
            else:
                print("❌ Login failed: No session created")
                return False

        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False

    def get_stored_token(self) -> Optional[str]:
        """Get stored access token if valid.

        Returns:
            Access token if valid, None otherwise
        """
        try:
            if not self.token_file.exists():
                return None

            with open(self.token_file, "r") as f:
                data = json.load(f)

            access_token = data.get("access_token")
            expires_at = data.get("expires_at")

            if not access_token or not expires_at:
                return None

            # Check if token is expired (with 5 minute buffer)
            if expires_at <= int(time.time()) + 300:
                print("🔄 Token expired, attempting refresh...")
                if self._refresh_token(data.get("refresh_token")):
                    return self.get_stored_token()  # Recursive call after refresh
                else:
                    return None

            return access_token

        except Exception as e:
            print(f"⚠️  Error reading stored token: {e}")
            return None

    def _refresh_token(self, refresh_token: str) -> bool:
        """Refresh the access token using refresh token.

        Args:
            refresh_token: The refresh token

        Returns:
            True if refresh successful, False otherwise
        """
        try:
            if not refresh_token:
                return False

            response = self.supabase.auth.refresh_session(refresh_token)

            if response.session:
                # Update stored token
                token_data = {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at,
                    "user_id": response.user.id if response.user else None,
                    "email": response.user.email if response.user else None,
                }

                with open(self.token_file, "w") as f:
                    json.dump(token_data, f, indent=2)

                print("✅ Token refreshed successfully")
                return True
            else:
                print("❌ Token refresh failed")
                return False

        except Exception as e:
            print(f"❌ Token refresh failed: {e}")
            return False

    async def signup(self, email: str, password: str) -> bool:
        """Register new user.

        Args:
            email: User email
            password: User password

        Returns:
            True if signup successful, False otherwise
        """
        try:
            response = self.supabase.auth.sign_up(
                {"email": email, "password": password}
            )

            if response.user:
                print(
                    f"✅ Signup successful! Please check {email} for verification email."
                )
                return True
            else:
                print("❌ Signup failed: No user created")
                return False

        except Exception as e:
            print(f"❌ Signup failed: {e}")
            return False

    def logout(self) -> bool:
        """Logout user and clear stored token.

        Returns:
            True if logout successful, False otherwise
        """
        try:
            # Sign out from Supabase
            self.supabase.auth.sign_out()

            # Remove stored token file
            if self.token_file.exists():
                self.token_file.unlink()

            print("✅ Logged out successfully")
            return True

        except Exception as e:
            print(f"⚠️  Logout error (continuing anyway): {e}")
            # Still try to remove token file
            if self.token_file.exists():
                self.token_file.unlink()
            return True

    def get_user_info(self) -> Optional[dict]:
        """Get current user information from stored token.

        Returns:
            User info dict if available, None otherwise
        """
        try:
            if not self.token_file.exists():
                return None

            with open(self.token_file, "r") as f:
                data = json.load(f)

            return {
                "user_id": data.get("user_id"),
                "email": data.get("email"),
                "has_token": bool(data.get("access_token")),
            }

        except Exception:
            return None
