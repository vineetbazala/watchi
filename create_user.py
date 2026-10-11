"""
Create a Watchi user account:

    python create_user.py

Run it on the server after run_init_db.py. It's also safe to run on your
laptop to add an extra account (for example a demo account).
"""
import getpass

from werkzeug.security import generate_password_hash

from app import app
import db

username = input("Username: ").strip()
if not username:
    raise SystemExit("Username can't be empty.")

password = getpass.getpass("Password: ")
if len(password) < 8:
    raise SystemExit("Password must be at least 8 characters.")
if password != getpass.getpass("Repeat password: "):
    raise SystemExit("Passwords didn't match. Nothing was created.")

with app.app_context():
    database = db.get_db()
    exists = database.execute(
        "SELECT 1 FROM users WHERE username = ?", (username,)
    ).fetchone()
    if exists:
        raise SystemExit(f"User '{username}' already exists. Nothing changed.")

    database.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, generate_password_hash(password)),
    )
    database.commit()
    print(f"User '{username}' created. You can log in now.")