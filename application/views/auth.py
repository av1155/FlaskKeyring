from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from application.models.user import User
from application.utils.extensions import db
from application.utils.helpers import (generate_and_store_fernet_key,
                                       is_password_complex)

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if the password is complex enough
        if not is_password_complex(password):
            flash(
                "Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a digit, and a special character.",
                "error",
            )
            return redirect(url_for("auth.register"))

        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists.", "error")
            return redirect(url_for("auth.register"))

        new_user = User(
            username=username, password_hash=generate_password_hash(password)
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
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash(
                "Invalid username or password", "error"
            )  # 'error' is a category, can be used for styling
            return redirect(url_for("auth.login"))  # Redirect back to the login page

        login_user(user)
        return redirect(url_for("main.index"))

    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
