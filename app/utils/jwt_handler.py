import jwt
import uuid
from datetime import datetime, timezone, timedelta
from flask import current_app
from typing import Optional


def generate_tokens(user_id: int, roles: list, permissions: list) -> dict:
    now = datetime.now(timezone.utc)

    access_payload = {
        "user_id":     user_id,
        "roles":       roles,
        "permissions": permissions,
        "type":        "access",
        "jti":         str(uuid.uuid4()),
        "iat":         now,
        "exp":         now + current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
    }

    refresh_payload = {
        "user_id": user_id,
        "type":    "refresh",
        "jti":     str(uuid.uuid4()),
        "iat":     now,
        "exp":     now + current_app.config["JWT_REFRESH_TOKEN_EXPIRES"],
    }

    secret = current_app.config["SECRET_KEY"]

    access_token  = jwt.encode(access_payload,  secret, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, secret, algorithm="HS256")

    return {
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "token_type":    "Bearer",
        "expires_in":    int(current_app.config["JWT_ACCESS_TOKEN_EXPIRES"].total_seconds()),
    }


def decode_token(token: str) -> Optional[dict]:
    try:
        # Clean token — remove any quotes or spaces accidentally included
        token = token.strip().strip('"').strip("'")

        payload = jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"],
            options={"require": ["exp", "iat", "jti", "user_id"]}
        )
        return payload

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None

    except Exception:
        return None


def extract_token_from_header(auth_header: Optional[str]) -> Optional[str]:
    if not auth_header:
        return None

    # Remove any extra quotes
    auth_header = auth_header.strip().strip('"').strip("'")

    parts = auth_header.split(" ")

    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    # Clean the token part too
    token = parts[1].strip().strip('"').strip("'")
    return token
