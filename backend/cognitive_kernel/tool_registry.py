from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class AgentTool(ABC):
    """
    Abstract base class for all tools that agents can use.
    Enforces a standard interface for execution and schema definition.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with the given arguments.
        Must return a dictionary with at least a "status" key.
        """
        pass

    @property
    @abstractmethod
    def schema(self) -> Dict[str, Any]:
        """
        Return the JSON schema or parameter definition for this tool.
        Used by the LLM or agent to understand how to call it.
        """
        pass

class ToolRegistry:
    """
    Central catalog of available tools.
    Agents query this registry to find tools they are authorized to use.
    """
    def __init__(self):
        self._tools: Dict[str, AgentTool] = {}
        logger.info("🛠️ ToolRegistry initialized.")

    def register_tool(self, tool: AgentTool):
        """Register a new tool capability."""
        if tool.name in self._tools:
            logger.warning(f"Overwriting existing tool registration: {tool.name}")
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def get_tool(self, name: str) -> Optional[AgentTool]:
        """Retrieve a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, str]]:
        """List all available tools and their descriptions."""
        return [{"name": t.name, "description": t.description} for t in self._tools.values()]

    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a named tool safely.
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return {"status": "error", "message": f"Tool '{tool_name}' not found."}
        
        try:
            logger.info(f"Executing tool '{tool_name}' with args: {kwargs.keys()}")
            return tool.execute(**kwargs)
        except Exception as e:
            logger.error(f"Tool execution failed ({tool_name}): {e}")
            return {"status": "error", "message": str(e)}
