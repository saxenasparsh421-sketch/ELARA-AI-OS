import ctypes
import ctypes.wintypes
import threading


user32 = ctypes.windll.user32


MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_NOREPEAT = 0x4000

VK_F9 = 0x78
VK_S = 0x53


class GlobalHotkey:

    def __init__(
        self,
        pause_callback,
        standby_callback
    ):

        self.pause_callback = pause_callback
        self.standby_callback = standby_callback

    def start(self):

        def listen():

            PAUSE_ID = 1
            STANDBY_ID = 2

            # F9 = Pause / Resume
            user32.RegisterHotKey(
                None,
                PAUSE_ID,
                MOD_NOREPEAT,
                VK_F9
            )

            # Ctrl + Alt + S = Standby
            user32.RegisterHotKey(
                None,
                STANDBY_ID,
                MOD_CONTROL | MOD_ALT | MOD_NOREPEAT,
                VK_S
            )

            msg = ctypes.wintypes.MSG()

            while True:

                result = user32.GetMessageW(
                    ctypes.byref(msg),
                    None,
                    0,
                    0
                )

                if result == 0:
                    break

                if msg.message == 0x0312:

                    if msg.wParam == PAUSE_ID:

                        self.pause_callback()

                    elif msg.wParam == STANDBY_ID:

                        self.standby_callback()

        threading.Thread(
            target=listen,
            daemon=True
        ).start()