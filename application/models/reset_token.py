from datetime import datetime, timezone

from application.utils.extensions import db


class ResetToken(db.Model):
    __tablename__ = "reset_tokens"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    expires_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(timezone.utc)
    )

    def __init__(self, user_id, token, expires_at):
        self.user_id = user_id
        self.token = token
        self.expires_at = expires_at
