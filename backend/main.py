from fastapi import FastAPI

from backend.conversation_service import save_conversation, get_conversation
from backend.ai_service import ask_ai
from backend.understanding_service import understand_weather_question
from backend.router_service import decide_data_source
from backend.forecast_filter_service import filter_forecast

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
def smart_weather(
    question: str,
    session_id: str = "default"
):

    # Step 1: Get previous conversation information
    memory = get_conversation(session_id)

    # Step 2: Understand the current question using previous context
    understanding = understand_weather_question(
        question,
        memory
    )

    city = understanding["city"]
    intent = understanding["intent"]
    time_period = understanding["time"]

    # Step 3: If no city was detected, use previous conversation memory
    if city == "UNKNOWN":

        if "city" in memory:
            city = memory["city"]

        else:
            return {
                "status": "need_location",
                "question": question,
                "detected_intent": intent,
                "detected_time": time_period,
                "message": "Which city or location would you like me to check?"
            }

    # Step 4: Save current conversation information
    save_conversation(
        session_id,
        city=city,
        intent=intent,
        time_period=time_period,
        last_question=question
    )

    # Step 5: Decide which weather data is required
    data_source = decide_data_source(intent)

    weather_data = None
    forecast_data = None

    # Step 6: Current weather
    if data_source == "current":

        weather_data = get_weather(city)

        if "error" in weather_data:
            return weather_data

    # Step 7: Forecast
    elif data_source == "forecast":

        location_data = get_location(city)

        if "error" in location_data:
            return location_data

        forecast_data = get_forecast(
            location_data["latitude"],
            location_data["longitude"]
        )

        if "error" in forecast_data:
            return forecast_data

        # Filter forecast according to requested time
        forecast_data = filter_forecast(
            forecast_data,
            time_period
        )

    # Step 8: Current weather + forecast
    elif data_source == "both":

        weather_data = get_weather(city)

        if "error" in weather_data:
            return weather_data

        location_data = get_location(city)

        if "error" in location_data:
            return location_data

        forecast_data = get_forecast(
            location_data["latitude"],
            location_data["longitude"]
        )

        if "error" in forecast_data:
            return forecast_data

        # Filter forecast according to requested time
        forecast_data = filter_forecast(
            forecast_data,
            time_period
        )

    # Step 9: Generate final AI answer
    answer = ask_ai(
        question=question,
        weather_data=weather_data,
        forecast_data=forecast_data
    )

    # Step 10: Return complete response
    return {
        "question": question,
        "session_id": session_id,
        "detected_city": city,
        "detected_intent": intent,
        "detected_time": time_period,
        "data_source": data_source,
        "weather": weather_data,
        "forecast": forecast_data,
        "answer": answer
    }