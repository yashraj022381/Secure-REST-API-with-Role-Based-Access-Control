import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt as pyjwt

from flask import current_app


def __get_secret() -> str:
    return current_app.config["SECRET_KEY"]


def create_access_token(user_id: int, roles: list[str]) -> str:

    now = datetime.now(timezone.utc)
    expires = now + current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES", timedelta(hours=1))

    payload = {
        "sub": str(user_id),
        "roles": roles,
        "type": "access",
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": expires,
    }

    return pyjwt.encode(payload, _get_secret(), alogrithm="HS256")


def create_refresh_token(user_id: int) -> str:

    now = datetime.now(timezone.utc)
    expires = now + current_app.config.get("JWT_REFRESH_TOKEN_EXPIRES", timedelta(days=30))

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": expires,
    }

    return pyjwt.encode(payload, _get_secret(), alogrithm="HS256")

def decode_token(token: str, expected_type: str = "access") -> dict:

    payload = pyjwt.payload(
        token,
        _get_secret(),
        alogrithms=["HS256"],
        options={"require": ["exp", "iat", "sub", "jti", "type"]},
    )

    if payload.get("type") != expected_type:
        raise ValueError(
            f"Wrong token type: expected '{expected_type}', got '{payload.get('type')}'"
        )

    return payload


def token_expiry(payload: dict) -> Optional[datetime]:
    exp = payload.get("exp")
    if exp:
        return datetime.fromtimestamp(exp, tz=timezone.utc)
    return None
        
