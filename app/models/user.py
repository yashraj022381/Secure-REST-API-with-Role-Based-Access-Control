import bcrypt
from datetime import datetime, timezone
from app import db
from app.models.role import user_roles, Role

class User(db.Model):
    
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)

    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    last_login_ip = db.Column(db.String(45), nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    roles = db.relationship("Role", secondary=user_roles, lazy="subquery")

    def set_password(self, plain_password: str) -> None:
        if len(plain_password) < 8:
            raise ValueError("Password must be at least 8 characters")

        password_bytes = plain_password.encode("utf-8")
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        self.password_hash = hashed.decode("utf-8")

    def check_password(self, plain_password: str) -> bool:
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                self.password_hash.encode("utf-8")
            )
        except ValueError:
            return False

    def is_locked(self) -> bool:
        if self.locked_until is None:
            return False
        return datetime.now(timezone.utc) < self.locked_until.replace(tzinfo=timezone.utc)

    def record_failed_login(self) -> None:
        from datetime import timedelta
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)

    def reset_failed_logins(self) -> None:
        self.failed_login_attempts = 0
        self.locked_until = None

    def has_role(self, role_name: str) -> bool:
        return any(r.name == role_name for r in self.roles)

    def has_permission(self, permission_name: str) -> bool:
        return any(role.has_permissions(permission_name) for role in self.roles)

    def get_all_permissions(self) -> list:
        perms = set()
        for role in self.roles:
            for perm in role.permissions:
                perms.add(perm.name)
        return list(perms)

    def assign_default_role(self) -> None:
        default_role = Role.query.filter_by(is_default=True).first()
        if default_role and default_role not in self.roles:
            self.roles.append(default_role)

    def to_dict(self, include_roles=True) -> dict:
        data = {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
        if include_roles:
            data["roles"] = [r.name for r in self.roles]
            data["permissions"] = self.get_all_permissions()
        return data

    def __repr__(self):
        return f"<User {self.username}>"
    
        
        
        
