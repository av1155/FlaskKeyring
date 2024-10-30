from application.utils.extensions import db


class Password(db.Model):
    __tablename__ = "passwords"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    website = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.Text, nullable=False)
    iv = db.Column(db.String(255), nullable=False)  # New IV field
    salt = db.Column(db.String(255), nullable=False)  # New salt field
    folder_id = db.Column(db.Integer, db.ForeignKey("folders.id"), nullable=True)

    def __init__(self, user_id, website, username, password, iv, salt, folder_id=None):
        self.user_id = user_id
        self.website = website
        self.username = username
        self.password = password
        self.iv = iv
        self.salt = salt
        self.folder_id = folder_id
