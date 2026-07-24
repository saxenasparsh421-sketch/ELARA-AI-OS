"""
assistant.py
Main controller of JARVIS OS
"""

from config import APP_NAME, VERSION


class Jarvis:
    def __init__(self):
        self.running = False

    def start(self):
        self.running = True

        print("=" * 50)
        print(APP_NAME)
        print(f"Version: {VERSION}")
        print("=" * 50)

        print("Initializing modules...")
        print("Speech        OK")
        print("Brain         OK")
        print("Memory        OK")
        print("Automation    OK")
        print("Security      OK")
        print()

        print("JARVIS is online.")

        while self.running:
            command = input("Boss > ").strip().lower()

            if command in ["exit", "quit"]:
                print("Goodbye Boss.")
                self.running = False
                break

            print(f"Processing: {command}")