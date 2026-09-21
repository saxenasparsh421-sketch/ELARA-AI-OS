"""
speech/whisper.py

JARVIS Speech To Text Engine
"""

import os
import string
import tempfile

import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel



class WhisperSTT:


    def __init__(self):

        self.model = None

        # Your Realtek microphone
        self.device = 1



    # -----------------------------
    # Load Whisper Model
    # -----------------------------

    def load(self):

        if self.model is None:

            print(
                "Loading Whisper Tiny (Multilingual)..."
            )


            self.model = WhisperModel(
                "tiny",
                device="cpu",
                compute_type="int8"
            )


            print(
                "Whisper Ready."
            )



    # -----------------------------
    # Listen
    # -----------------------------

    def listen(self, duration=5):


        self.load()


        print(
            "Listening..."
        )


        sample_rate = 16000



        try:

            audio = sd.rec(

                int(duration * sample_rate),

                samplerate=sample_rate,

                channels=1,

                dtype="int16",

                device=self.device

            )


            sd.wait()



        except Exception as e:


            print(
                "Microphone error:",
                e
            )

            return ""



        temp = os.path.join(

            tempfile.gettempdir(),

            "jarvis.wav"

        )



        write(

            temp,

            sample_rate,

            audio

        )



        # -----------------------------
        # Whisper Transcription
        # -----------------------------

        segments, _ = self.model.transcribe(

            temp,

            beam_size=5,

            language="en",

            vad_filter=True

        )



        text = ""



        for segment in segments:

            text += segment.text



        text = text.lower()



        text = text.translate(

            str.maketrans(

                "",

                "",

                string.punctuation

            )

        )



        text = text.strip()



        if len(text) < 2:

            return ""



        print(

            "You:",
            text

        )


        return text