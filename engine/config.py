import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    openrouter_key: str = os.getenv("OPENROUTER_API_KEY", "")
    brain_model: str = os.getenv("BRAIN_MODEL", "openrouter/free")
    fallback_model: str = os.getenv("BRAIN_FALLBACK_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free")
    perception_model: str = os.getenv("PERCEPTION_MODEL", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free")
    tts_model: str = os.getenv("TTS_MODEL", "openai/gpt-4o-mini-tts-2025-12-15")
    tts_voice: str = os.getenv("TTS_VOICE", "alloy")
    wake_phrase: str = os.getenv("WAKE_PHRASE", "mr ayo")
    host: str = os.getenv("MR_AYO_HOST", "127.0.0.1")
    port: int = int(os.getenv("MR_AYO_PORT", "8765"))

settings = Settings()
