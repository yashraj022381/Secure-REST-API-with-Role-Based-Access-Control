from app import db
from datetime import datetime, timezone

class RevokedToken(db.Model):
    
    __tablename__ = "revoked_tokens"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), unique=True, nullable=False, index=True)
    token_type = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    revoked_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)
    

    @classmethod
    def is_revoked(cls, jti: str) -> bool:
        
        return cls.query.filter_by(jti=jti).first() is not None
    

    @classmethod
    def cleanup_expired(cls) -> int:
        
        now = datetime.now(timezone.utc)
        expired = cls.query.filter(cls.expires_at < now).all()
        count = len(expired)
        for token in expired:
            db.session.delete(token)
        db.session.commit()
        return count
