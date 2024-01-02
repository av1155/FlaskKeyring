import json

from cryptography.fernet import Fernet


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
