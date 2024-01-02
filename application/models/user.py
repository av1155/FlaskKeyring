from flask_login import UserMixin

from application.utils.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __init__(self, email, username, password_hash):
        self.email = email
        self.username = username
        self.password_hash = password_hash
