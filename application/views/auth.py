import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from validate_email import validate_email
from werkzeug.security import check_password_hash, generate_password_hash

from application.models.user import User
from application.utils.extensions import db
from application.utils.helpers import *

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not username or not password:
            flash("Email, username, and password are required.", "error")
            logging.warning("Failed registration attempt due to missing fields")

            return redirect(url_for("auth.register"))

        # Validate email format using validate_email
        if not validate_email(email):
            flash("Invalid email format.", "error")
            logging.warning("Failed registration attempt due to invalid email format")

            return redirect(url_for("auth.register"))

        if not is_password_complex(password):
            flash(
                "Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a digit, and a special character.",
                "error",
            )
            logging.warning(
                "Failed registration attempt due to password complexity requirements"
            )

            return redirect(url_for("auth.register"))

        if "@" in username:
            flash("Username cannot contain @", "error")
            logging.warning(
                "Failed registration attempt due to invalid character in username"
            )

            return redirect(url_for("auth.register"))

        # Check for existing users in a case-insensitive manner
        email_exists = User.query.filter(func.lower(User.email) == email).first()
        username_exists = User.query.filter(
            func.lower(User.username) == func.lower(username)
        ).first()

        if email_exists:
            flash("Email already exists.", "error")
            logging.warning(
                f"Failed registration attempt due to existing email: {email}"
            )

            return redirect(url_for("auth.register"))

        if username_exists:
            flash("Username already exists.", "error")
            logging.warning(
                f"Failed registration attempt due to existing username: {username}"
            )

            return redirect(url_for("auth.register"))

        try:
            # Attempt to create a new user
            new_user = User(
                email=email,
                username=username,
                password_hash=generate_password_hash(password),
            )
            db.session.add(new_user)
            db.session.commit()
            logging.info(f"New user registered: {username}")

            # Assuming this function generates and stores a Fernet key for the new user
            generate_and_store_fernet_key(new_user.id)

            flash("Registration successful. Please sign in.", "success")

            return redirect(url_for("auth.login"))

        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error("Error occurred while creating a user account", exc_info=e)
            flash(
                "An error occurred while creating the account. Please try again.",
                "error",
            )

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_email = request.form.get("username_email")
        password = request.form.get("password")

        if not username_email or not password:
            flash("Please enter both email and password", "error")
            return redirect(url_for("auth.login"))

        # Query for user by email or username
        user = User.query.filter(
            (User.email == username_email) | (User.username == username_email)
        ).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password", "error")
            logging.warning(f"Failed login attempt for: {username_email}")

            return redirect(url_for("auth.login"))

        login_user(user)
        logging.info(f"User logged in: {username_email}")

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
            logging.info(f"Password changed for user: {current_user.username}")

            return redirect(url_for("main.dashboard"))

        else:
            flash("User not found.", "error")
            return redirect(url_for("auth.change_password"))

    return render_template("change_password.html")


@auth.route("/logout")
@login_required
def logout():
    logging.info(f"User logged out: {current_user.username}")
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")

        # Check if the email exists in the database
        user = User.query.filter_by(email=email).first()

        if user:
            # Generate a unique token for password reset
            reset_token = generate_reset_token(user.id)

            # Create a password reset link
            reset_link = url_for(
                "auth.reset_password", token=reset_token, _external=True
            )

            # Send the password reset email
            send_password_reset_email(user.email, reset_link)

            flash("Password reset email sent. Check your inbox.", "success")
            logging.info(f"Password reset requested for: {email}")

            return redirect(url_for("auth.login"))
        else:
            flash("Email not found. Please try again.", "error")
            logging.warning(f"Password reset requested for non-existing email: {email}")

    return render_template("forgot_password.html")


@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    # Validate the reset token
    user = validate_reset_token(token)

    if not user:
        flash("Invalid or expired token. Please request a new password reset.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("new_password")

        if new_password is None:
            flash("New password is required.", "error")
            return render_template("reset_password.html", token=token)

        # Check if the new password is complex enough
        if not is_password_complex(new_password):
            flash(
                "Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a digit, and a special character.",
                "error",
            )
            return render_template("reset_password.html", token=token)

        # Update the user's password in the database
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        flash(
            "Password reset successful. You can now log in with your new password.",
            "success",
        )
        logging.info(f"Password reset for user ID: {user.id}")

        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", token=token)
