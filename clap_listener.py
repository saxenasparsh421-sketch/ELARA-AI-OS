"""ELARA double-clap background activator for Windows.

Runs as a lightweight background process. Two sharp clap-like audio peaks
within a short window trigger the existing ELARA dashboard. If ELARA is
already open the listener sends a localhost activation command instead of
starting a second dashboard instance.
"""
from __future__ import annotations

import math
import socket
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import sounddevice as sd


PROJECT_ROOT = Path(__file__).resolve().parent
MAIN_PY = PROJECT_ROOT / "main.py"
PYTHON_EXE = PROJECT_ROOT / "jarvis_env" / "Scripts" / "python.exe"

HOST = "127.0.0.1"
PORT = 47521

SAMPLE_RATE = 16_000
BLOCK_SIZE = 512
CHANNELS = 1

# Double-clap timing.
MIN_CLAP_GAP = 0.12
MAX_CLAP_GAP = 0.75
TRIGGER_COOLDOWN = 8.0

# Detection tuning. Raise these values if the room causes false triggers.
MIN_PEAK = 0.28
MIN_RMS = 0.035
MIN_CREST = 3.2
MIN_HIGH_FREQ_RATIO = 0.28


class DoubleClapDetector:
    def __init__(self) -> None:
        self.noise_rms = 0.008
        self.last_hit_time: float | None = None
        self.cooldown_until = 0.0

    @staticmethod
    def high_frequency_ratio(samples: np.ndarray) -> float:
        samples = samples.astype(np.float32, copy=False).reshape(-1)
        if samples.size < 64:
            return 0.0

        window = np.hanning(samples.size).astype(np.float32)
        spectrum = np.abs(np.fft.rfft(samples * window))
        total = float(np.sum(spectrum)) + 1e-9
        frequencies = np.fft.rfftfreq(samples.size, d=1.0 / SAMPLE_RATE)
        high = float(np.sum(spectrum[frequencies >= 2_000]))
        return high / total

    def detect_hit(self, block: np.ndarray, now: float) -> bool:
        samples = block.reshape(-1).astype(np.float32, copy=False)
        peak = float(np.max(np.abs(samples)))
        rms = float(math.sqrt(float(np.mean(samples * samples))))

        # Slowly follow the ambient floor without following a clap transient.
        self.noise_rms = (self.noise_rms * 0.985) + (rms * 0.015)
        dynamic_rms = max(MIN_RMS, self.noise_rms * 4.2)

        crest = peak / max(rms, 1e-6)
        high_ratio = self.high_frequency_ratio(samples)

        return (
            peak >= MIN_PEAK
            and rms >= dynamic_rms
            and crest >= MIN_CREST
            and high_ratio >= MIN_HIGH_FREQ_RATIO
        )

    def register_hit(self, now: float) -> bool:
        if now < self.cooldown_until:
            return False

        previous = self.last_hit_time
        self.last_hit_time = now

        if previous is None:
            return False

        gap = now - previous
        if MIN_CLAP_GAP <= gap <= MAX_CLAP_GAP:
            self.last_hit_time = None
            self.cooldown_until = now + TRIGGER_COOLDOWN
            return True

        # Too much time has passed. Treat this hit as the first clap of a
        # new pair instead of discarding it.
        if gap > MAX_CLAP_GAP:
            self.last_hit_time = now

        return False


def app_is_running() -> bool:
    try:
        with socket.create_connection((HOST, PORT), timeout=0.15) as conn:
            return True
    except OSError:
        return False


def activate_existing_app() -> bool:
    try:
        with socket.create_connection((HOST, PORT), timeout=0.5) as conn:
            conn.sendall(b"CLAP")
        return True
    except OSError:
        return False


def launch_app() -> None:
    interpreter = PYTHON_EXE if PYTHON_EXE.exists() else Path(sys.executable)
    if not MAIN_PY.exists():
        raise FileNotFoundError(f"ELARA main.py not found: {MAIN_PY}")

    creation_flags = 0
    if sys.platform.startswith("win"):
        creation_flags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS

    subprocess.Popen(
        [str(interpreter), str(MAIN_PY), "--listen-now"],
        cwd=str(PROJECT_ROOT),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creation_flags,
        close_fds=True,
    )


def trigger_elara() -> None:
    print("[ELARA CLAP] Double clap detected.")

    if app_is_running():
        if activate_existing_app():
            print("[ELARA CLAP] Existing ELARA microphone activated.")
        return

    launch_app()
    print("[ELARA CLAP] ELARA launch requested.")


def main() -> None:
    print("[ELARA CLAP] Listener online.")

    detector = DoubleClapDetector()
    trigger_event = __import__("threading").Event()

    def callback(indata, frames, callback_time, status):
        if status:
            print("[ELARA CLAP AUDIO]", status)

        now = time.monotonic()
        if detector.detect_hit(indata, now):
            if detector.register_hit(now):
                # Do not launch ELARA from the PortAudio callback thread.
                # Signal the owner loop so the input stream can be closed
                # before ELARA opens its own microphone.
                trigger_event.set()

    while True:
        trigger_event.clear()

        try:
            with sd.InputStream(
                samplerate=SAMPLE_RATE,
                blocksize=BLOCK_SIZE,
                channels=CHANNELS,
                dtype="float32",
                callback=callback,
            ):
                print("[ELARA CLAP] Listening for double clap...")
                while not trigger_event.wait(0.10):
                    pass
        except Exception as error:
            print("[ELARA CLAP AUDIO ERROR]", error)
            time.sleep(2.0)
            continue

        # The stream is now fully closed so the dashboard microphone can use
        # the same hardware without an input-device contention problem.
        try:
            trigger_elara()
        except Exception as error:
            print("[ELARA CLAP ERROR]", error)

        time.sleep(TRIGGER_COOLDOWN)


if __name__ == "__main__":
    main()
