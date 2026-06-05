from flask import Blueprint, request, jsonify, g
from datetime import datetime, timezone
from app import db
from app.models.user import User
from app.models.token import RevokedToken
from app.utils.jwt_handler import generate_tokens, decode_token, extract_token_from_header
from app.middleware.auth_middleware import token_required
from app.utils.email_helper import generate_verification_token, verify_token
from app.utils.email_helper import verification_tokens

import secrets


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    required = ["email", "username", "password"]
    missing = [field for field in required if field not in data]

    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if User.query.filter_by(email=data["email"].lower()).first():
        return jsonify({"error": "Email already registered"}), 409

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already taken"}), 409


    try:
        user = User(
            email=data["email"].lower().strip(),
            username=data["username"].strip(),
        )
        user.set_password(data["password"])
        user.assign_default_role()

        db.session.add(user)
        db.session.commit()

        return jsonify({
            "message": "Account created successfully!",
            "user": user.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Registration failed", "detail": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password required"}), 400

    generic_error = jsonify({"error":"Invalid credentials"}), 401

    user = User.query.filter_by(email=data["email"].lower()).first()


    if not user or not user.is_active:
        return generic_error
    

    if user.is_locked():
        return jsonify({
            "error": "Account temporarily locked",
            "message": "Too many failed attempts. Try again in 30 minutes.",
            "locked_until": user.locked_until.isoformat()
        }), 423

    #if not user.check_password(data["password"]):
    #    user.record_failed_login()
    #    db.session.commit()
    #    return generic_error

    from app.models.login_log import LoginLog

    if not user.check_password(data["password"]):
        user.record_failed_login()
        log = LoginLog(
            email=data["email"],
            ip_address=request.remote_addr,
            success=False,
            reason="Wrong password"
        )
        db.session.add(log)
        db.session.commit()
        return generic_error


    log = LoginLog(
        user_id=user.id,
        email=user.email,
        ip_address=request.remote_addr,
        success=True,
        reason="OK"
    )
    db.session.add(log)
    

    user.reset_failed_logins()
    user.last_login = datetime.now(timezone.utc)
    user.last_login_ip = request.remote_addr
    db.session.commit()
    

    tokens = generate_tokens(
        user_id = user.id,
        roles=[r.name for r in user.roles],
        permissions=user.get_all_permissions()
    )

    return jsonify({
        "message": "Login successful",
        "user": user.to_dict(),
        **tokens
    }), 200


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    auth_header = request.headers.get("Authorization")
    token = extract_token_from_header(auth_header)

    if not token:
        return jsonify({"error": "Refresh token required"}), 401

    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        return jsonify({"error": "Invalid refresh token"}), 401

    if RevokedToken.is_revoked(payload["jti"]):
        return jsonify({"error": "Refresh token has been revoked. Please log in again."}), 401

    user = User.query.get(payload["user_id"])
    if not user or not user.is_active:
        return jsonify({"error": "User not found"}), 401

    tokens = generate_tokens(
        user_id = user.id,
        roles = [r.name for r in user.roles],
        permissions = user.get_all_permissions()
    )

    return jsonify({
        "message": "Tokens refreshed",
        **tokens
    }), 200


@auth_bp.route("/logout", methods=["POST"])
@token_required
def logout():
    from datetime import timedelta
    payload = g.token_payload

    revoked = RevokedToken(
        jti = payload["jti"],
        token_type = "access",
        user_id = g.current_user.id,
        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    )
    db.session.add(revoked)
    db.session.commit()

    return jsonify({"message": "Logged out successfully. Token invalidstion."})

@auth_bp.route("/send-verification", methods=["POST"])
@token_required
def send_verification():
    
    user = g.current_user
    if user.is_verified:
        return jsonify({"message": "Already verified!"}), 200

    token = generate_verification_token(user.id)

    return jsonify({
        "message": "Verification token generated",
        "verify_url": f"http://127.0.0.1:5000/api/auth/verify/{token}",
        "note": "In production this URL would be emailed to the user"
    }), 200

@auth_bp.route("/me", methods=["GET"])
@token_required
def get_current_user():
    return jsonify(g.current_user.to_dict()), 200


@auth_bp.route("/verify/<token>", methods=["GET"])
def verify_email(token):
   
    user_id = verify_token(token)
    if not user_id:
        return jsonify({
            "error": "Invalid or expired verification token"
        }), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.is_verified = True
    db.session.commit()

    return jsonify({
        "message": f"Email verified! Welcome {user.username}."
    }), 200


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    
    data = request.get_json()
    if not data or not data.get("email"):
        return jsonify({"error": "Email required"}), 400

    user = User.query.filter_by(
        email=data["email"].lower()
    ).first()

    if user:
        token = secrets.token_urlsafe(32)
        verification_tokens[f"reset_{token}"] = {
            "user_id": user.id,
            "expires": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        print(f"Reset token for {user.email}: {token}")

    return jsonify({
        "message": "If that email exists, a reset link has been sent.",
        "reset_url": f"http://127.0.0.1:5000/api/auth/reset-password/{token if user else 'example'}"
    }), 200


@auth_bp.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):
    
    data = request.get_json()
    if not data or not data.get("new_password"):
        return jsonify({"error": "new_password required"}), 400

    token_data = verification_tokens.get(f"reset_{token}")
    if not token_data:
        return jsonify({"error": "Invalid or expired reset token"}), 400

    if datetime.now(timezone.utc) > token_data["expires"]:
        del verification_tokens[f"reset_{token}"]
        return jsonify({"error": "Reset token has expired"}), 400

    user = User.query.get(token_data["user_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        user.set_password(data["new_password"])
        db.session.commit()
        del verification_tokens[f"reset_{token}"]
        return jsonify({
            "message": "Password reset successfully! Please log in."
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
