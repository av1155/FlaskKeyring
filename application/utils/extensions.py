import os

from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

# Modify DATABASE_URL for SQLAlchemy 1.4+ compatibility
database_url = os.getenv("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
    os.environ["DATABASE_URL"] = database_url

db = SQLAlchemy()
mail = Mail()
