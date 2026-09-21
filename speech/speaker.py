import asyncio
import edge_tts
import pygame
import tempfile
import os


# ELARA voices
ENGLISH_VOICE = "en-IN-NeerjaNeural"
HINDI_VOICE = "hi-IN-SwaraNeural"

# Calm and comfortable delivery
RATE = "-8%"
VOLUME = "-5%"
PITCH = "-2Hz"


class Speaker:

    def __init__(self):
        pygame.mixer.init()

    def _select_voice(self, text: str):
        # If Hindi/Devanagari characters are present,
        # use the Indian Hindi female voice.
        for char in text:
            if "\u0900" <= char <= "\u097F":
                return HINDI_VOICE

        # Otherwise use Indian English female voice.
        return ENGLISH_VOICE

    async def _speak_async(self, text: str):

        print(f"ELARA: {text}")

        fd, temp_file = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)

        voice = self._select_voice(text)

        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=RATE,
            volume=VOLUME,
            pitch=PITCH
        )

        await communicate.save(temp_file)

        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)

        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

        try:
            os.remove(temp_file)
        except Exception:
            pass

    def speak(self, text: str):
        asyncio.run(self._speak_async(text))

    def close(self):
        pygame.mixer.quit()