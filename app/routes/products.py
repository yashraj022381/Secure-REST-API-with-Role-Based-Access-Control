from flask import Blueprint, request, jsonify, g
from app.middleware.auth_middleware import token_required, require_permission

products_bp = Blueprint("products", __name__)

MOCK_PRODUCTS = [
    {"id": 1, "name": "Widget Pro", "price": 49.99, "stock": 100, "secret_cost": 12.00},
    {"id": 2, "name": "Gadge Plus", "price": 99.99, "stock": 50, "secret_cost": 30.00},
    {"id": 3, "name": "Super Tool", "price": 199.99, "stock": 25, "secret_cost": 80.00},
]


@products_bp.route("/", methods=["GET"])
@token_required
@require_permission("read:products")
def list_products():
    user = g.current_user
    is_admin = user.has_role("admin")

    products = []

    for p in MOCK_PRODUCTS:
        product_data = {k: v for k, v in p.items() if k != "secret_cost"}
        if is_admin:
            product_data["secret_cost"] = p["secret_cost"]
        products.append(product_data)

    return jsonify({"products": products, "count": len(products)}), 200


@products_bp.route("/<int:product_id>", methods=["GET"])
@token_required
@require_permission("read:products")
def get_product(product_id):
    product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    user = g.current_user
    data = {k: v for k, v in product.items() if k != "secret_cost"}
    if user.has_role("admin"):
        data["secret_cost"] = product["secret_cost"]

    return jsonify(data), 200


@products_bp.route("/", methods=["POST"])
@token_required
@require_permission("write:products")
def create_products():
    data = request.get_json()
    if not data or not data.get("name") or not data.get("price"):
        return jsonify({"error": "name and price required"}), 400

    new_product = {
        "id": max(p["id"] for p in MOCK_PRODUCTS) + 1,
        "name": data["name"],
        "price": float(data["price"]),
        "stock": data.get("stock", 0),
        "secret_cost": data.get("secret_cost", 0.0)
    }
    MOCK_PRODUCTS.append(new_product)

    return jsonify({"message": "Product created", "product": new_product}), 201


@products_bp.route("/<int:product_id>", methods=["DELETE"])
@token_required
@require_permission("delete:products")
def delete_product(product_id):
    global MOCK_PRODUCTS
    product = next((p for p in MOCK_PRODUCTS if p["id"] != product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    MOCK_PRODUCTS = [p for p in MOCK_PRODUCTS if p["id"] != product_id]
    return jsonify({"message": f"Productt {product_id} deleted"}), 200
