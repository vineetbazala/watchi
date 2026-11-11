"""
Manage Watchi user accounts:

    python manage_users.py list
    python manage_users.py passwd <username>
    python manage_users.py delete <username>
"""
import getpass
import glob
import os
import sys

from werkzeug.security import generate_password_hash

from app import app
import db


def list_users(database):
    rows = database.execute(
        """
        SELECT u.id, u.username, u.created_at,
               (SELECT COUNT(*) FROM movies WHERE user_id = u.id) AS movies,
               (SELECT COUNT(*) FROM series WHERE user_id = u.id) AS shows
        FROM users u ORDER BY u.id
        """
    ).fetchall()
    if not rows:
        print("No users yet.")
        return
    print(f"{'ID':<4} {'USERNAME':<20} {'MOVIES':<7} {'SHOWS':<6} CREATED")
    for r in rows:
        print(f"{r['id']:<4} {r['username']:<20} {r['movies']:<7} {r['shows']:<6} {r['created_at']}")


def change_password(database, username):
    user = database.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()
    if not user:
        raise SystemExit(f"No user named '{username}'.")
    password = getpass.getpass("New password: ")
    if len(password) < 8:
        raise SystemExit("Password must be at least 8 characters.")
    if password != getpass.getpass("Repeat password: "):
        raise SystemExit("Passwords didn't match. Nothing changed.")
    database.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (generate_password_hash(password), user["id"]),
    )
    database.commit()
    print(f"Password changed for '{username}'.")


def delete_user(database, username):
    user = database.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()
    if not user:
        raise SystemExit(f"No user named '{username}'.")
    confirm = input(
        f"This permanently deletes '{username}' and all their movies and shows.\n"
        "Type the username to confirm: "
    )
    if confirm != username:
        raise SystemExit("Cancelled. Nothing was deleted.")
    uid = user["id"]
    database.execute("DELETE FROM movies WHERE user_id = ?", (uid,))
    database.execute("DELETE FROM series WHERE user_id = ?", (uid,))
    database.execute("DELETE FROM users WHERE id = ?", (uid,))
    database.commit()
    avatars = os.path.join(app.root_path, "static", "avatars", f"user_{uid}.*")
    for path in glob.glob(avatars):
        os.remove(path)
    print(f"User '{username}' deleted.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] not in ("list", "passwd", "delete"):
        raise SystemExit(__doc__)
    with app.app_context():
        database = db.get_db()
        if args[0] == "list":
            list_users(database)
        elif len(args) < 2:
            raise SystemExit("Please give a username.")
        elif args[0] == "passwd":
            change_password(database, args[1])
        else:
            delete_user(database, args[1])