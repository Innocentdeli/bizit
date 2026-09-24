"""
migrate_sub_agent.py — adds ai_agent columns and customer_inquiries table
"""
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from database.database import engine
from sqlalchemy import text

def run():
    with engine.connect() as conn:
        # Add columns to businesses
        for col, typedef in [
            ("ai_agent_enabled", "BOOLEAN DEFAULT 0"),
            ("ai_agent_prompt",  "VARCHAR"),
        ]:
            try:
                conn.execute(text(f"ALTER TABLE businesses ADD COLUMN {col} {typedef}"))
                print(f"  + Added businesses.{col}")
            except Exception as e:
                print(f"  ~ businesses.{col}: already exists ({e})")

        # Create customer_inquiries table
        sql = (
            "CREATE TABLE IF NOT EXISTS customer_inquiries ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  business_id VARCHAR REFERENCES businesses(id),"
            "  customer_name VARCHAR,"
            "  customer_email VARCHAR,"
            "  message TEXT,"
            "  agent_reply TEXT,"
            "  status VARCHAR DEFAULT 'PENDING',"
            "  timestamp FLOAT"
            ")"
        )
        try:
            conn.execute(text(sql))
            print("  + Created customer_inquiries table")
        except Exception as e:
            print(f"  ~ customer_inquiries: {e}")

        conn.commit()

    print("\nMigration complete.")

if __name__ == "__main__":
    run()
