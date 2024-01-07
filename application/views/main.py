from datetime import datetime

from cryptography.fernet import Fernet
from flask import (
    Blueprint,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
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
        folders = Folder.query.filter_by(user_id=current_user.id).all()
        return render_template(
            "dashboard.html",
            current_year=current_year,
            passwords=passwords,
            folders=folders,
        )
    else:
        return render_template("index.html", current_year=current_year)


@main.route("/dashboard")
@login_required
def dashboard():
    current_year = datetime.now().year
    passwords = Password.query.filter_by(user_id=current_user.id).all()
    folders = Folder.query.filter_by(user_id=current_user.id).all()
    return render_template(
        "dashboard.html",
        current_year=current_year,
        passwords=passwords,
        folders=folders,
    )


@main.route("/view_password/<int:password_id>")
@login_required
def view_password(password_id):
    password_entry = Password.query.get_or_404(password_id)

    fernet_key = get_user_fernet_key(current_user.id)
    if not fernet_key:
        flash("Unable to retrieve encryption key for the password.", "error")
        return redirect(url_for("main.dashboard"))

    cipher_suite = Fernet(fernet_key.encode())
    decrypted_password = cipher_suite.decrypt(password_entry.password.encode()).decode()

    # Get the folder name
    folder_name = None
    if password_entry.folder_id:
        folder = Folder.query.get(password_entry.folder_id)
        if folder:
            folder_name = folder.name

    return render_template(
        "view_passwords.html",
        password=password_entry,
        decrypted_password=decrypted_password,
        folder_name=folder_name,
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
    folders = Folder.query.filter_by(user_id=current_user.id).all()

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
        folder_id = request.form.get("folder_id")

        if folder_id:
            current_password.folder_id = int(folder_id)
        else:
            current_password.folder_id = None

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

    # Pre-select the current folder in the dropdown
    selected_folder_id = (
        current_password.folder_id if current_password.folder_id else None
    )

    return render_template(
        "edit_password.html",
        password=current_password,
        decrypted_password=current_decrypted_password,
        folders=folders,
        selected_folder_id=selected_folder_id,
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
    folders = Folder.query.filter_by(user_id=current_user.id).all()

    if request.method == "POST":
        website = request.form.get("website")
        username = request.form.get("username")
        password = request.form.get("password")
        folder_id = request.form.get("folder_id")

        if folder_id:
            folder_id = int(folder_id)
        else:
            folder_id = None

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
            folder_id=folder_id,  # Add folder_id
        )
        db.session.add(new_password)
        db.session.commit()

        flash("Account added successfully.", "success")
        return redirect(url_for("main.dashboard"))

    # Ensure a default "Main" folder exists and is selected
    main_folder = Folder.query.filter_by(user_id=current_user.id, name="Main").first()
    if not main_folder:
        main_folder = Folder(name="Main", user_id=current_user.id)
        db.session.add(main_folder)
        db.session.commit()

    return render_template("dashboard.html", folders=folders, main_folder=main_folder)


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


# FOLDERS
@main.route("/create_folder", methods=["GET", "POST"])
@login_required
def create_folder():
    if request.method == "POST":
        folder_name = request.form.get("folder_name")
        if folder_name:
            new_folder = Folder(user_id=current_user.id, name=folder_name)
            db.session.add(new_folder)
            db.session.commit()
            flash("Folder created successfully!", "success")
        else:
            flash("Folder name is required", "error")
        return redirect(url_for("main.dashboard"))
    return render_template("create_folder.html")


@main.route("/update_folder/<int:folder_id>", methods=["GET", "POST"])
@login_required
def update_folder(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    if folder.user_id != current_user.id:
        abort(403)
    if request.method == "POST":
        folder.name = request.form.get("folder_name")
        db.session.commit()
        flash("Folder updated successfully!", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("update_folder.html", folder=folder)


@main.route("/delete_folder/<int:folder_id>", methods=["POST"])
@login_required
def delete_folder(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    if folder.user_id != current_user.id:
        abort(403)
    db.session.delete(folder)
    db.session.commit()
    flash("Folder deleted successfully!", "success")
    return redirect(url_for("main.dashboard"))


@main.route("/folder/<int:folder_id>")
@login_required
def view_folder(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    if folder.user_id != current_user.id:
        abort(403)
    passwords = Password.query.filter_by(folder_id=folder.id).all()
    return render_template("view_folder.html", folder=folder, passwords=passwords)


@main.route("/list_folders")
@login_required
def list_folders():
    folders = Folder.query.filter_by(user_id=current_user.id).all()
    return render_template("list_folders.html", folders=folders)
