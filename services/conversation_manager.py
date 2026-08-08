import json
from typing import List, Dict, Any
from services.llm_service import LLMService
from agent.tool_manager import ToolManager
from agent.tools.time_tool import TIME_TOOL_SCHEMA

class ConversationManager:
    """
    Orchestrates conversation flow between user prompts, the LLM service,
    and registered tools.
    """

    def __init__(self):
        self.llm_service = LLMService()
        self.tool_manager = ToolManager()
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
        if history is None:
            history = []

        system_instruction = {
            "role": "system",
            "content": (
                "You are a helpful AI Assistant. "
                "Remember conversation details mentioned by the user previously. "
                "You have access to a tool named 'get_current_time'. "
                "Only call 'get_current_time' if the user explicitly asks for the current date, time, or temporal updates. "
                "Otherwise, respond naturally using conversation history context."
            )
        }
        
        # Combine system prompt + chronological history + current turn
        messages = [system_instruction] + list(history) + [{"role": "user", "content": user_message}]

        tools = self.tool_manager.get_tool_schemas()

        try:
            response_message = self.llm_service.get_completion(messages=messages, tools=tools)
        except Exception as llm_err:
            print(f"[ConversationManager Error]: LLM completion failed: {llm_err}")
            return "I am currently having trouble reaching my intelligence engine. Please try again shortly."

        # Handle tool calling
        if hasattr(response_message, "tool_calls") and response_message.tool_calls:
            messages.append(response_message)

            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                arguments = tool_call.function.arguments

                try:
                    tool_output = self.tool_manager.execute_tool(function_name, arguments)
                except Exception as tool_err:
                    tool_output = f"Tool Execution Failure: Unable to complete '{function_name}'. Details: {str(tool_err)}"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": tool_output
                })

            try:
                final_response = self.llm_service.get_completion(messages=messages)
                return final_response.content
            except Exception:
                return "Executed the required action, but failed to format the response string."

        return response_message.content or "I processed your request, but have no text response to return."