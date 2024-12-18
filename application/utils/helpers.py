import logging
import os
import random
import secrets
import string
from datetime import datetime, timedelta, timezone

from flask import render_template
from flask_mail import Message

from application.models.reset_token import ResetToken
from application.models.user import User
from application.utils.extensions import db, mail


def is_password_complex(password):
    if len(password) < 8:
        return False

    has_upper = has_lower = has_digit = has_special = False

    for char in password:
        if char.isdigit():
            has_digit = True
        elif char.isupper():
            has_upper = True
        elif char.islower():
            has_lower = True
        elif char in "@$!%*?&_.":
            has_special = True

    return all([has_upper, has_lower, has_digit, has_special])


def generate_random_password(
    length=12, use_numbers=True, use_symbols=True, avoid_similar=True
):
    similar_chars = "il1Lo0O"
    allowed_symbols = "@$!%*#?&"  # Define a set of allowed symbols.
    characters = (
        string.ascii_letters
        + (string.digits if use_numbers else "")
        + (allowed_symbols if use_symbols else "")
    )

    if avoid_similar:
        characters = "".join(filter(lambda x: x not in similar_chars, characters))

    return "".join(random.choice(characters) for _ in range(length))


def generate_memorable_password(length=4):
    word_list_path = "static/files/words.txt"

    if not os.path.exists(word_list_path):
        print("Word list file not found.")
        return None

    try:
        with open(word_list_path, "r") as file:
            word_list = [line.strip() for line in file if len(line.strip()) > 2]
    except Exception as e:
        print(f"Error reading word list file: {e}")
        return None

    if len(word_list) < length:
        print("Word list does not contain enough words.")
        return None

    words = random.sample(word_list, length)
    return "-".join(words)


def generate_pin_code(length=4):
    return "".join(random.choice(string.digits) for _ in range(length))


def send_password_reset_email(to_email, reset_link):
    subject = "Password Reset Request for Your FlaskKeyring Account"
    current_year = datetime.now().year
    html_body = render_template(
        "password_reset_email_template.html",
        reset_link=reset_link,
        current_year=current_year,
    )
    msg = Message(subject, recipients=[to_email], html=html_body)

    try:
        mail.send(msg)
    except Exception as e:
        print(f"Error sending password reset email: {e}")


def generate_reset_token(user_id):
    # Generate a unique token for password reset
    token = secrets.token_hex(32)  # Generate a 64-character (32-byte) hex token

    # Calculate the token expiration time (e.g., 1 hour from now)
    expiration_time = datetime.now(timezone.utc) + timedelta(hours=1)

    # Create a new ResetToken instance and store it in the database
    reset_token = ResetToken(user_id=user_id, token=token, expires_at=expiration_time)
    db.session.add(reset_token)
    db.session.commit()

    return token


def validate_reset_token(token):
    # Find the ResetToken record in the database
    reset_token = ResetToken.query.filter_by(token=token).first()

    if reset_token:
        # Ensure expires_at is timezone-aware (set to UTC if naive)
        expires_at = reset_token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at > datetime.now(timezone.utc):
            # Token is valid and not expired
            return User.query.get(reset_token.user_id)

    return None


def generate_email_verification_token(user_id):
    # Generate a unique token for email verification
    token = secrets.token_hex(16)  # Generate a 32-character (16-byte) hex token

    # Calculate the token expiration time (e.g., 24 hours from now)
    expiration_time = datetime.now(timezone.utc) + timedelta(hours=24)

    # Retrieve the user and check if it exists
    user = User.query.get(user_id)
    if user is not None:
        # Store the token and expiration time in the User model
        user.email_verification_token = token
        user.email_verification_expires_at = expiration_time
        db.session.commit()
        return token
    else:
        logging.warning(f"User with id {user_id} not found.")
        return None


def send_email_verification_link(to_email, verification_link):
    subject = "Email Verification for Your FlaskKeyring Account"
    current_year = datetime.now().year
    html_body = render_template(
        "email_verification_template.html",
        verification_link=verification_link,
        current_year=current_year,
    )
    msg = Message(subject, recipients=[to_email], html=html_body)

    try:
        mail.send(msg)
    except Exception as e:
        logging.warning(f"Error sending email verification link: {e}")


def generate_iv():
    return os.urandom(12).hex()  # Generates a 12-byte iv in hex


def generate_salt():
    return os.urandom(16).hex()  # Generates a 16-byte salt in hex
