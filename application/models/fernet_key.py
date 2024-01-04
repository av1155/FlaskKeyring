from application.utils.extensions import db


class FernetKey(db.Model):
    __tablename__ = "fernet_keys"
    user_id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), nullable=False)

    def __init__(self, user_id, key):
        self.user_id = user_id
        self.key = key
