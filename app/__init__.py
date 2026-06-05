from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config


db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    

    app = Flask(__name__)
    app.config.from_object(config_class)
    

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.admin import admin_bp
    from app.routes.products import products_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(products_bp, url_prefix="/api/products")

    from app.models.user import User
    from app.models.role import Role, Permission
    from app.models.token import RevokedToken
    #from app.models.login_log import LoginLog
    

    @app.route("/api/health")
    def health_check():
        from datetime import datetime, timezone
        from flask import jsonify
        return jsonify({
            "status":    "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version":   "1.0.0",
            "service":   "Secure REST API with RBAC"
        }), 200

    return app
