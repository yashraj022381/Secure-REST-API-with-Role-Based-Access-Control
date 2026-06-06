from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from flask_migrate import upgrade, init
import os

app = create_app()

def deploy():
    """Run database migrations and seed automatically on startup."""
    with app.app_context():
        # Run all pending migrations
        try:
            upgrade()
            print("✅ Database migrations applied!")
        except Exception as e:
            print(f"Migration note: {e}")

        # Seed initial data if needed
        try:
            from app.models.role import Role, Permission
            from app.models.user import User

            # Only seed if no roles exist yet
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
                    p = Permission(
                        name=name,
                        resource=resource,
                        action=action,
                        description=desc
                    )
                    db.session.add(p)
                    permissions[name] = p

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
                    role = Role(
                        name=role_name,
                        description=config["description"],
                        is_default=config["is_default"]
                    )
                    role.permissions = [
                        permissions[p]
                        for p in config["permissions"]
                    ]
                    db.session.add(role)

                # Create admin user
                admin_role = Role.query.filter_by(
                    name="admin"
                ).first()

                if not User.query.filter_by(
                    email="admin@example.com"
                ).first():
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
                print("✅ Database seeded successfully!")
                print("   Admin: admin@example.com / Admin1234!")
            else:
                print("✅ Database already seeded — skipping.")

        except Exception as e:
            print(f"Seed error: {e}")
            db.session.rollback()


# Run on startup
deploy()


if __name__ == "__main__":
   # with app.app_context():
    #    db.create_all()
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
