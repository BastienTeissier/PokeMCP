import uuid

from datetime import datetime
from typing import List, Optional

from sqlmodel import JSON, Column, Field, SQLModel


class OAuth2Client(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    client_id: str = Field(index=True, unique=True)
    client_secret: Optional[str]
    grant_types: List[str] = Field(sa_column=Column(JSON))
    redirect_uris: List[str] = Field(sa_column=Column(JSON))
    scope: Optional[str]
    issued_at: datetime = Field(default_factory=datetime.now)

class OAuth2Token(SQLModel, table=True):
    """OAuth 2.0 Token model for storing access and refresh tokens."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    client_id: str = Field(index=True)
    subject: Optional[str]
    scope: str
    issued_at: datetime = Field(default_factory=datetime.now)
    expires_in: int
    access_token: str
    refresh_token: Optional[str]

class User(SQLModel, table=True):
    """User model for storing authenticated users."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    google_sub: str = Field(index=True, unique=True)
    email: str
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)