"""Audio transcription service using Faster-Whisper."""
from faster_whisper import WhisperModel
import config
from pathlib import Path
from typing import Optional


class Transcriber:
    """Handles audio transcription using Faster-Whisper."""
    
    def __init__(self, model_size: str = None):
        self.model_size = model_size or config.WHISPER_MODEL
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model."""
        print(f"Loading Whisper model: {self.model_size}")
        self.model = WhisperModel(
            self.model_size,
            device="cpu",  # Change to "cuda" if you have GPU
            compute_type="int8"  # Use "float16" for GPU
        )
        print("Model loaded successfully")
    
    def transcribe(self, audio_path: str, language: str = None) -> dict:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'en', 'fr'). If None, auto-detect.
        
        Returns:
            Dictionary with transcription text and metadata
        """
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True,  # Voice Activity Detection
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        # Combine all segments
        full_text = " ".join([segment.text for segment in segments])
        
        return {
            "text": full_text.strip(),
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration,
            "segments": [
                {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text
                }
                for segment in segments
            ]
        }
    
    def transcribe_stream(self, audio_stream, language: str = None) -> dict:
        """Transcribe from audio stream (for real-time recording)."""
        # This would be implemented for real-time transcription
        # For now, we'll use file-based transcription
        raise NotImplementedError("Stream transcription not yet implemented")

