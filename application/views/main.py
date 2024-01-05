from datetime import datetime

from cryptography.fernet import Fernet
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required
from sqlalchemy import func

from application.models.folder import Folder
from application.models.password import Password
from application.utils.extensions import db
from application.utils.helpers import *

main = Blueprint("main", __name__)


@main.route("/")
def index():
    current_year = datetime.now().year
    if current_user.is_authenticated:
        passwords = Password.query.filter_by(user_id=current_user.id).all()
        return render_template(
            "dashboard.html", current_year=current_year, passwords=passwords
        )
    return render_template("index.html")


@main.route("/dashboard")
@login_required
def dashboard():
    current_year = datetime.now().year
    passwords = Password.query.filter_by(user_id=current_user.id).all()
    return render_template(
        "dashboard.html", current_year=current_year, passwords=passwords
    )


@main.route("/view_password/<int:password_id>")
@login_required
def view_password(password_id):
    password_entry = Password.query.get_or_404(password_id)

    fernet_key = get_user_fernet_key(current_user.id)
    if not fernet_key:
        # Handle the case where the Fernet key is not found
        flash("Unable to retrieve encryption key for the password.", "error")
        return redirect(url_for("main.dashboard"))

    cipher_suite = Fernet(fernet_key.encode())
    decrypted_password = cipher_suite.decrypt(password_entry.password.encode()).decode()

    # Pass the decrypted password to the template
    return render_template(
        "view_passwords.html",
        password=password_entry,
        decrypted_password=decrypted_password,
    )


@main.route("/search_password", methods=["POST"])
@login_required
def search_password():
    search_website_raw = request.form.get("search_website")
    if search_website_raw:
        search_website = f"%{search_website_raw.lower()}%"
        password_entries = Password.query.filter(
            Password.user_id == current_user.id,
            func.lower(Password.website).ilike(search_website),
        ).all()

        return render_template("view_passwords.html", passwords=password_entries)
    else:
        return render_template("view_passwords.html", passwords=[])


@main.route("/edit_password/<int:password_id>", methods=["GET", "POST"])
@login_required
def edit_password(password_id):
    current_password = Password.query.get_or_404(password_id)

    fernet_key = get_user_fernet_key(current_user.id)
    if not fernet_key:
        flash("Unable to retrieve encryption key for editing.", "error")
        return redirect(url_for("main.dashboard"))

    cipher_suite = Fernet(fernet_key.encode())

    # Decrypt the current password
    current_decrypted_password = cipher_suite.decrypt(
        current_password.password.encode()
    ).decode()

    if request.method == "POST":
        website = request.form.get("website")
        username = request.form.get("username")
        new_password = request.form.get("password")

        # Update website if provided
        if website:
            current_password.website = website

        # Update username if provided
        if username:
            current_password.username = username

        # Encrypt and update the new password if provided
        if new_password:
            encrypted_password = cipher_suite.encrypt(new_password.encode())
            current_password.password = encrypted_password.decode()

        db.session.commit()

        flash("Account updated successfully.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template(
        "edit_password.html",
        password=current_password,
        decrypted_password=current_decrypted_password,
    )


@main.route("/remove_password/<int:password_id>", methods=["POST"])
@login_required
def remove_password(password_id):
    password = Password.query.get_or_404(password_id)
    db.session.delete(password)
    db.session.commit()
    flash("Account removed successfully.", "success")
    return redirect(url_for("main.dashboard"))


@main.route("/add_password", methods=["GET", "POST"])
@login_required
def add_password():
    if request.method == "POST":
        website = request.form.get("website")
        username = request.form.get("username")
        password = request.form.get("password")

        if not website or not username or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("main.add_password"))

        fernet_key = get_user_fernet_key(current_user.id)
        if not fernet_key:
            flash("Encryption key not found.", "error")
            return redirect(url_for("main.add_password"))

        cipher_suite = Fernet(fernet_key.encode())
        encrypted_password = cipher_suite.encrypt(password.encode())

        new_password = Password(
            user_id=current_user.id,
            website=website,
            username=username,
            password=encrypted_password.decode(),
        )
        db.session.add(new_password)
        db.session.commit()

        flash("Account added successfully.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("dashboard.html")


@main.route("/generate_password", methods=["POST"])
@login_required
def generate_password():
    data = request.get_json()
    password_type = data.get("type")
    length = int(data.get("length"))  # Ensure length is an integer

    if password_type == "random":
        use_numbers = data.get("numbers", True)
        use_symbols = data.get("symbols", True)
        password = generate_random_password(length, use_numbers, use_symbols)
    elif password_type == "memorable":
        # Assuming length here represents the number of words
        password = generate_memorable_password(length)
    elif password_type == "pin":
        password = generate_pin_code(length)
    else:
        return jsonify({"error": "Invalid password type"}), 400

    return jsonify({"password": password})


@main.route("/folders", methods=["GET", "POST"])
@login_required
def folders():
    if request.method == "POST":
        folder_name = request.form.get("folder_name")
        if folder_name:
            new_folder = Folder(user_id=current_user.id, name=folder_name)
            db.session.add(new_folder)
            db.session.commit()
            flash("Folder created successfully.", "success")
        else:
            flash("Folder name is required.", "error")

    user_folders = Folder.query.filter_by(user_id=current_user.id).all()
    return render_template("folders.html", folders=user_folders)
