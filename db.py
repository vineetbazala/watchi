import sqlite3
from flask import g

DATABASE = "watchi.db"


def get_db():
    """Open a new database connection for this request if one doesn't exist yet.
    Flask's `g` object is a per-request storage — this means every route in
    app.py can call get_db() and get the SAME connection, without passing it
    around as a parameter everywhere."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # lets us access columns by name, e.g. row["title"]
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """Closes the database connection at the end of the request. Registered
    below via app.teardown_appcontext — Flask calls this automatically,
    you never call it yourself."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Wipes and recreates all tables from schema.sql.
    Run this once (see run_init_db.py) to set up watchi.db for the first time.
    WARNING: this deletes all existing data — only run it once, at the start."""
    db = get_db()
    with open("schema.sql") as f:
        db.executescript(f.read())


def init_app(app):
    """Call this once in app.py: db.init_app(app)
    Registers close_db so Flask cleans up the connection after every request."""
    app.teardown_appcontext(close_db)