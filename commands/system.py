import subprocess
import os
import webbrowser
import urllib.parse

# --------------------------
# Known websites
# --------------------------

WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "physics wallah": "https://www.pw.live",
    "pw": "https://www.pw.live",
    "chatgpt": "https://chatgpt.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
    "instagram": "https://www.instagram.com",
    "facebook": "https://www.facebook.com",
    "linkedin": "https://www.linkedin.com",
    "reddit": "https://www.reddit.com",
    "stackoverflow": "https://stackoverflow.com",
    "geeksforgeeks": "https://www.geeksforgeeks.org",
    "leetcode": "https://leetcode.com",
    "amazon": "https://www.amazon.in",
    "flipkart": "https://www.flipkart.com",
    "netflix": "https://www.netflix.com",
    "spotify": "https://open.spotify.com",
}


def execute(text):

    text = text.lower().strip()

    # ==========================================================
    # SEARCH YOUTUBE
    # Example:
    # Search YouTube for Python
    # ==========================================================

    if text.startswith("search youtube for"):

        query = text.replace(
            "search youtube for",
            ""
        ).strip()

        url = (
            "https://www.youtube.com/results?search_query="
            + urllib.parse.quote(query)
        )

        webbrowser.open(url)

        return f"Searching YouTube for {query}, Boss."

    # ==========================================================
    # PLAY ON YOUTUBE
    # Example:
    # Play Believer
    # ==========================================================

    if text.startswith("play "):

        query = text.replace(
            "play",
            ""
        ).strip()

        url = (
            "https://www.youtube.com/results?search_query="
            + urllib.parse.quote(query)
        )

        webbrowser.open(url)

        return f"Playing {query} on YouTube, Boss."

    # ==========================================================
    # OPEN WEBSITE
    # Example:
    # Open YouTube
    # Open Google
    # Open Netflix
    # Open Physics Wallah
    # ==========================================================

    if text.startswith("open "):

        site = text.replace(
            "open",
            ""
        ).strip()

        # Known websites
        if site in WEBSITES:

            webbrowser.open(
                WEBSITES[site]
            )

            return f"Opening {site.title()}, Boss."

        # Try .com automatically

        try:

            url = (
                "https://www."
                + site.replace(" ", "")
                + ".com"
            )

            webbrowser.open(url)

            return f"Opening {site.title()}, Boss."

        except Exception:
            pass

        # Google Search

        search = (
            "https://www.google.com/search?q="
            + urllib.parse.quote(site)
        )

        webbrowser.open(search)

        return (
            f"I couldn't find {site}. "
            f"Searching Google instead, Boss."
        )

    # ==========================================================
    # APPS
    # ==========================================================

    if "open chrome" in text:

        subprocess.Popen(
            "start chrome",
            shell=True
        )

        return "Opening Chrome, Boss."

    if (
        "open code" in text
        or
        "open visual studio code" in text
    ):

        subprocess.Popen(
            "code",
            shell=True
        )

        return "Opening Visual Studio Code."

    if "open explorer" in text:

        subprocess.Popen(
            "explorer",
            shell=True
        )

        return "Opening File Explorer."

    if "open downloads" in text:

        downloads = os.path.join(
            os.path.expanduser("~"),
            "Downloads"
        )

        subprocess.Popen(
            f'explorer "{downloads}"'
        )

        return "Opening Downloads."

    # ==========================================================
    # SYSTEM
    # ==========================================================

    if (
        "shutdown" in text
        or
        "shut down" in text
    ):

        subprocess.Popen(
            "shutdown /s /t 5",
            shell=True
        )

        return "Shutting down your computer in five seconds, Boss."

    if "restart" in text:

        subprocess.Popen(
            "shutdown /r /t 5",
            shell=True
        )

        return "Restarting your computer, Boss."

    return None