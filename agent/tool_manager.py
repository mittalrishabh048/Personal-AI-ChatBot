import json
from typing import Callable, Dict, Any, List, Optional

class ToolManager:
    """
    Manages registration, JSON schema generation, and execution of tools/functions for the AI Agent.
    """

    def __init__(self):
        # Stores tool registry: { tool_name: {"func": callable, "schema": dict} }
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register_tool(self, name: str, description: str, parameters: Dict[str, Any], func: Callable):
        """
        Registers a Python function as an agent tool.

        :param name: Unique name of the tool (e.g., 'get_current_time')
        :param description: Description guiding the LLM on when to use this tool
        :param parameters: JSON Schema dictionary defining function parameters
        :param func: The actual Python function to execute
        """
        schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }
        self._tools[name] = {
            "func": func,
            "schema": schema
        }
        print(f"[ToolManager] Registered tool: {name}")

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Returns a list of all registered tool schemas formatted for Groq / OpenAI tool calling.
        """
        return [tool["schema"] for tool in self._tools.values()]

    def execute_tool(self, tool_name: str, arguments_json: str) -> str:
        """
        Parses JSON arguments from the LLM response and executes the requested tool.

        :param tool_name: Name of the tool requested by the LLM
        :param arguments_json: Stringified JSON arguments provided by the LLM
        :return: String output of the tool execution (or error message)
        """
        if tool_name not in self._tools:
            return f"Error: Tool '{tool_name}' is not registered."

        try:
            # Parse argument string from LLM into a Python dictionary
            args = json.loads(arguments_json) if isinstance(arguments_json, str) and arguments_json else arguments_json
            args = args or {}

            print(f"[ToolManager] Executing '{tool_name}' with args: {args}")
            tool_func = self._tools[tool_name]["func"]
            
            # Execute tool function with unpacked keyword arguments
            result = tool_func(**args)
            return str(result)

        except Exception as e:
            error_msg = f"Error executing tool '{tool_name}': {str(e)}"
            print(f"[ToolManager Error]: {error_msg}")
            return error_msg