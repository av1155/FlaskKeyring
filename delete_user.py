import os
import sqlite3

import click

from app import app
from application.models.user import User
from application.utils.extensions import db


def get_database_connection():
    # Check if DATABASE_URL is set in environment or .env
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        print(f"Using database URL: {database_url}")
        return (
            None  # Return None to indicate that SQLAlchemy should handle the connection
        )
    else:
        print("DATABASE_URL not set. Defaulting to local SQLite database.")
        return sqlite3.connect(
            "flaskkeyring.db"
        )  # Connect directly to SQLite if no DATABASE_URL


@click.command()
@click.option(
    "--email",
    prompt="Enter the user's email to delete",
    help="The email of the user to delete, along with all related data.",
)
def delete_user(email):
    # Check for a direct SQLite connection
    conn = get_database_connection()

    if conn:
        # If using direct SQLite connection, perform raw SQL deletion
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if not user:
            print(f"No user found with email: {email}")
            conn.close()
            return

        # Confirm deletion
        confirm = input(
            f"Are you sure you want to delete user '{email}' and all related data? (yes/no): "
        )
        if confirm.lower() != "yes":
            print("Deletion aborted.")
            conn.close()
            return

        # Delete related records manually with raw SQL
        user_id = user[0]
        cursor.execute("DELETE FROM folders WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM passwords WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM reset_tokens WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        print(f"User '{email}' and all related data have been deleted (SQLite).")

    else:
        # If DATABASE_URL is set, use SQLAlchemy with Flask context
        with app.app_context():
            user = User.query.filter_by(email=email).first()
            if not user:
                print(f"No user found with email: {email}")
                return

            confirm = input(
                f"Are you sure you want to delete user '{email}' and all related data? (yes/no): "
            )
            if confirm.lower() != "yes":
                print("Deletion aborted.")
                return

            # Use SQLAlchemy to delete user and related data
            db.session.delete(user)
            db.session.commit()
            print(
                f"User '{email}' and all related data have been deleted (SQLAlchemy)."
            )


if __name__ == "__main__":
    delete_user()
