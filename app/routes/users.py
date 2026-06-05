from flask import Blueprint, request, jsonify, g
from app import db
from app.models.user import User
from app.middleware.auth_middleware import token_required, require_permission

users_bp = Blueprint("users", __name__)


@users_bp.route("/profile", methods=["GET"])
@token_required
def get_profile():
    
    return jsonify(g.current_user.to_dict()), 200


@users_bp.route("/profile", methods=["PUT"])
@token_required
def update_profile():

    data = request.get_json()
    user = g.current_user

    if "username" in data:
        existing = User.query.filter_by(username = data["username"]).first()
        if existing and existing.id != user.id:
            return jsonify({
                "error": "Username already taken"
            }), 409
        user.username = data["username"].strip()

    db.session.commit()
    return jsonify({
        "message": "Profile updated",
        "user": user.to_dict()
    }), 200


@users_bp.route("/change-password", methods=["POST"])
@token_required
def change_password():
    
    data = request.get_json()
    
    if not data or not data.get("current_password") or not data.get("new_password"):
        return jsonify({
            "error": "current_password and new_password required"
        }), 400

    user = g.current_user

    if not user.check_password(data["current_password"]):
        return jsonify({
            "error": "Current password is incorrect"
        }), 400
    
    try:
        user.set_password(data["new_password"])
        db.session.commit()
        return jsonify({
            "message": "Password changed successfully"
        }), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400


@users_bp.route("/", methods=["GET"])
@token_required
@require_permission("read:users")
def list_users():
    """
    GET /api/users/?page=1&per_page=10&search=john
    List users with pagination and optional search.
    """
    page     = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    search   = request.args.get("search", "", type=str)

    query = User.query

    # Filter by search term if provided
    if search:
        query = query.filter(
            db.or_(
                User.email.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%")
            )
        )

    users_page = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        "users":    [u.to_dict() for u in users_page.items],
        "total":    users_page.total,
        "page":     page,
        "per_page": per_page,
        "pages":    users_page.pages,
        "has_next": users_page.has_next,
        "has_prev": users_page.has_prev,
        "search":   search
    }), 200
    
