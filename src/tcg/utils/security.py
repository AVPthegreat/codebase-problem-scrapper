"""Security helpers for JWT token creation and validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List

import jwt

from tcg.utils.settings import Settings


@dataclass
class UserClaims:
    """Represents the authenticated principal."""

    subject: str
    roles: List[str]


class JWTManager:
    """Minimal wrapper around PyJWT for API authentication."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def create_access_token(self, *, subject: str, roles: List[str]) -> str:
        expire_delta = timedelta(minutes=self._settings.security.access_token_expire_minutes)
        expire_at = datetime.now(tz=timezone.utc) + expire_delta

        payload = {
            "sub": subject,
            "roles": roles,
            "exp": expire_at,
        }

        token = jwt.encode(
            payload,
            self._settings.security.jwt_secret_key,
            algorithm=self._settings.security.jwt_algorithm,
        )
        return token

    def decode(self, token: str) -> UserClaims:
        decoded = jwt.decode(
            token,
            self._settings.security.jwt_secret_key,
            algorithms=[self._settings.security.jwt_algorithm],
        )
        subject = decoded.get("sub")
        roles = decoded.get("roles", [])

        if not subject:
            raise jwt.InvalidTokenError("Token missing subject")

        return UserClaims(subject=str(subject), roles=list(roles))
