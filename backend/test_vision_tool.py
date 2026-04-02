import sys
sys.path.append(".")
import logging
import os
from cognitive_kernel.tools.vision_tool import ComputerVisionTool

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def test_vision_tool():
    print("👁️ Testing Level 36b: Computer Vision (The Eyes)...")
    
    tool = ComputerVisionTool()
    
    # 1. Test Invoice Detection
    print("\n[TEST 1] Testing 'Invoice' Perception")
    # We use a mock protocol to bypass file existence check for testing logic
    result = tool.execute("mock://images/supplier_invoice_001.pdf")
    if result.get("vision_data", {}).get("detected_type") == "DOCUMENT":
        print(f"✅ Perception Success: Identified DOCUMENT (Invoice)")
        print(f"   > OCR Summary: {result['vision_data']['ocr_summary']}")
    else:
        print(f"❌ Perception Failed: {result}")

    # 2. Test Blueprint Detection
    print("\n[TEST 2] Testing 'Blueprint' Perception")
    result = tool.execute("mock://schematic_v2.png")
    if result.get("vision_data", {}).get("detected_type") == "TECHNICAL_DRAWING":
        print(f"✅ Perception Success: Identified TECHNICAL_DRAWING")
        print(f"   > Objects: {result['vision_data']['objects']}")
    else:
        print(f"❌ Perception Failed: {result}")

    # 3. Test Unknown/Generic
    print("\n[TEST 3] Testing Generic Perception")
    result = tool.execute("mock://vacation_photo.jpg")
    if result.get("vision_data", {}).get("detected_type") == "UNKNOWN_IMAGE":
        print(f"✅ Perception Success: Identified UNKNOWN_IMAGE (Default)")
    else:
        print(f"❌ Perception Failed: {result}")

if __name__ == "__main__":
    test_vision_tool()
