import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_location(city):
    url = "https://api.openweathermap.org/geo/1.0/direct"

    params = {
        "q": city,
        "limit": 1,
        "appid": API_KEY
    }

    response = requests.get(url, params=params, timeout=15)

    if response.status_code != 200:
        return {
            "error": "Unable to find location",
            "details": response.json()
        }

    data = response.json()

    if not data:
        return {
            "error": "Location not found"
        }

    location = data[0]

    return {
        "name": location.get("name"),
        "country": location.get("country"),
        "state": location.get("state"),
        "latitude": location.get("lat"),
        "longitude": location.get("lon")
    }