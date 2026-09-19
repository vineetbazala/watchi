"""
Run this ONCE to create watchi.db from schema.sql:

    python run_init_db.py

Re-running it wipes and recreates all tables (see schema.sql's DROP TABLE
statements) — fine before you have real data in there, dangerous after.
"""
from app import app
import db

with app.app_context():
    db.init_db()
    print("watchi.db created from schema.sql")