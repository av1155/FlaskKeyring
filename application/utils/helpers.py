import json
import os
import random
import secrets
import string

from cryptography.fernet import Fernet
from flask_mail import Message

from application.models.reset_token import ResetToken
from application.models.user import User
from application.utils.extensions import db, mail


def generate_and_store_fernet_key(user_id):
    # Generate a new Fernet key
    fernet_key = Fernet.generate_key().decode()
    # Store the key in a file or a secure location
    # Here we use a JSON file for simplicity
    try:
        with open("fernet_keys.json", "r") as file:
            keys = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        keys = {}

    keys[str(user_id)] = fernet_key
    with open("fernet_keys.json", "w") as file:
        json.dump(keys, file)


def get_user_fernet_key(user_id):
    try:
        with open("fernet_keys.json", "r") as file:
            keys = json.load(file)
            return keys.get(str(user_id))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


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

    return "".join(random.choice(characters) for i in range(length))


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
    return "".join(random.choice(string.digits) for i in range(length))


def send_password_reset_email(to_email, reset_link):
    subject = "Password Reset Request for Your FlaskKeyring Account"
    body = f"Click the following link to reset your password: {reset_link}"

    msg = Message(subject, recipients=[to_email])
    msg.body = body

    try:
        mail.send(msg)
    except Exception as e:
        print(f"Error sending password reset email: {e}")


from datetime import datetime, timedelta


def generate_reset_token(user_id):
    # Generate a unique token for password reset
    token = secrets.token_hex(32)  # Generate a 64-character (32-byte) hex token

    # Calculate the token expiration time (e.g., 1 hour from now)
    expiration_time = datetime.utcnow() + timedelta(hours=1)

    # Create a new ResetToken instance and store it in the database
    reset_token = ResetToken(user_id=user_id, token=token, expires_at=expiration_time)
    db.session.add(reset_token)
    db.session.commit()

    return token


def validate_reset_token(token):
    # Find the ResetToken record in the database
    reset_token = ResetToken.query.filter_by(token=token).first()

    if reset_token and reset_token.expires_at > datetime.utcnow():
        # Token is valid and not expired
        return User.query.get(reset_token.user_id)

    return None
