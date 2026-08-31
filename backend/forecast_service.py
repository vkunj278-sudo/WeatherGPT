import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_forecast(latitude, longitude):
    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params, timeout=15)

    if response.status_code != 200:
        return {
            "error": "Unable to get forecast data",
            "details": response.json()
        }

    data = response.json()

    forecast_list = []

    for item in data.get("list", []):
        forecast_list.append({
            "datetime": item.get("dt_txt"),
            "temperature": item["main"].get("temp"),
            "feels_like": item["main"].get("feels_like"),
            "humidity": item["main"].get("humidity"),
            "weather": item["weather"][0].get("description"),
            "wind_speed": item["wind"].get("speed"),
            "rain_3h": item.get("rain", {}).get("3h", 0)
        })

    return {
        "location": data.get("city", {}).get("name"),
        "forecast": forecast_list
    }