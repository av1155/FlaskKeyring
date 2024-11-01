from datetime import datetime, timedelta, timezone

from application.models.user import User
from application.utils.extensions import db


def delete_unverified_users():
    # Define a cutoff date for deletion (e.g., 7 days since registration)
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
    print(f"Cutoff date: {cutoff_date}")

    # Query for unverified users where the email_verification_expires_at is NOT NULL and has passed
    unverified_users = User.query.filter(
        User.email_verified == False,
        User.email_verification_expires_at.isnot(None),
        User.email_verification_expires_at < cutoff_date,
    ).all()

    print(f"Unverified users found: {len(unverified_users)}")

    # Delete each unverified user
    for user in unverified_users:
        print(f"Deleting user: {user.email}, ID: {user.id}")
        db.session.delete(user)  # This will also delete related records due to cascade

    # Commit changes to the database
    db.session.commit()
    print(f"{len(unverified_users)} unverified users removed.")


# Run the script within app context if executed directly
if __name__ == "__main__":
    from app import app

    with app.app_context():
        delete_unverified_users()
