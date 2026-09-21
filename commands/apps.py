import subprocess


def handle_apps(text):

    text = text.lower()

    # Chrome / Browser
    if "chrome" in text or "browser" in text:
        subprocess.Popen("start chrome", shell=True)
        return "Opening Chrome, Boss."

    # VS Code
    if "code" in text or "visual studio" in text:
        subprocess.Popen("code", shell=True)
        return "Opening Visual Studio Code, Boss."

    # Calculator
    if "calculator" in text or "calc" in text:
        subprocess.Popen("calc", shell=True)
        return "Opening Calculator, Boss."

    # Notepad
    if "notepad" in text:
        subprocess.Popen("notepad", shell=True)
        return "Opening Notepad, Boss."

    return None