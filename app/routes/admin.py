from flask import Blueprint, request, jsonify, g
from app import db
from app.models.user import User
from app.models.role import Role, Permission
from app.models.token import RevokedToken
from app.middleware.auth_middleware import token_required, require_role, require_permission

admin_bp = Blueprint("admin", __name__)



@admin_bp.route("/users", methods=["GET"])
@token_required
@require_role("admin")
def list_all_users():
    users = User.query.all()
    return jsonify({
        "users": [u.to_dict() for u in users],
        "count": len(users)
    }), 200



@admin_bp.route("/users/<int:user_id>/roles", methods=["POST"])
@token_required
@require_permission("manage:roles")
def assign_role(user_id):
    
    data = request.get_json()
    role_name = data.get("role")

    user = User.query.get_or_404(user_id)
    role = Role.query.filter_by(name=role_name).first()

    if not role:
        return jsonify({
            "error": f"Role '{role_name}' not found"
        }), 404

    if role not in user.roles:
        user.roles.append(role)
        db.session.commit()

    return jsonify({
        "message": f"Role '{role_name}' assigned to {user.username}",
        "user": user.to_dict()
    }), 200



@admin_bp.route("/users/<int:user_id>/deactivate", methods=["POST"])
@token_required
@require_permission("manage:users")
def deactivate_user(user_id):
    
    if user_id == g.current_user_user.id:
        return jsonify({
            "error": "Cannot deactivate yourself"
        }), 400

    user = User.query.get_or_404(user_id)
    user.is_active = False
    db.session.commit()

    return jsonify({
        "message": f"User {user.username} deactivated"
    }), 200


@admin_bp.route("/users/<int:user_id>/activate", methods=["POST"])
@token_required
@require_permission("manage:users")
def activate_user(user_id):
    """
    POST /api/admin/users/<id>/activate
    Re-enable a previously deactivated account.
    """
    user = User.query.get_or_404(user_id)

    if user.is_active:
        return jsonify({
            "message": f"{user.username} is already active"
        }), 200

    user.is_active = True
    db.session.commit()

    return jsonify({
        "message": f"User {user.username} reactivated successfully",
        "user":    user.to_dict()
    }), 200


@admin_bp.route("/roles", methods=["GET"])
@token_required
@require_role("admin")
def list_roles():
    
    roles = Role.query.all()
    return jsonify({
        "roles": [r.to_dict() for r in roles]
    }), 200


@admin_bp.route("/roles", methods=["POST"])
@token_required
@require_permission("manage:roles")
def create_table():

    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({
            "error": "Role name required"
        }), 400

    if Role.query.filter_by(name = data["name"]).first():
        return jsonify({
            "error": "Role already exists"
        }), 409

    role = Role(
        name = data["name"],
        description = data.get("description", ""),
        is_default = data.get("is_default", False)
    )
    
    db.session.add(role)
    db.session.commit()

    return jsonify({
        "message": "Role created", "role": role.to_dict()
    }), 201



@admin_bp.route("/cleanup-tokens", methods=["POST"])
@token_required
@require_role("admin")
def clean_tokens():

    count = RevokedToken.cleanup_expired()
    return jsonify({
        "message": f"Removed {count} expired tokens form blacklist"
    }), 200


from app.models.login_log import LoginLog

@admin_bp.route("/login-logs", methods=["GET"])
@token_required
@require_role("admin")
def get_login_logs():
    """
    GET /api/admin/login-logs?limit=50
    View recent login attempts.
    """
    limit = min(request.args.get("limit", 50, type=int), 200)
    logs  = LoginLog.query.order_by(
        LoginLog.timestamp.desc()
    ).limit(limit).all()

    return jsonify({
        "logs":  [l.to_dict() for l in logs],
        "count": len(logs)
    }), 200
