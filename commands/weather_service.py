import requests

# ===================================
# CONFIG
# ===================================

API_KEY = "8c485033214354c22c410c677b09d410"

CITY = "Bareilly"
COUNTRY = "IN"


def get_weather(text):

    try:

        # ===================================
        # CURRENT WEATHER
        # ===================================

        weather_url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={CITY},{COUNTRY}"
            f"&appid={API_KEY}"
            f"&units=metric"
        )

        weather = requests.get(
            weather_url,
            timeout=10
        ).json()

        if str(weather.get("cod")) != "200":
            return "Boss I couldn't fetch the weather."

        lat = weather["coord"]["lat"]
        lon = weather["coord"]["lon"]

        # ===================================
        # AIR QUALITY
        # ===================================

        air_url = (
            f"https://api.openweathermap.org/data/2.5/air_pollution"
            f"?lat={lat}"
            f"&lon={lon}"
            f"&appid={API_KEY}"
        )

        air = requests.get(
            air_url,
            timeout=10
        ).json()

        # ===================================
        # WEATHER VALUES
        # ===================================

        temperature = round(weather["main"]["temp"])
        feels_like = round(weather["main"]["feels_like"])
        humidity = weather["main"]["humidity"]
        pressure = weather["main"]["pressure"]
        wind_speed = round(weather["wind"]["speed"] * 3.6)
        description = weather["weather"][0]["description"].capitalize()
        visibility = weather.get("visibility", 0) / 1000

        aqi = air["list"][0]["main"]["aqi"]

        aqi_text = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }.get(aqi, "Unknown")

        # ===================================
        # ADVICE
        # ===================================

        advice = []

        if humidity >= 75:
            advice.append("Carry a water bottle because humidity is high.")

        if temperature >= 35:
            advice.append("Avoid direct sunlight because it is very hot.")

        if wind_speed >= 20:
            advice.append("Be careful because the wind is strong.")

        if "rain" in description.lower():
            advice.append("Take an umbrella because rain may occur.")

        if aqi >= 4:
            advice.append("Wear a mask because air quality is poor.")

        if not advice:
            advice.append("The weather looks comfortable.")

        # ===================================
        # BASIC REPORT
        # ===================================

        reply = (
            f"Boss. "
            f"The current temperature is {temperature} degrees Celsius. "
            f"It feels like {feels_like} degrees. "
            f"The weather is {description}. "
            f"Humidity is {humidity} percent. "
            f"Wind speed is {wind_speed} kilometers per hour. "
            f"Pressure is {pressure} hectopascals. "
            f"Visibility is {visibility:.1f} kilometers. "
            f"Air quality is {aqi_text}."
        )

        # ===================================
        # GOING OUTSIDE MODE
        # ===================================

        if (
            "outside" in text.lower()
            or "going outside" in text.lower()
            or "going out" in text.lower()
            or "bahar" in text.lower()
        ):

            reply += " Since you are going outside. "

            reply += " ".join(advice)

        return reply

    except Exception as e:

        print("Weather Error:", e)

        return "Boss I couldn't connect to the weather service."