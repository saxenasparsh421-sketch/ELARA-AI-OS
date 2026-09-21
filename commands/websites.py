import webbrowser


def handle_websites(text):

    text = text.lower()

    # YouTube
    if "youtube" in text:
        webbrowser.open("https://youtube.com")
        return "Opening YouTube, Boss."

    # Physics Wallah
    if "physics wallah" in text or "pw" in text:
        webbrowser.open("https://www.pw.live")
        return "Opening Physics Wallah, Boss."

    # Google
    if "google" in text:
        webbrowser.open("https://google.com")
        return "Opening Google, Boss."

    # ChatGPT
    if "chatgpt" in text:
        webbrowser.open("https://chat.openai.com")
        return "Opening ChatGPT, Boss."

    # Gmail
    if "gmail" in text or "mail" in text:
        webbrowser.open("https://mail.google.com")
        return "Opening Gmail, Boss."

    return None