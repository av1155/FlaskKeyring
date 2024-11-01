from datetime import datetime, timezone

from flask_login import UserMixin

from application.utils.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    email = db.Column(db.String(100), unique=True, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    email_verification_token = db.Column(db.String(100), nullable=True)
    email_verification_expires_at = db.Column(
        db.DateTime, nullable=True, default=lambda: datetime.now(timezone.utc)
    )

    # Add cascading delete to related models
    folders = db.relationship(
        "Folder", backref="user", cascade="all, delete", lazy=True
    )
    passwords = db.relationship(
        "Password", backref="user", cascade="all, delete", lazy=True
    )
    reset_tokens = db.relationship(
        "ResetToken", backref="user", cascade="all, delete", lazy=True
    )

    def __init__(self, email, username, password_hash):
        self.email = email
        self.username = username
        self.password_hash = password_hash
