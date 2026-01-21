"""
AudioProcessor module for SentinAI.
Handles audio transcription using OpenAI Whisper with GPU optimization.
"""

import os
import torch
import whisper


class AudioProcessor:
    """
    Production-ready audio processor for transcribing audio files
    using OpenAI Whisper with automatic hardware optimization.
    """

    def __init__(self, model_size: str = "base"):
        """
        Initialize the AudioProcessor with Whisper model.
        
        Args:
            model_size: Size of the Whisper model to load. Defaults to 'base'.
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model(model_size, device=self.device)

    def transcribe(self, file_path: str) -> dict:
        """
        Transcribe an audio file to text.
        
        Args:
            file_path: Path to the audio file to transcribe.
            
        Returns:
            Dictionary containing:
                - status: 'success' or 'error'
                - text: Transcribed text (on success)
                - language: Detected language (on success)
                - message: Error message (on error)
        """
        if not os.path.exists(file_path):
            return {
                "status": "error",
                "message": f"File not found: {file_path}"
            }

        try:
            result = self.model.transcribe(file_path)
            return {
                "status": "success",
                "text": result["text"],
                "language": result["language"]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
