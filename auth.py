from flask_login import LoginManager, UserMixin
from werkzeug.security import check_password_hash
import db

login_manager = LoginManager()
login_manager.login_view = "login"  # if not logged in, redirects here automatically


class User(UserMixin):
    """Wraps one row from the users table so Flask-Login can work with it.
    UserMixin gives us is_authenticated / is_active / get_id() for free —
    that's the interface Flask-Login expects."""

    def __init__(self, row):
        self.id = row["id"]
        self.username = row["username"]
        self.password_hash = row["password_hash"]
        # row.keys() check handles a DB where the ALTER TABLE hasn't run yet
        self.profile_image = row["profile_image"] if "profile_image" in row.keys() else None

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get(user_id):
        row = db.get_db().execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return User(row) if row else None

    @staticmethod
    def get_by_username(username):
        row = db.get_db().execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        return User(row) if row else None


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login calls this on every request to reload the logged-in
    user from their session cookie. You never call this yourself."""
    return User.get(user_id)


def init_app(app):
    login_manager.init_app(app)