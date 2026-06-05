from app import create_app, db
from app.models.user import User
from app.models.role import Role, Permission

def seed():
    app = create_app()                    # Make sure this uses correct config
    with app.app_context():
        print("🌱 Seeding database...")

        # === IMPORTANT: Create all tables first ===
        print("Creating database tables...")
        db.create_all()
        print("✅ Tables created successfully!")

        # Now seed the data
        permissions_data = [
            ("read:products",   "products", "read",   "View products"),
            ("write:products",  "products", "write",  "Create/edit products"),
            ("delete:products", "products", "delete", "Delete products"),

            ("read:users",   "users", "read",   "View user list"),
            ("manage:users", "users", "manage", "Activate/deactivate users"),
            ("manage:roles", "roles", "manage", "Assign roles to users"),
        ]

        permissions = {}
        for name, resource, action, desc in permissions_data:
            p = Permission.query.filter_by(name=name).first()
            if not p:
                p = Permission(name=name, resource=resource, action=action, description=desc)
                db.session.add(p)
                print(f" ✓ Added Permission: {name}")
            permissions[name] = p
            
        db.session.flush()

        roles_config = {
            "viewer": {
                "description": "Can only read data",
                "is_default": True,
                "permissions": ["read:products"]
            },
            "editor": {
                "description": "Can read and write products",
                "is_default": False,
                "permissions": ["read:products", "write:products", "read:users"]
            },
            "admin": {
                "description": "Full access to everything",
                "is_default": False,
                "permissions": list(permissions.keys())
            }
        }

        roles = {}
        for role_name, config in roles_config.items():
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(
                    name=role_name,
                    description=config["description"],
                    is_default=config["is_default"]
                )
                db.session.add(role)

            role.permissions = [permissions[p] for p in config["permissions"]]
            roles[role_name] = role
            print(f" ✓ Role: {role_name} ({len(config['permissions'])} permissions)")

        admin = User.query.filter_by(email="admin@example.com").first()
        if not admin:
            admin = User(email="admin@example.com", username="admin")
            admin.set_password("Admin1234!")
            admin.is_verified = True
            admin.roles = [roles["admin"]]
            db.session.add(admin)
            print("  ✓ Admin user: admin@example.com / Admin1234!")

        db.session.commit()
        print("\n✅ Database seeded successfully!")
        print("\nTest Login:")
        print("  Admin → admin@example.com  /  Admin1234!")

if __name__ == "__main__":
    seed()
