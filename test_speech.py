from services.speech_service import SpeechService


def main():
    speech = SpeechService()
    speech.speak("Hello Boss. Speech system is online.")


if __name__ == "__main__":
    main()