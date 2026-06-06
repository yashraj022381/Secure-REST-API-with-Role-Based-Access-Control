from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from flask_migrate import upgrade, init, migrate
import os

app = create_app()


def deploy():
    """Run database setup automatically on startup."""
    with app.app_context():

        # Step 1 — Create all tables directly (simpler than migrations)
        try:
            db.create_all()
            print("✅ Database tables created!")
        except Exception as e:
            print(f"Table creation note: {e}")

        # Step 2 — Seed data if empty
        try:
            from app.models.role import Role, Permission
            from app.models.user import User

            if Role.query.count() == 0:
                print("🌱 Seeding database...")

                # Create permissions
                permissions_data = [
                    ("read:products",   "products", "read",   "View products"),
                    ("write:products",  "products", "write",  "Create/edit products"),
                    ("delete:products", "products", "delete", "Delete products"),
                    ("read:users",      "users",    "read",   "View user list"),
                    ("manage:users",    "users",    "manage", "Manage users"),
                    ("manage:roles",    "roles",    "manage", "Manage roles"),
                ]

                permissions = {}
                for name, resource, action, desc in permissions_data:
                    existing = Permission.query.filter_by(
                        name=name
                    ).first()
                    if not existing:
                        p = Permission(
                            name=name,
                            resource=resource,
                            action=action,
                            description=desc
                        )
                        db.session.add(p)
                        permissions[name] = p
                    else:
                        permissions[name] = existing

                db.session.flush()

                # Create roles
                roles_config = {
                    "viewer": {
                        "description": "Can only read data",
                        "is_default": True,
                        "permissions": ["read:products"]
                    },
                    "editor": {
                        "description": "Can read and write",
                        "is_default": False,
                        "permissions": [
                            "read:products",
                            "write:products",
                            "read:users"
                        ]
                    },
                    "admin": {
                        "description": "Full access",
                        "is_default": False,
                        "permissions": list(permissions.keys())
                    }
                }

                for role_name, config in roles_config.items():
                    role = Role.query.filter_by(
                        name=role_name
                    ).first()
                    if not role:
                        role = Role(
                            name=role_name,
                            description=config["description"],
                            is_default=config["is_default"]
                        )
                        role.permissions = [
                            permissions[p]
                            for p in config["permissions"]
                            if p in permissions
                        ]
                        db.session.add(role)

                # Create admin user
                if not User.query.filter_by(
                    email="admin@example.com"
                ).first():
                    admin_role = Role.query.filter_by(
                        name="admin"
                    ).first()
                    admin = User(
                        email="admin@example.com",
                        username="admin"
                    )
                    admin.set_password("Admin1234!")
                    admin.is_verified = True
                    if admin_role:
                        admin.roles = [admin_role]
                    db.session.add(admin)

                db.session.commit()
                print("✅ Database seeded!")
                print("   Admin: admin@example.com / Admin1234!")
            else:
                print("✅ Database already seeded.")

        except Exception as e:
            print(f"Seed error: {e}")
            db.session.rollback()


# Run setup on startup
deploy()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
