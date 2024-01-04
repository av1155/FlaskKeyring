import os

from dotenv import load_dotenv

load_dotenv()

print("DATABASE_URL:", os.getenv("DATABASE_URL"))

MAIL_SERVER = "mail.smtp2go.com"  # SMTP2GO SMTP server
MAIL_PORT = 2525  # SMTP2GO port for TLS
MAIL_USE_TLS = True  # Use TLS
MAIL_USERNAME = os.getenv("SMTP2GO_USERNAME")
MAIL_PASSWORD = os.getenv("SMTP2GO_PASSWORD")
MAIL_DEFAULT_SENDER = os.getenv("VERIFIED_SENDER_EMAIL")
