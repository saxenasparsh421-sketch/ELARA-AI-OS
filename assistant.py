"""
assistant.py
Main controller of ELARA OS
"""

import time

from config import APP_NAME, VERSION

from core.kernel import Kernel

from utils.hotkey import GlobalHotkey

from services.speech_service import SpeechService
from services.brain_service import BrainService

from utils.timer import Timer

from commands.router import route

from elara_os.chat_bridge import ELARAOSChatBridge


class Jarvis:

    def __init__(self):

        self.kernel = Kernel()

        self.paused = False
        self.standby = False

        # Shared ELARA OS chat storage
        self.chat_bridge = ELARAOSChatBridge()

    def toggle_pause(self):

        self.paused = not self.paused

        speech = self.kernel.get("speech")

        if self.paused:

            print("\n[ELARA PAUSED]\n")

            speech.speak(
                "ELARA paused Boss."
            )

        else:

            print("\n[ELARA RESUMED]\n")

            speech.speak(
                "ELARA resumed Boss."
            )

    def enter_standby(self):

        self.standby = True

        print("\n[ELARA STANDBY]\n")

        speech = self.kernel.get("speech")

        speech.speak(
            "Entering standby mode Boss."
        )

    def toggle_standby(self):

        if self.standby:

            self.exit_standby()

        else:

            self.enter_standby()

    def exit_standby(self):

        self.standby = False

        print("\n[ELARA STANDBY OFF]\n")

        speech = self.kernel.get("speech")

        speech.speak(
            "Welcome back Boss."
        )

    def save_boss_message(self, text):

        try:

            message_id = self.chat_bridge.save_boss_message(
                text
            )

            print(
                f"[ELARA CHAT] Boss message saved: {message_id}"
            )

            return message_id

        except Exception as error:

            print(
                f"[ELARA CHAT] Failed to save Boss message: {error}"
            )

            return None

    def save_elara_message(self, text):

        try:

            message_id = self.chat_bridge.save_elara_message(
                text
            )

            print(
                f"[ELARA CHAT] ELARA message saved: {message_id}"
            )

            return message_id

        except Exception as error:

            print(
                f"[ELARA CHAT] Failed to save ELARA message: {error}"
            )

            return None

    def start(self):

        print("=" * 50)
        print(APP_NAME)
        print(f"Version: {VERSION}")
        print("=" * 50)

        print("\nRegistering services...\n")

        timer = Timer()

        self.kernel.register(
            "speech",
            SpeechService()
        )

        print(
            f"[TIME] Speech Loaded: {timer.stop()}s"
        )

        timer = Timer()

        self.kernel.register(
            "brain",
            BrainService()
        )

        print(
            f"[TIME] Brain Loaded: {timer.stop()}s"
        )

        timer = Timer()

        self.kernel.start()

        print(
            f"[TIME] Services Started: {timer.stop()}s"
        )

        speech = self.kernel.get("speech")

        brain = self.kernel.get("brain")

        hotkey = GlobalHotkey(
            self.toggle_pause,
            self.toggle_standby
        )

        hotkey.start()

        print("\nAll services are online.\n")

        speech.speak(
            "ELARA is online Boss."
        )

        time.sleep(1)

        while True:

            if self.paused:

                time.sleep(0.2)

                continue

            if self.standby:

                time.sleep(0.2)

                continue

            print(
                "\nWaiting for wake word...\n"
            )

            speech.wait()

            print(
                "Wake word detected!"
            )

            if self.standby:

                print(
                    "\n[ELARA STANDBY - WAKE IGNORED]\n"
                )

                continue

            speech.speak(
                "Welcome back Boss."
            )

            time.sleep(1)

            missed_commands = 0

            while True:

                if self.paused:

                    break

                if self.standby:

                    print(
                        "\n[ELARA STANDBY - LISTENING STOPPED]\n"
                    )

                    break

                print(
                    "\nListening...\n"
                )

                text = speech.listen()

                if self.standby:

                    print(
                        "\n[ELARA STANDBY - COMMAND IGNORED]\n"
                    )

                    break

                if text:

                    lower = text.lower()

                    if (
                        "activate stand by" in lower
                        or "stand by mode" in lower
                        or "go stand by" in lower
                    ):

                        self.enter_standby()

                        break

                if not text:

                    missed_commands += 1

                    if missed_commands >= 5:

                        self.enter_standby()

                        time.sleep(1)

                        break

                    continue

                missed_commands = 0

                print(
                    f"\nYou: {text}"
                )

                # -------------------------------------------------
                # SAVE BOSS MESSAGE
                # -------------------------------------------------

                self.save_boss_message(
                    text
                )

                # -------------------------------------------------
                # COMMAND ROUTER
                # -------------------------------------------------

                response = route(
                    text,
                    speech
                )

                if response:

                    print(
                        f"\nELARA: {response}"
                    )

                    # Save ELARA response
                    self.save_elara_message(
                        response
                    )

                    speech.speak(
                        response
                    )

                    time.sleep(1)

                    continue

                # -------------------------------------------------
                # AI BRAIN
                # -------------------------------------------------

                print(
                    "\nThinking..."
                )

                response = brain.think(
                    text
                )

                if response:

                    print(
                        f"\nELARA: {response}"
                    )

                    # Save ELARA response
                    self.save_elara_message(
                        response
                    )

                    speech.speak(
                        response
                    )

                    time.sleep(1)

                else:

                    fallback = (
                        "I did not understand that Boss."
                    )

                    self.save_elara_message(
                        fallback
                    )

                    speech.speak(
                        fallback
                    )

                    time.sleep(1)