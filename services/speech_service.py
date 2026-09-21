from core.service import Service
from speech.manager import SpeechManager


class SpeechService(Service):

    def __init__(self):

        print("Initializing Speech Service...")

        self.manager = SpeechManager()

    def start(self):

        print("Speech Service Online.")

    def wait(self):

        return self.manager.wait_for_wakeword()

    def listen(self):

        return self.manager.listen()

    def speak(self, text):

        self.manager.speak(text)