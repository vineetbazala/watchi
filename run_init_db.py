"""
Run this ONCE to create watchi.db from schema.sql:

    python run_init_db.py

Re-running it wipes and recreates all tables (see schema.sql's DROP TABLE
statements). That is fine before you have real data, dangerous after, so it
asks for confirmation if a database already exists.
"""
import os

from app import app
import db

with app.app_context():
    if os.path.exists(db.DATABASE) and os.path.getsize(db.DATABASE) > 0:
        answer = input(
            "watchi.db already exists. This will DELETE all data. "
            "Type YES to continue: "
        )
        if answer != "YES":
            print("Cancelled. Nothing was changed.")
            raise SystemExit

    db.init_db()
    print("watchi.db created from schema.sql")