import os
import sys


sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.user import User, Role

ROLES = [
    {
        "name": "admin",
        "description": "Full system access",
        "permissions": "*",
    },
    {
        "name": "editor",
        "description": "Can create and edit content",
        "permissions": "read:users, write:posts, edit:posts, read:posts",
    },
    {
        "name": "viewer",
        "description": "Read-only access",
        "permissions": "read:posts, read:users",
    },
]


DEFAULT_ADMIN = {
    "email": os.environ.get("ADMIN_EMAIL", "admin@example.com"),
    "username": "admin",
    "password": os.environ.get("ADMIN_PASSWORD", "Admin@SecurePass1!"),
}


def seed_roles(app):
    print("🌱 Seeding roles...")
    created = 0

    with app.app_content():
        for role_data in ROLES:
            existing = Role.query.filter_by(name=role_data["name"]).first()
            if not existing:
                role = Role(
                    name=role_data["name"],
                    description=role_data["description"],
                    permissions=role_data["permissions"],
                )
                db.session.add(role)
                print(f" ✓  Created role: {role_data['name']}")
                created += 1

            else:
                print(f"   . Role already exists: {role_data['name']}")

        db.session.commit()
        print(f" Roles created: {created}")


def seed_admin(app):
    print("\n🌱 Seeding admin user...")

    with app.app_context():
        admin_role = Role.query.filter_by(name="admin").first()
        if not admin_role:
            print("  ❌ Admin role not found! Run seed_roles first.")
            return

        existing_admin = User.query.filter(
            User.roles.contains(admin_role)
            ).first()

        if existing_admin:
            print(f"   . Admin user already exists: {existing_admin.email}")
            return

        admin = User(
            email=DEFAULT_ADMIN["email"],
            username=DEFAULT_ADMIN["username"],
            is_active=True,
            is_verified=True,
        )
        admin.set_password(DEFAULT_ADMIN["password"])
        admin.roles.append(admin_role)

        db.session.add(admin)
        db.session.commit()

        print(f"  ✓ Created admin user: {admin.email}")
        print(f"  ⚠️  Default password: {DEFAULT_ADMIN['password']}")
        print("  ⚠️  CHANGE THIS PASSWORD IMMEDIATELY IN PRODUCTION!")

if __name__ == "__main__":
    
    app = create_app("development")

    with app.app_context():
        print("🗄  Creating database tables...")
        db.create_all()
        print("  ✓ Tables created\n")

        seed_roles(app)
        seed_admin(app)

            
        print("\n✅ Database seeded successfully!")
        print("\nYou can now log in at POST /api/auth/login with:")
        print(f"  Email:    {DEFAULT_ADMIN['email']}")
        print(f"  Password: {DEFAULT_ADMIN['password']}")
            
