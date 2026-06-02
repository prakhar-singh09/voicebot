import os
from dotenv import load_dotenv

# Load .env file from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")

# LLM Config (Cyfuture API)
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.cyfuture.ai/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "/workspace/models/Llama-4-Maverick-17B-128E-Instruct")

# Whisper STT Config
WHISPER_BASE_URL = os.getenv("WHISPER_BASE_URL", "http://49.50.77.130:8000/v1")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "/workspace/models/whisper-large-v3")

# TTS Config (Edge TTS voice)
# High-quality Hindi/English bilingual neural voices:
# "hi-IN-MadhurNeural" (Male), "hi-IN-SwaraNeural" (Female)
TTS_VOICE = os.getenv("TTS_VOICE", "hi-IN-MadhurNeural")
