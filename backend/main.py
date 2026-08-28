from fastapi import FastAPI

from backend.condition_service import (
    analyze_conditions,
    analyze_forecast_conditions
)

from backend.severity_service import determine_severity
from backend.recommendation_service import generate_recommendations
from backend.alert_service import generate_warnings
from backend.alert_manager import (
    create_alert,
    get_alerts,
    clear_alerts,
    resolve_alert
)

from backend.conversation_service import (
    save_conversation,
    get_conversation
)

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
@app.get("/alerts")
def alerts(
    city: str = None,
    status: str = None
):

    return {
        "alerts": get_alerts(
            city=city,
            status=status
        )
    }


@app.get("/alerts/{city}")
def city_alerts(city: str):

    return {
        "city": city,
        "alerts": get_alerts(city=city)
    }


@app.patch("/alerts/{alert_id}/resolve")
def resolve_alert_endpoint(alert_id: int):

    alert = resolve_alert(alert_id)

    if alert is None:

        return {
            "error": "Alert not found."
        }

    return {
        "message": "Alert resolved successfully.",
        "alert": alert
    }


@app.delete("/alerts")
def delete_alerts():

    return clear_alerts()

@app.get("/smart-weather")
def smart_weather(
    question: str,
    session_id: str = "default"
):

    # Step 1: Get previous conversation information
    memory = get_conversation(session_id)

    # Step 2: Understand current question using previous context
    understanding = understand_weather_question(
        question,
        memory
    )

    city = understanding["city"]
    intent = understanding["intent"]
    time_period = understanding["time"]

    # Step 3: Use previous city if current question has no city
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

    # Step 4: Save conversation
    save_conversation(
        session_id,
        city=city,
        intent=intent,
        time_period=time_period,
        last_question=question
    )

    # Step 5: Decide required data
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

        forecast_data = filter_forecast(
            forecast_data,
            time_period
        )

    # Step 9: Initialize intelligence
    intelligence = {
        "conditions": [],
        "severity": "unknown",
        "recommendations": [],
        "warnings": []
    }

    # Step 10: Current weather intelligence
    if weather_data and not forecast_data:

        condition_result = analyze_conditions(
            weather_data
        )

        conditions = condition_result["conditions"]

        severity = determine_severity(
            conditions
        )

        recommendations = generate_recommendations(
            conditions
        )

        warnings = generate_warnings(
            conditions,
            severity
        )

        intelligence = {
            "conditions": conditions,
            "severity": severity,
            "recommendations": recommendations,
            "warnings": warnings
        }

    # Step 11: Forecast intelligence
    elif forecast_data and not weather_data:

        condition_result = analyze_forecast_conditions(
            forecast_data
        )

        conditions = condition_result["conditions"]

        severity = determine_severity(
            conditions
        )

        recommendations = generate_recommendations(
            conditions
        )

        warnings = generate_warnings(
            conditions,
            severity
        )

        intelligence = {
            "conditions": conditions,
            "severity": severity,
            "recommendations": recommendations,
            "warnings": warnings
        }

    # Step 12: Combined current + forecast intelligence
    elif weather_data and forecast_data:

        current_result = analyze_conditions(
            weather_data
        )

        forecast_result = analyze_forecast_conditions(
            forecast_data
        )

        current_conditions = current_result["conditions"]
        forecast_conditions = forecast_result["conditions"]

        # Combine conditions and remove duplicates
        conditions = list(
            dict.fromkeys(
                current_conditions + forecast_conditions
            )
        )

        severity = determine_severity(
            conditions
        )

        recommendations = generate_recommendations(
            conditions
        )

        warnings = generate_warnings(
            conditions,
            severity
        )

        intelligence = {
            "conditions": conditions,
            "severity": severity,
            "recommendations": recommendations,
            "warnings": warnings
        }

    # Step 13: Create alerts from generated warnings
    created_alerts = []

    for warning in intelligence["warnings"]:

        alert = create_alert(
            city=city,
            severity=intelligence["severity"],
            warning=warning,
            conditions=intelligence["conditions"]
        )

        created_alerts.append(alert)

    # Step 14: Generate final AI answer
    answer = ask_ai(
        question=question,
        weather_data=weather_data,
        forecast_data=forecast_data
    )

    # Step 15: Return complete response
    return {
        "question": question,
        "session_id": session_id,
        "detected_city": city,
        "detected_intent": intent,
        "detected_time": time_period,
        "data_source": data_source,
        "weather": weather_data,
        "forecast": forecast_data,
        "intelligence": intelligence,
        "alerts": created_alerts,
        "answer": answer
    }