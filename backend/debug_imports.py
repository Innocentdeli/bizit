import sys
import traceback

print(f"Python version: {sys.version}")
try:
    print("Importing FastAPI...")
    from fastapi import FastAPI
    print("✅ FastAPI imported successfully.")
except Exception as e:
    print("❌ FastAPI import failed.")
    traceback.print_exc()

try:
    print("\nImporting uvicorn...")
    import uvicorn
    print("✅ uvicorn imported successfully.")
except Exception as e:
    print("❌ uvicorn import failed.")
    traceback.print_exc()

try:
    print("\nImporting local modules...")
    from core.state import OrganismState
    from human_interface.chat_engine import ChatEngine
    from cognitive_kernel.tools.web_search_tool import WebSearchTool
    from cognitive_kernel.local_llm_client import LocalLLMClient
    print("✅ Local modules imported successfully.")
except Exception as e:
    print("❌ Local module import failed.")
    traceback.print_exc()
