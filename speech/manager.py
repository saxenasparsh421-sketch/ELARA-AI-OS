import re

from speech.wakeword import WakeWordDetector
from speech.whisper import WhisperSTT
from speech.speaker import Speaker


class SpeechManager:

    def __init__(self):

        print("Initializing Speech Manager...")

        self.wakeword = None
        self.whisper = None
        self.speaker = None

    def _get_wakeword(self):

        if self.wakeword is None:
            print("Loading WakeWord...")
            self.wakeword = WakeWordDetector()

        return self.wakeword

    def _get_whisper(self):

        if self.whisper is None:
            print("Loading Whisper...")
            self.whisper = WhisperSTT()

        return self.whisper

    def _get_speaker(self):

        if self.speaker is None:
            print("Loading Speaker...")
            self.speaker = Speaker()

        return self.speaker

    def wait_for_wakeword(self):

        return self._get_wakeword().wait()

    def listen(self):

        return self._get_whisper().listen()

    def _clean_for_speech(self, text):

        if not text:
            return ""

        text = str(text)

        # Remove Markdown code blocks
        text = re.sub(
            r"```.*?```",
            " ",
            text,
            flags=re.DOTALL
        )

        # Remove Markdown headings
        text = re.sub(
            r"^\s*#{1,6}\s*",
            "",
            text,
            flags=re.MULTILINE
        )

        # Remove bold / italic markers
        text = text.replace("**", "")
        text = text.replace("__", "")
        text = text.replace("*", "")
        text = text.replace("_", "")

        # Remove bullet points at the beginning of lines
        text = re.sub(
            r"^\s*[-•]\s*",
            "",
            text,
            flags=re.MULTILINE
        )

        # Remove Markdown links but keep their visible text
        text = re.sub(
            r"\[([^\]]+)\]\([^)]+\)",
            r"\1",
            text
        )

        # Remove common technical symbols
        text = re.sub(
            r"[`~^|<>={}\[\]]",
            " ",
            text
        )

        # Convert slash to a natural spoken separator
        text = text.replace("/", " ")

        # Remove repeated punctuation
        text = re.sub(
            r"[.!?]{2,}",
            ".",
            text
        )

        # Remove excessive whitespace
        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    def speak(self, text):

        clean_text = self._clean_for_speech(text)

        if not clean_text:
            return

        self._get_speaker().speak(clean_text)