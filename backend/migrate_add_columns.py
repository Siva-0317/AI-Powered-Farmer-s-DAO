# backend/migrate_add_columns.py
"""
One-off migration helper for SQLite used by the Flask backend.
Adds missing simple columns (including `email`) to the `farmers` table.
Run this from the backend/ folder using your Python interpreter.
"""

import sqlite3, os, sys, uuid
from datetime import datetime

try:
    # import app & db to discover sqlite path
    from app import app
    from database import db
except Exception as e:
    print("Error importing app/db. Make sure to run from backend/ folder.")
    print("Exception:", e)
    sys.exit(1)


def add_column_if_missing(cur, table, col_name, col_def):
    cur.execute(f"PRAGMA table_info({table});")
    cols = [r[1] for r in cur.fetchall()]
    if col_name in cols:
        print(f"Column `{col_name}` already exists in {table}, skipping.")
        return False
    print(f"Adding column `{col_name}` to {table} with definition: {col_def}")
    cur.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def};")
    return True


def migrate():
    with app.app_context():
        engine = db.get_engine()
        db_file = engine.url.database
        print("Detected sqlite DB file:", db_file)
        if not os.path.exists(db_file):
            print("Database file not found:", db_file)
            sys.exit(1)

        conn = sqlite3.connect(db_file)
        cur = conn.cursor()

        # Ensure basic columns we expect exist (idempotent)
        to_ensure = [
            ("registration_no", "TEXT DEFAULT ''"),
            ("mobile", "TEXT DEFAULT ''"),
            ("aadhaar", "TEXT DEFAULT ''"),
            ("wallet_address", "TEXT DEFAULT ''"),
            ("gov_id_path", "TEXT DEFAULT ''"),
            ("selfie_path", "TEXT DEFAULT ''"),
            ("verification_meta", "TEXT DEFAULT ''"),
            ("verified", "INTEGER DEFAULT 0"),
            ("email", "TEXT DEFAULT ''")   # <-- the missing column causing your error
        ]

        added = []
        for name, definition in to_ensure:
            try:
                if add_column_if_missing(cur, "farmers", name, definition):
                    added.append(name)
            except Exception as ex:
                print(f"Failed to add column {name}: {ex}")

        conn.commit()

        # If registration_no empty for existing rows, fill with generated values
        try:
            cur.execute("SELECT rowid, registration_no FROM farmers;")
            rows = cur.fetchall()
            updated = 0
            for row in rows:
                rowid, reg = row
                if reg is None or str(reg).strip() == "":
                    new_reg = f"HBL-{datetime.utcnow().year}-{uuid.uuid4().hex[:6].upper()}"
                    cur.execute("UPDATE farmers SET registration_no = ? WHERE rowid = ?;", (new_reg, rowid))
                    updated += 1
            conn.commit()
            if updated:
                print(f"Populated registration_no for {updated} rows.")
        except Exception:
            # table may not exist yet / or other issues - ignore gracefully
            pass

        # Print resulting columns for confirmation
        cur.execute("PRAGMA table_info(farmers);")
        cols = cur.fetchall()
        print("Final farmers table columns:")
        for c in cols:
            print(f" - {c[1]} (type: {c[2]})")

        conn.close()
        print("Migration complete. Added columns:", added)


if __name__ == "__main__":
    migrate()
