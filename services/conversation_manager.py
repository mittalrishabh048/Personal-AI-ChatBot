import json
from typing import List, Dict, Any
from services.llm_service import LLMService
from agent.tool_manager import ToolManager
from agent.tools.time_tool import TIME_TOOL_SCHEMA

class ConversationManager:
    """
    Orchestrates the conversation flow between user prompts, the LLM service,
    and agent tools.
    """

    def __init__(self):
        # 1. Initialize LLM Service
        self.llm_service = LLMService()

        # 2. Initialize Tool Manager
        self.tool_manager = ToolManager()

        # 3. Register available tools
        self._register_default_tools()

    def _register_default_tools(self):
        """Registers all tools available to the agent."""
        self.tool_manager.register_tool(
            name=TIME_TOOL_SCHEMA["name"],
            description=TIME_TOOL_SCHEMA["description"],
            parameters=TIME_TOOL_SCHEMA["parameters"],
            func=TIME_TOOL_SCHEMA["func"]
        )

    def process_message(self, user_message: str, history: List[Dict[str, Any]] = None) -> str:
        """
        Executes the main agent processing loop.
        """
        if history is None:
            history = []

        # Construct payload with history and current message
        messages = list(history)
        messages.append({"role": "user", "content": user_message})

        # Fetch schemas for available tools
        tools = self.tool_manager.get_tool_schemas()

        # Step A: First call to LLM
        response_message = self.llm_service.get_completion(messages=messages, tools=tools)

        # Step B: Check if the model decided to call a tool
        if hasattr(response_message, "tool_calls") and response_message.tool_calls:
            # Append initial model decision to message chain
            messages.append(response_message)

            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                arguments = tool_call.function.arguments

                # Execute requested tool via ToolManager
                tool_output = self.tool_manager.execute_tool(function_name, arguments)

                # Append tool result back to message context
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": tool_output
                })

            # Step C: Send tool output back to Groq for final natural response
            final_response = self.llm_service.get_completion(messages=messages)
            return final_response.content

        # Direct reply without tool execution
        return response_message.content