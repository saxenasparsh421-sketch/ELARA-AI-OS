"""
speech/wakeword.py

JARVIS Wake Word + Double Clap Detection
"""

import time
import numpy as np
import sounddevice as sd
from openwakeword.model import Model


class WakeWordDetector:

    def __init__(self):

        print("Loading OpenWakeWord + Clap Detection...")

        # Existing "Hey Jarvis" wake word
        self.model = Model(inference_framework="onnx")

        self.sample_rate = 16000

        # Keep the existing wake-word chunk size
        self.chunk_size = 1280

        self.threshold = 0.75

        # -----------------------------
        # Double Clap Settings
        # -----------------------------

        self.first_clap_time = None
        self.last_activation_time = 0

        # Second clap must happen within this time
        self.double_clap_window = 1.0

        # Prevent immediate repeated activation
        self.clap_cooldown = 1.5

        # Adaptive room-noise levels
        self.noise_rms = 0.01
        self.noise_peak = 0.05

    def _is_clap(self, audio):
        """
        Detect a short, sharp sound such as a hand clap.
        """

        audio = audio.astype(np.float32) / 32768.0

        if len(audio) < 2:
            return False

        # Detect fast changes in the audio signal.
        high_freq = np.diff(audio)

        rms = np.sqrt(np.mean(high_freq ** 2))
        peak = np.max(np.abs(high_freq))

        # Slowly learn the normal room noise level.
        if rms < self.noise_rms * 2.5:

            self.noise_rms = (
                self.noise_rms * 0.95
                + rms * 0.05
            )

        if peak < self.noise_peak * 2.5:

            self.noise_peak = (
                self.noise_peak * 0.95
                + peak * 0.05
            )

        # Adaptive thresholds
        rms_threshold = max(
            0.035,
            self.noise_rms * 4.0
        )

        peak_threshold = max(
            0.12,
            self.noise_peak * 3.0
        )

        return (
            rms > rms_threshold
            and peak > peak_threshold
        )

    def _double_clap_detected(self):
        """
        Detect two claps within the allowed time window.
        """

        now = time.monotonic()

        # Remove an old first clap
        if (
            self.first_clap_time is not None
            and now - self.first_clap_time
            > self.double_clap_window
        ):

            self.first_clap_time = None

        # First clap
        if self.first_clap_time is None:

            self.first_clap_time = now

            print("Clap detected...")

            return False

        # Second clap
        elapsed = now - self.first_clap_time

        if 0.12 <= elapsed <= self.double_clap_window:

            self.first_clap_time = None

            # Cooldown
            if (
                now - self.last_activation_time
                >= self.clap_cooldown
            ):

                self.last_activation_time = now

                print("Double clap detected!")

                return True

        return False

    def wait(self):

        print('Waiting for "Hey Jarvis" or double clap...')

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            blocksize=self.chunk_size,
        ) as stream:

            while True:

                audio, _ = stream.read(
                    self.chunk_size
                )

                audio = (
                    audio
                    .flatten()
                    .astype(np.int16)
                )

                # ==================================
                # 1. EXISTING "HEY JARVIS" DETECTION
                # ==================================

                prediction = self.model.predict(audio)

                if prediction:

                    score = max(
                        prediction.values()
                    )

                    if score > self.threshold:

                        print("Hey Jarvis detected!")

                        time.sleep(2)

                        return True

                # ==================================
                # 2. DOUBLE CLAP DETECTION
                # ==================================

                if self._is_clap(audio):

                    if self._double_clap_detected():

                        time.sleep(0.5)

                        return True