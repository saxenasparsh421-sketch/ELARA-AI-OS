import webbrowser


def handle_study(text):

    text = text.lower()

    if "activate study mode" in text or "activate the study mode" in text:

        webbrowser.open("https://www.pw.live")

        return "Study mode activated. Opening Physics Wallah. Happy studying Boss."

    return None