import sys, os, time
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from database.database import SessionLocal, Base, engine
from database.models import Business, CustomerInquiry

def seed():
    # Ensure new tables are created
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    
    # Enable AI Agent for "Urban Dynamics"
    biz = db.query(Business).filter(Business.name == "Urban Dynamics").first()
    if biz:
        biz.ai_agent_enabled = True
        biz.ai_agent_prompt = "You are friendly, use emojis, and emphasize that we only use eco-friendly plumbing materials."
        db.commit()
        print(f"[OK] Enabled AI Sub-Agent for {biz.name}")
        
        # Test 1: We will trigger a POST request to test the background task manually via curl.
        print("\nSeed complete! To test the Sub-Agent, run:")
        print(f"""curl -X POST "http://localhost:8002/business/{biz.id}/inquire" -H "Content-Type: application/json" -d "{{\\"customer_name\\":\\"Sarah\\",\\"customer_email\\":\\"sarah@example.com\\",\\"message\\":\\"Hi, do you fix leaking pipes and how much is it?\\"}}" """)
    else:
        print("[MISS] Could not find Urban Dynamics.")

    db.close()

if __name__ == "__main__":
    seed()
