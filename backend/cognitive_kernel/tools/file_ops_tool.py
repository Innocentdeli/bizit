from cognitive_kernel.tool_registry import AgentTool
from typing import Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

class FileOpsTool(AgentTool):
    """
    Allow agents to safely read and write files within the workspace.
    Enforces the same Immutability Guard as the RecursiveEditor.
    """
    def __init__(self):
        super().__init__("file_ops", "Read or write files in the workspace.")
        # Hardcoded Sovereign Guard (Duplicated here for depth-defense)
        self.IMMUTABLE_FILES = [
            "directive_engine.py", 
            "main_loop.py", 
            "recursive_editor.py", 
            "local_llm_client.py"
        ]

    def execute(self, operation: str = "read", file_path: str = "", content: str = "", **kwargs) -> Dict[str, Any]:
        """
        Execute file operation.
        operation: 'read' or 'write'
        file_path: Relative path to file
        content: Content to write (if writing)
        """
        logger.info(f"📂 [FILE_OPS] Operation: {operation} on '{file_path}'")
        
        # 1. Security Check
        if any(protected in file_path for protected in self.IMMUTABLE_FILES):
            return {
                "status": "error", 
                "message": f"ACCESS DENIED: {os.path.basename(file_path)} is Sovereign-Protected."
            }

        # 2. Execute
        try:
            if operation == "read":
                if not os.path.exists(file_path):
                    return {"status": "error", "message": "File not found."}
                with open(file_path, "r", encoding="utf-8") as f:
                    data = f.read()
                return {"status": "success", "content": data[:2000] + "... (truncated)" if len(data) > 2000 else data}
            
            elif operation == "write":
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return {"status": "success", "message": f"File '{file_path}' written successfully."}
            
            else:
                return {"status": "error", "message": f"Unknown operation: {operation}"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "name": "file_ops",
            "description": "Read or write files safely.",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": ["read", "write"], "description": "Operation type."},
                    "file_path": {"type": "string", "description": "Path to the target file."},
                    "content": {"type": "string", "description": "Content to write (optional)."}
                },
                "required": ["operation", "file_path"]
            }
        }
