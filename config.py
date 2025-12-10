"""Configuration settings for the application."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PATIENTS_DIR = DATA_DIR / "patients"
CONVERSATIONS_DIR = DATA_DIR / "conversations"

# Create directories if they don't exist
PATIENTS_DIR.mkdir(parents=True, exist_ok=True)
CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)

# Database
DATABASE_PATH = DATA_DIR / "patients.db"
CHROMADB_PATH = DATA_DIR / "chromadb"

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:latest")  # Using latest which is 8B

# Whisper Configuration
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")  # base, small, medium, large-v2

# Medical Entity Extraction
MEDICAL_MODEL = os.getenv("MEDICAL_MODEL", "en_core_web_sm")  # Can upgrade to medical models

# PDF Settings
PDF_OUTPUT_DIR = PATIENTS_DIR / "pdfs"
PDF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Audio Settings
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
AUDIO_FORMAT = "wav"

