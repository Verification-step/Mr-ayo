from __future__ import annotations
import base64
import json
from typing import Any
import requests
from .config import settings

API = "https://openrouter.ai/api/v1"

class OpenRouter:
    def __init__(self):
        if not settings.openrouter_key:
            raise RuntimeError("OPENROUTER_API_KEY is missing. Put it in .env")
        self.headers = {
            "Authorization": f"Bearer {settings.openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Mr Ayo",
        }

    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None):
        body = {"model": settings.brain_model, "messages": messages, "temperature": 0.2}
        if tools:
            body["tools"] = tools
            body["tool_choice"] = "auto"
        r = requests.post(f"{API}/chat/completions", headers=self.headers, json=body, timeout=90)
        if r.status_code >= 400:
            body["model"] = settings.fallback_model
            r = requests.post(f"{API}/chat/completions", headers=self.headers, json=body, timeout=90)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]

    def transcribe(self, audio_path: str) -> str:
        with open(audio_path, "rb") as f:
            r = requests.post(
                f"{API}/audio/transcriptions",
                headers={"Authorization": f"Bearer {settings.openrouter_key}"},
                files={"file": ("audio.wav", f, "audio/wav")},
                data={"model": "openai/gpt-4o-mini-transcribe"},
                timeout=90,
            )
        r.raise_for_status()
        return r.json().get("text", "")

    def speak(self, text: str, output_path: str):
        r = requests.post(
            f"{API}/audio/speech",
            headers=self.headers,
            json={"model": settings.tts_model, "voice": settings.tts_voice, "input": text, "response_format": "mp3"},
            timeout=90,
        )
        r.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(r.content)
