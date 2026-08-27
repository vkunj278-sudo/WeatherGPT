import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)


MODEL_NAME = "gemini-3.6-flash"


def ask_ai(question, weather_data=None, forecast_data=None):

    weather_context = ""

    if weather_data:
        weather_context += f"""
CURRENT WEATHER DATA:
{weather_data}
"""

    if forecast_data:
        weather_context += f"""
FORECAST DATA:
{forecast_data}
"""

    prompt = f"""
You are WeatherGPT, an intelligent conversational weather assistant.

USER QUESTION:
{question}

REAL WEATHER DATA:
{weather_context}

IMPORTANT RULES:

1. Use the provided weather data whenever it is available.
2. Never invent weather information.
3. If the required weather data is not available, clearly say so.
4. Give simple and natural answers.
5. Keep answers concise but useful.
6. Provide practical weather advice when appropriate.
7. If the user asks a weather-related question, prioritize the actual weather data.
8. Do not claim that you have live weather data unless it is provided to you.

Answer the user's question naturally.
"""

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        return response.text

    except Exception as e:

        error_text = str(e)

        if "503" in error_text or "UNAVAILABLE" in error_text:
            return (
                "Gemini is temporarily unavailable. "
                "Please try again in a few moments."
            )

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            return (
                "The Gemini API quota has temporarily been reached. "
                "Please try again later."
            )

        return "Sorry, I could not generate an AI response right now."


def understand_question(question):

    prompt = f"""
You are the query understanding system for WeatherGPT.

Analyze this user question:

"{question}"

Return the result in EXACTLY this format:

CITY: <city name or UNKNOWN>
INTENT: <one intent>
TIME: <one time period>

Allowed intents:

CURRENT_WEATHER
FORECAST
RAIN
TEMPERATURE
HUMIDITY
WIND
WEATHER_ADVICE
GENERAL_WEATHER

Allowed time periods:

NOW
TODAY
TOMORROW
THIS_WEEK
THIS_WEEKEND
FUTURE
UNKNOWN

Rules:

- Extract the city mentioned by the user.
- If no city is mentioned, use UNKNOWN.
- Determine the most appropriate weather intent.
- Determine the requested time period.
- Return ONLY the three lines.
- Do not provide explanations.

Example:

CITY: Ahmedabad
INTENT: RAIN
TIME: TOMORROW
"""

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        result = response.text.strip()

    except Exception as e:

        error_text = str(e)

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            return {
                "city": "UNKNOWN",
                "intent": "GENERAL_WEATHER",
                "time": "UNKNOWN",
                "error": "Gemini API quota has been reached."
            }

        if "503" in error_text or "UNAVAILABLE" in error_text:
            return {
                "city": "UNKNOWN",
                "intent": "GENERAL_WEATHER",
                "time": "UNKNOWN",
                "error": "Gemini is temporarily unavailable."
            }

        return {
            "city": "UNKNOWN",
            "intent": "GENERAL_WEATHER",
            "time": "UNKNOWN",
            "error": "Unable to understand the question."
        }

    city = "UNKNOWN"
    intent = "GENERAL_WEATHER"
    time_period = "UNKNOWN"

    for line in result.splitlines():

        line = line.strip()

        if line.startswith("CITY:"):
            city = line.replace("CITY:", "", 1).strip()

        elif line.startswith("INTENT:"):
            intent = line.replace("INTENT:", "", 1).strip().upper()

        elif line.startswith("TIME:"):
            time_period = line.replace("TIME:", "", 1).strip().upper()

    return {
        "city": city,
        "intent": intent,
        "time": time_period
    }