from functools import wraps
from flask import request, jsonify, g
from app.models.user import User
from app.models.token import RevokedToken
from app.utils.jwt_handler import decode_token, extract_token_from_header


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "error": "Missing token",
                "message": "Include Authorization: Bearer <token> in headers"
            }), 401

        token = extract_token_from_header(auth_header)

        if not token:
            return jsonify({
                "error": "Invalid token format",
                "message": "Use: Authorization: Bearer <your_token>"
            }), 401

        payload = decode_token(token)

        if not payload:
            return jsonify({
                "error": "Invalid or expired token",
                "message": "Your session has expired. Please log in again."
            }), 401

        if payload.get("type") != "access":
            return jsonify({
                "error": "Wrong token type",
                "message": "Use an access token not a refresh token."
            }), 401

        if RevokedToken.is_revoked(payload["jti"]):
            return jsonify({
                "error": "Token revoked",
                "message": "This token has been invalidated. Please log in again."
            }), 401

        user = User.query.get(payload["user_id"])
        if not user or not user.is_active:
            return jsonify({
                "error": "User not found or inactive"
            }), 401

        g.current_user  = user
        g.token_payload = payload

        return f(*args, **kwargs)
    return decorated


def require_permission(permission_name: str):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(g, "current_user", None)
            if not user:
                return jsonify({"error": "Not authenticated"}), 401
            if not user.has_permission(permission_name):
                return jsonify({
                    "error": "Forbidden",
                    "message": f"You need '{permission_name}' permission.",
                    "your_permissions": user.get_all_permissions()
                }), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


def require_role(role_name: str):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(g, "current_user", None)
            if not user:
                return jsonify({"error": "Not authenticated"}), 401
            if not user.has_role(role_name):
                return jsonify({
                    "error": "Forbidden",
                    "message": f"You need '{role_name}' role.",
                    "your_roles": [r.name for r in user.roles]
                }), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
