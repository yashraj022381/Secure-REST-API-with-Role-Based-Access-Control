from app import db
from datetime import datetime, timezone


class LoginLog(db.Model):
    __tablename__ = "login_logs"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )
    email      = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(45),  nullable=True)
    success    = db.Column(db.Boolean,     nullable=False)
    reason     = db.Column(db.String(100), nullable=True)
    timestamp  = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id":         self.id,
            "email":      self.email,
            "ip_address": self.ip_address,
            "success":    self.success,
            "reason":     self.reason,
            "timestamp":  self.timestamp.isoformat()
        }
