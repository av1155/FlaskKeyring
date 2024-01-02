from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from application.models.user import User
from application.utils.extensions import db
from application.utils.helpers import (generate_and_store_fernet_key,
                                       is_password_complex)

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        if not email or not username or not password:
            flash("Email, username, and password are required.", "error")
            return redirect(url_for("auth.register"))

        if not is_password_complex(password):
            flash(
                "Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a digit, and a special character.",
                "error",
            )
            return redirect(url_for("auth.register"))

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists or username_exists:
            flash("Email or username already exists.", "error")
            return redirect(url_for("auth.register"))

        new_user = User(
            email=email,
            username=username,
            password_hash=generate_password_hash(password),
        )
        db.session.add(new_user)
        db.session.commit()

        generate_and_store_fernet_key(new_user.id)

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Please enter both email and password", "error")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password", "error")
            return redirect(url_for("auth.login"))

        login_user(user)
        return redirect(url_for("main.index"))

    return render_template("login.html")


@auth.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        email = request.form.get("email")
        new_password = request.form.get("new_password")

        if not email or not new_password:
            flash("Email and new password are required.", "error")
            return redirect(url_for("auth.register"))

        if email != current_user.email:
            flash("Unauthorized operation.", "error")
            return redirect(url_for("auth.change_password"))

        if not is_password_complex(new_password):
            flash(
                "Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a digit, and a special character.",
                "error",
            )
            return redirect(url_for("auth.change_password"))

        user = current_user

        if user:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash("Password changed successfully.", "success")
            return redirect(url_for("main.dashboard"))

        else:
            flash("User not found.", "error")
            return redirect(url_for("auth.change_password"))

    return render_template("change_password.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
