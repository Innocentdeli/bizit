from cognitive_kernel.tool_registry import AgentTool
from typing import Dict, Any
import logging
import os
import random

logger = logging.getLogger(__name__)

class ComputerVisionTool(AgentTool):
    """
    Allows agents to 'see' and analyze images.
    Level 36b: The Eyes of the Organism.
    """
    def __init__(self):
        super().__init__("computer_vision", "Analyze an image file and return visual description.")

    def execute(self, image_path: str = "", **kwargs) -> Dict[str, Any]:
        logger.info(f"👁️ [VISION] Analyzing image: '{image_path}'")
        
        if not os.path.exists(image_path):
            # If strictly a file path, fail. 
            # But let's allow 'simulated' paths for testing if they start with 'mock://'
            if not image_path.startswith("mock://"):
                return {"status": "error", "message": f"Image file not found: {image_path}"}
        
        # --- Level 36b MVP: Mock Perception ---
        # In a real system, this would call OpenCV, Tesseract (OCR), or OpenAI Vision (GPT-4o)
        
        filename = os.path.basename(image_path).lower()
        analysis = {}
        
        # 1. Simulate OCR / Object Detection based on filename context
        if "invoice" in filename or "receipt" in filename:
            analysis = {
                "detected_type": "DOCUMENT",
                "ocr_summary": f"Detected Total: ${random.randint(50, 5000)}.99",
                "merchant": "Unknown Vendor",
                "date": "2026-01-23"
            }
        elif "blueprint" in filename or "schematic" in filename:
            analysis = {
                "detected_type": "TECHNICAL_DRAWING",
                "objects": ["Circuit", "Power Supply", "Microcontroller"],
                "dimensions": "1024x768"
            }
        elif "shipping" in filename or "label" in filename:
             analysis = {
                "detected_type": "LOGISTICS_LABEL",
                "barcode": f"TRK-{random.randint(1000, 9999)}",
                "destination": "Detected Address: 123 Innovation Dr."
            }
        else:
            analysis = {
                "detected_type": "UNKNOWN_IMAGE",
                "dominant_colors": ["#FF0000", "#00FF00"],
                "description": "A generic visual stimulus."
            }
            
        return {
            "status": "success",
            "image_path": image_path,
            "vision_data": analysis,
            "confidence": 0.95
        }

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "name": "computer_vision",
            "description": "Analyze an image to extract text, objects, and metadata.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Local path or URL of the image."}
                },
                "required": ["image_path"]
            }
        }
