from application.utils.extensions import db


class Password(db.Model):
    __tablename__ = "passwords"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    website = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __init__(self, user_id, website, username, password):
        self.user_id = user_id
        self.website = website
        self.username = username
        self.password = password
