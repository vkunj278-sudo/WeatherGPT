from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


# =========================================================
# APP
# =========================================================

app = FastAPI(title="WeatherGPT API")


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "message": "WeatherGPT API is running!"
    }


# =========================================================
# CURRENT WEATHER
# =========================================================

@app.get("/weather/{city}")
def weather(city: str):
    return get_weather(city)


# =========================================================
# LOCATION
# =========================================================

@app.get("/location/{city}")
def location(city: str):
    return get_location(city)


# =========================================================
# FORECAST
# =========================================================

@app.get("/forecast/{city}")
def forecast(city: str):

    location_data = get_location(city)

    if "error" in location_data:
        return location_data

    latitude = location_data["latitude"]
    longitude = location_data["longitude"]

    return get_forecast(
        latitude,
        longitude
    )


# =========================================================
# WEATHER ANALYSIS
# =========================================================

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


# =========================================================
# AI TEST
# =========================================================

@app.get("/ask-ai")
def ask_ai_test(question: str):

    answer = ask_ai(question)

    return {
        "question": question,
        "answer": answer
    }


# =========================================================
# ALERTS
# =========================================================

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


# =========================================================
# SMART WEATHER
# =========================================================

@app.get("/smart-weather")
def smart_weather(
    question: str,
    session_id: str = "default"
):

    # -----------------------------------------------------
    # STEP 1: MEMORY
    # -----------------------------------------------------

    memory = get_conversation(session_id)

    # -----------------------------------------------------
    # STEP 2: UNDERSTAND QUESTION
    # -----------------------------------------------------

    understanding = understand_weather_question(
        question,
        memory
    )

    # Safety check
    if not isinstance(understanding, dict):
        return {
            "status": "error",
            "message": "Unable to understand the weather question."
        }

    city = understanding.get(
        "city",
        "UNKNOWN"
    )

    intent = understanding.get(
        "intent",
        "GENERAL_WEATHER"
    )

    time_period = understanding.get(
        "time",
        "UNKNOWN"
    )

    understanding_error = understanding.get("error")

    # -----------------------------------------------------
    # STEP 3: USE MEMORY CITY
    # -----------------------------------------------------

    if city == "UNKNOWN":

        if memory.get("city"):
            city = memory["city"]

        else:

            return {
                "status": "need_location",
                "question": question,
                "detected_intent": intent,
                "detected_time": time_period,
                "message": (
                    "Which city or location would you like "
                    "me to check?"
                )
            }

    # -----------------------------------------------------
    # STEP 4: SAVE MEMORY
    # -----------------------------------------------------

    save_conversation(
        session_id,
        city=city,
        intent=intent,
        time_period=time_period,
        last_question=question
    )

    # -----------------------------------------------------
    # STEP 5: DECIDE DATA SOURCE
    # -----------------------------------------------------

    data_source = decide_data_source(intent)

    weather_data = None
    forecast_data = None

    # -----------------------------------------------------
    # STEP 6: CURRENT WEATHER
    # -----------------------------------------------------

    if data_source == "current":

        weather_data = get_weather(city)

        if "error" in weather_data:
            return weather_data

    # -----------------------------------------------------
    # STEP 7: FORECAST
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # STEP 8: BOTH
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # STEP 9: INTELLIGENCE
    # -----------------------------------------------------

    intelligence = {
        "conditions": [],
        "severity": "normal",
        "recommendations": [],
        "warnings": []
    }

    # -----------------------------------------------------
    # CURRENT INTELLIGENCE
    # -----------------------------------------------------

    if weather_data and not forecast_data:

        condition_result = analyze_conditions(
            weather_data
        )

        conditions = condition_result.get(
            "conditions",
            []
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

    # -----------------------------------------------------
    # FORECAST INTELLIGENCE
    # -----------------------------------------------------

    elif forecast_data and not weather_data:

        condition_result = analyze_forecast_conditions(
            forecast_data
        )

        conditions = condition_result.get(
            "conditions",
            []
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

    # -----------------------------------------------------
    # COMBINED INTELLIGENCE
    # -----------------------------------------------------

    elif weather_data and forecast_data:

        current_result = analyze_conditions(
            weather_data
        )

        forecast_result = analyze_forecast_conditions(
            forecast_data
        )

        current_conditions = current_result.get(
            "conditions",
            []
        )

        forecast_conditions = forecast_result.get(
            "conditions",
            []
        )

        conditions = list(
            dict.fromkeys(
                current_conditions +
                forecast_conditions
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

    # -----------------------------------------------------
    # STEP 10: CREATE ALERTS
    # -----------------------------------------------------

    created_alerts = []

    for warning in intelligence["warnings"]:

        alert = create_alert(
            city=city,
            severity=intelligence["severity"],
            warning=warning,
            conditions=intelligence["conditions"]
        )

        created_alerts.append(alert)

    # -----------------------------------------------------
    # STEP 11: FINAL AI ANSWER
    # -----------------------------------------------------

    answer = ask_ai(
        question=question,
        weather_data=weather_data,
        forecast_data=forecast_data
    )

    # -----------------------------------------------------
    # STEP 12: FINAL RESPONSE
    # -----------------------------------------------------

    response = {
        "status": "success",
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

    if understanding_error:
        response["understanding_warning"] = understanding_error

    return response