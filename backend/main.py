from backend.ai_service import ask_ai, extract_city, extract_intent
from fastapi import FastAPI
from backend.weather_service import get_weather
from backend.location_service import get_location
from backend.forecast_service import get_forecast
from backend.intelligence_service import analyze_weather

app = FastAPI(title="WeatherGPT API")


@app.get("/")
def home():
    return {
        "message": "WeatherGPT API is running!"
    }


@app.get("/weather/{city}")
def weather(city: str):
    return get_weather(city)


@app.get("/location/{city}")
def location(city: str):
    return get_location(city)


@app.get("/forecast/{city}")
def forecast(city: str):
    location_data = get_location(city)

    if "error" in location_data:
        return location_data

    latitude = location_data["latitude"]
    longitude = location_data["longitude"]

    return get_forecast(latitude, longitude)


@app.get("/weather-analysis/{city}")
def weather_analysis(city: str):
    weather_data = get_weather(city)

    if "error" in weather_data:
        return weather_data

    analysis = analyze_weather(weather_data)

    return {
        "city": weather_data.get("city"),
        "country": weather_data.get("country"),
        "temperature": weather_data.get("temperature"),
        "feels_like": weather_data.get("feels_like"),
        "humidity": weather_data.get("humidity"),
        "weather": weather_data.get("weather"),
        "wind_speed": weather_data.get("wind_speed"),
        "analysis": analysis
    }
@app.get("/ask-ai")
def ask_ai_test(question: str):
    answer = ask_ai(question)

    return {
        "question": question,
        "answer": answer
    }

@app.get("/smart-weather")
def smart_weather(question: str):

    city = extract_city(question)

    if city == "UNKNOWN":
        return {
            "error": "I could not find a city in your question."
        }

    weather_data = get_weather(city)

    if "error" in weather_data:
        return weather_data

    answer = ask_ai(
        question=question,
        weather_data=weather_data
    )

    return {
        "question": question,
        "detected_city": city,
        "weather": weather_data,
        "answer": answer
    }

@app.get("/understand-question")
def understand_question(question: str):

    city = extract_city(question)
    intent = extract_intent(question)

    return {
        "question": question,
        "detected_city": city,
        "detected_intent": intent
    }