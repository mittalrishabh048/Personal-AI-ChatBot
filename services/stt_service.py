import os
from typing import Optional
from openai import OpenAI

class STTService:
    """
    Dedicated service for handling Speech-to-Text (STT) transcription
    using Groq's Whisper endpoint.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "whisper-large-v3-turbo"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set.")

        self.model = model
        # Re-using the Groq OpenAI-compatible client endpoint
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )

    def transcribe_audio(self, file_path: str) -> str:
        """
        Sends an audio file to Groq Whisper and returns the transcribed text.

        :param file_path: Path to the local audio file (e.g., .wav, .mp3, .m4a, .webm)
        :return: Transcribed text string
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found at path: {file_path}")

        try:
            with open(file_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    response_format="text"
                )
            
            # OpenAI client returns either a string directly or an object depending on format
            text_result = transcription if isinstance(transcription, str) else getattr(transcription, "text", "")
            return text_result.strip()

        except Exception as e:
            print(f"[STTService Error]: {str(e)}")
            raise e