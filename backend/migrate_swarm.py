"""
migrate_swarm.py — adds reviews columns and appointments table
"""
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from database.database import engine
from sqlalchemy import text

def run():
    with engine.connect() as conn:
        # Add columns to reviews
        for col, typedef in [
            ("agent_reply", "TEXT"),
            ("reply_status",  "VARCHAR DEFAULT 'PENDING'"),
        ]:
            try:
                conn.execute(text(f"ALTER TABLE reviews ADD COLUMN {col} {typedef}"))
                print(f"  + Added reviews.{col}")
            except Exception as e:
                print(f"  ~ reviews.{col}: already exists ({e})")

        # Create appointments table
        sql = (
            "CREATE TABLE IF NOT EXISTS appointments ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  business_id VARCHAR REFERENCES businesses(id),"
            "  customer_name VARCHAR,"
            "  customer_email VARCHAR,"
            "  requested_time VARCHAR,"
            "  service VARCHAR,"
            "  agent_confirmation_message TEXT,"
            "  status VARCHAR DEFAULT 'PENDING',"
            "  timestamp FLOAT"
            ")"
        )
        try:
            conn.execute(text(sql))
            print("  + Created appointments table")
        except Exception as e:
            print(f"  ~ appointments: {e}")

        conn.commit()

    print("\nMigration complete.")

if __name__ == "__main__":
    run()
