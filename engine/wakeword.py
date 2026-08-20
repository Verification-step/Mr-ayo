"""Wake-word detector for Mr Ayo.

Uses OpenWakeWord when installed. The detector is intentionally isolated so it can
be replaced later without changing the agent.
"""
from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass
from typing import Callable

try:
    import numpy as np
    import sounddevice as sd
    from openwakeword.model import Model
except ImportError:  # optional until dependencies are installed
    np = None
    sd = None
    Model = None


@dataclass
class WakeWordConfig:
    keyword: str = "hey_jarvis"
    sample_rate: int = 16000
    chunk_size: int = 1280
    threshold: float = 0.55


class WakeWordListener:
    def __init__(self, on_wake: Callable[[], None], config: WakeWordConfig | None = None):
        self.on_wake = on_wake
        self.config = config or WakeWordConfig()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _run(self) -> None:
        if Model is None or sd is None or np is None:
            print("[wake-word] install dependencies first: openwakeword sounddevice numpy")
            return
        model = Model(vad_threshold=0.5)
        audio_queue: queue.Queue = queue.Queue()

        def callback(indata, frames, time_info, status):
            if status:
                print(f"[wake-word] {status}")
            audio_queue.put(indata.copy().reshape(-1))

        with sd.InputStream(
            samplerate=self.config.sample_rate,
            channels=1,
            dtype="int16",
            blocksize=self.config.chunk_size,
            callback=callback,
        ):
            print("[wake-word] listening...")
            while not self._stop.is_set():
                try:
                    audio = audio_queue.get(timeout=0.25)
                except queue.Empty:
                    continue
                scores = model.predict(audio)
                score = max(scores.values()) if scores else 0.0
                if score >= self.config.threshold:
                    self.on_wake()
                    time.sleep(1.2)
