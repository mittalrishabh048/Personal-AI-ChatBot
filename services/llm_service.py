import os
from typing import List, Dict, Any, Optional
from openai import OpenAI

class LLMService:
    """
    Dedicated service for managing interactions with the Groq API.
    Encapsulates client initialization, chat completion requests, and tool definition formatting.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        # Automatically pull from environment variables set on your machine
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set on your system.")

        self.model = model
        
        # Groq endpoint via OpenAI-compatible SDK
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )

    def get_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7
    ) -> Any:
        """
        Sends conversation messages and tool schemas to Groq API.
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }

            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message

        except Exception as e:
            print(f"[LLMService Error]: {str(e)}")
            raise e