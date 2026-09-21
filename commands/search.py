import webbrowser
import urllib.parse


def handle_search(text):

    text = text.lower()

    if "search" not in text:
        return None


    query = text.split("search", 1)[1]


    if "google" in query:

        query = query.replace("google", "")
        
        query = query.replace("for", "")
        
        query = query.strip()

        if query:
            url = "https://www.google.com/search?q=" + urllib.parse.quote(query)

            webbrowser.open(url)

            return f"Searching Google for {query}, Boss."


    if "youtube" in query:

        query = query.replace("youtube", "")
        
        query = query.replace("for", "")
        
        query = query.strip()

        if query:
            url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)

            webbrowser.open(url)

            return f"Searching YouTube for {query}, Boss."


    return None