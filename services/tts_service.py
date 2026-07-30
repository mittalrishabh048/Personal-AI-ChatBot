import os
import logging
from gtts import gTTS

class TTSService:
    """
    Dedicated service for handling Text-to-Speech (TTS) synthesis using gTTS.
    """

    def __init__(self, default_language: str = "en"):
        self.default_language = default_language

    def generate_speech(self, text: str, output_path: str = "output_response.mp3") -> str:
        """
        Synthesizes text into an audio file.

        :param text: Text string to convert to speech
        :param output_path: Target path for the output audio file
        :return: Path to the generated audio file
        """
        if not text or not text.strip():
            raise ValueError("Input text for TTS synthesis cannot be empty.")

        try:
            logging.info(f"[TTSService] Synthesizing audio for text: '{text[:30]}...'")
            
            # Initialize gTTS engine
            tts = gTTS(text=text, lang=self.default_language, slow=False)
            
            # Save audio file to disk
            tts.save(output_path)
            logging.info(f"[TTSService] Audio successfully generated at: {output_path}")
            
            return output_path

        except Exception as e:
            logging.error(f"[TTSService Error]: Failed to generate speech: {e}")
            raise e