import uvicorn
import os
import sys

# Ensure backend root is in path
sys.path.append(os.getcwd())

from human_interface.dashboard_api import app

if __name__ == "__main__":
    print("Starting BIZIT Dashboard API on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
