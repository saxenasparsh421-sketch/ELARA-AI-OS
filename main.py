from __future__ import annotations

import threading
import time

from assistant import Jarvis
from gui.dashboard import ELARADashboard


def start_elara_os():
    try:
        print("[ELARA OS] Starting ELARA OS...")

        jarvis = Jarvis()

        print("[ELARA OS] ELARA OS initialized.")

        jarvis.start()

    except Exception as error:
        print("[ELARA OS ERROR]", error)


def start_clap_listener():
    try:
        from clap_listener import main as clap_main

        print("[ELARA CLAP] Starting double clap listener...")

        clap_main()

    except Exception as error:
        print("[ELARA CLAP ERROR]", error)


def main():
    print("=" * 60)
    print("              ELARA SYSTEM")
    print("=" * 60)

    # ----------------------------------------------------------
    # ELARA OS
    # ----------------------------------------------------------

    os_thread = threading.Thread(
        target=start_elara_os,
        daemon=True,
        name="ELARA-OS",
    )

    os_thread.start()

    # ----------------------------------------------------------
    # Give OS a moment to initialize
    # ----------------------------------------------------------

    time.sleep(0.5)

    # ----------------------------------------------------------
    # Double Clap Listener
    # ----------------------------------------------------------

    clap_thread = threading.Thread(
        target=start_clap_listener,
        daemon=True,
        name="ELARA-Clap-Listener",
    )

    clap_thread.start()

    # ----------------------------------------------------------
    # ELARA Dashboard
    # ----------------------------------------------------------

    print("[ELARA GUI] Starting ELARA Dashboard...")

    dashboard = ELARADashboard()

    dashboard.run()


if __name__ == "__main__":
    main()