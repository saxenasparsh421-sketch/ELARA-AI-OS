from commands.weather_service import get_weather


def handle_weather(text):

    text = text.lower()

    weather_keywords = [
        "weather",
        "temperature",
        "forecast",
        "humidity",
        "rain",
        "aqi",
        "outside",
        "going outside",
        "going out",
        "bahar",
        "baarish",
        "mausam",
    ]

    for word in weather_keywords:

        if word in text:

            return get_weather(text)

    return None