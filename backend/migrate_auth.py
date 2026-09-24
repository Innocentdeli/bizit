"""
migrate_auth.py — creates the users table
"""
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from database.database import engine
from sqlalchemy import text

def run():
    with engine.connect() as conn:
        # Create users table
        sql = (
            "CREATE TABLE IF NOT EXISTS users ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  email VARCHAR UNIQUE,"
            "  hashed_password VARCHAR,"
            "  is_active BOOLEAN DEFAULT 1,"
            "  role VARCHAR DEFAULT 'user',"
            "  business_id VARCHAR REFERENCES businesses(id)"
            ")"
        )
        try:
            conn.execute(text(sql))
            print("  + Created users table")
        except Exception as e:
            print(f"  ~ users: {e}")

        conn.commit()

    print("\nAuth migration complete.")

if __name__ == "__main__":
    run()
