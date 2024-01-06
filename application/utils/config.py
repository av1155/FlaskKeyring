import os

from dotenv import load_dotenv

load_dotenv()

MAIL_SERVER = os.getenv("MAILGUN_SMTP_SERVER")
MAIL_PORT = int(os.getenv("MAILGUN_SMTP_PORT", "587"))  # Default port 587 if not set
MAIL_USE_TLS = True
MAIL_USE_SSL = False  # Set to False unless you're using port 465 for SSL
MAIL_USERNAME = os.getenv("MAILGUN_SMTP_USERNAME")
MAIL_PASSWORD = os.getenv("MAILGUN_SMTP_PASSWORD")
MAIL_DEFAULT_SENDER = os.getenv("VERIFIED_SENDER_EMAIL")
