"""
migrate_social.py — creates the social_posts table
"""
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from database.database import engine
from sqlalchemy import text

def run():
    with engine.connect() as conn:
        # Create social_posts table
        sql = (
            "CREATE TABLE IF NOT EXISTS social_posts ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  business_id VARCHAR REFERENCES businesses(id),"
            "  platform VARCHAR DEFAULT 'Twitter',"
            "  post_copy TEXT,"
            "  image_url VARCHAR,"
            "  timestamp FLOAT"
            ")"
        )
        try:
            conn.execute(text(sql))
            print("  + Created social_posts table")
        except Exception as e:
            print(f"  ~ social_posts: {e}")

        conn.commit()

    print("\nMigration complete.")

if __name__ == "__main__":
    run()
