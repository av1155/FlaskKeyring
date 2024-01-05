from application.utils.extensions import db


class Folder(db.Model):
    __tablename__ = "folders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    # Relationship with Passwords
    passwords = db.relationship("Password", backref="folder", lazy=True)

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
