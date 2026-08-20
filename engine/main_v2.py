from __future__ import annotations
import os, tempfile, time, wave
from .agent_v2 import Agent
from .ai import OpenRouter
from .config import settings

try:
    import sounddevice as sd
    import numpy as np
except ImportError:
    sd=None; np=None

WAKE = settings.wake_phrase.lower()


def record(seconds=5, rate=16000):
    if sd is None or np is None: raise RuntimeError("Install sounddevice and numpy first")
    data=sd.rec(int(seconds*rate), samplerate=rate, channels=1, dtype="int16"); sd.wait()
    path=os.path.join(tempfile.gettempdir(), "mr_ayo_command.wav")
    with wave.open(path,"wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate); f.writeframes(data.tobytes())
    return path


def speak(ai, text):
    try:
        path=os.path.join(tempfile.gettempdir(), "mr_ayo_reply.mp3")
        ai.speak(text,path)
        os.startfile(path)
    except Exception as e:
        print(f"[tts] {e}\nMr Ayo: {text}")


def main():
    ai=OpenRouter(); agent=Agent()
    print(f"Mr Ayo ready. Wake phrase: '{WAKE}'")
    print("Say the wake phrase, then your command. Press Ctrl+C to stop.")
    while True:
        try:
            wake_audio=record(2.5)
            heard=ai.transcribe(wake_audio).strip().lower()
            if WAKE not in heard: continue
            print("[LISTENING]")
            command_audio=record(6)
            command=ai.transcribe(command_audio).strip()
            if not command: continue
            print(f"You: {command}")
            reply=agent.run(command)
            print(f"Mr Ayo: {reply}")
            speak(ai, reply)
            time.sleep(0.5)
        except KeyboardInterrupt: break
        except Exception as e: print(f"[error] {e}")

if __name__ == "__main__": main()
