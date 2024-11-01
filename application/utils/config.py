import os

from dotenv import load_dotenv

load_dotenv()

MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))  # Default to 587 for TLS
MAIL_USE_TLS = True
MAIL_USE_SSL = False  # Set to True only if using port 465 for SSL
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = os.getenv("VERIFIED_SENDER_EMAIL")
