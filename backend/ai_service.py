import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from google import genai


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

deepseek_client = None

if DEEPSEEK_API_KEY:
    deepseek_client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )

MODEL_NAME = "gemini-3.6-flash"

_client = None


def get_client():
    global _client

    if _client is not None:
        return _client

    if not API_KEY:
        return None

    _client = genai.Client(
        api_key=API_KEY
    )

    return _client


# =========================================================
# ERROR HANDLING
# =========================================================

def gemini_error_message(error):

    error_text = str(error)

    if (
        "429" in error_text
        or "RESOURCE_EXHAUSTED" in error_text
    ):
        return (
            "The Gemini API quota has temporarily "
            "been reached. Please try again later."
        )

    if (
        "503" in error_text
        or "UNAVAILABLE" in error_text
    ):
        return (
            "Gemini is temporarily unavailable. "
            "Please try again in a few moments."
        )

    if (
        "API key" in error_text
        or "API_KEY" in error_text
    ):
        return (
            "Gemini API key is missing or invalid. "
            "Please check the GEMINI_API_KEY setting."
        )

    return (
        "Sorry, I could not generate an AI response "
        "right now."
    )


# =========================================================
# AI ANSWER
# =========================================================
def ask_deepseek(prompt):

    if deepseek_client is None:
        return None

    try:
        response = deepseek_client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are WeatherGPT, a concise and reliable "
                        "weather assistant. Use only the weather data "
                        "provided in the prompt and never invent weather facts."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            thinking={
                "type": "disabled"
            },
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        print("DeepSeek error:", e)
        return None

def ask_ai(
    question,
    weather_data=None,
    forecast_data=None
):

    client = get_client()

    if client is None:

        return (
            "The Gemini API key is not configured. "
            "Please check GEMINI_API_KEY in your .env file."
        )

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
You are WeatherGPT, an intelligent conversational
weather assistant.

USER QUESTION:
{question}

REAL WEATHER DATA:
{weather_context}

IMPORTANT RULES:

1. Use the provided weather data whenever available.
2. Never invent weather information.
3. If required weather data is unavailable, clearly say so.
4. Give simple and natural answers.
5. Keep answers concise but useful.
6. Provide practical weather advice when appropriate.
7. Prioritize actual weather data.
8. Never claim to have live data unless it is provided.
9. If forecast data is provided, use it for forecast questions.
10. If alerts or warnings are present in the provided data,
    explain them clearly.

Answer naturally.
"""

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        text = getattr(
            response,
            "text",
            None
        )

        if text:
            return text.strip()

        return (
            "I received the weather information, "
            "but could not generate a readable answer."
        )

    except Exception as e:

        error_text = str(e)

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "503" in error_text
            or "UNAVAILABLE" in error_text
        ):

            deepseek_answer = ask_deepseek(prompt)

            if deepseek_answer:
                return deepseek_answer

            return (
                "The AI services are temporarily unavailable. "
                "Please try again later."
            )

        return (
            "Sorry, I could not generate an AI response right now."
        )


# =========================================================
# CITY EXTRACTION
# =========================================================

def extract_city(question):

    if not question:
        return "UNKNOWN"

    text = question.strip()

    # Common phrases:
    # "weather in Ahmedabad"
    # "weather at Ahmedabad"
    # "forecast for Ahmedabad"

    pattern = re.search(
        r"\b(?:in|at|for|near)\s+"
        r"([A-Za-z][A-Za-z .'-]{1,60}?)"
        r"(?:\?|$|,|\s+tomorrow|\s+today|\s+this|\s+now)",
        text,
        re.IGNORECASE
    )

    if pattern:

        city = pattern.group(1).strip(
            " .,'\""
        )

        # Remove common trailing weather words
        city = re.sub(
            r"\s+(weather|forecast|temperature|rain)$",
            "",
            city,
            flags=re.IGNORECASE
        )

        if city:
            return city.title()

    # Direct common Indian city detection.
    known_cities = [
        "Ahmedabad",
        "Mumbai",
        "Delhi",
        "New Delhi",
        "Bengaluru",
        "Bangalore",
        "Chennai",
        "Hyderabad",
        "Pune",
        "Kolkata",
        "Surat",
        "Vadodara",
        "Rajkot",
        "Jaipur",
        "Lucknow",
        "Kanpur",
        "Indore",
        "Bhopal",
        "Nagpur",
        "Patna",
        "Ranchi",
        "Noida",
        "Gurugram",
        "Chandigarh",
        "Amritsar",
        "Nashik",
        "Thane",
        "Mysuru",
        "Mysore"
    ]

    lower_text = text.lower()

    for city in sorted(
        known_cities,
        key=len,
        reverse=True
    ):

        if re.search(
            r"\b"
            + re.escape(city.lower())
            + r"\b",
            lower_text
        ):
            return city

    return "UNKNOWN"


# =========================================================
# TIME DETECTION
# =========================================================

def detect_time(question):

    text = question.lower()

    if re.search(
        r"\bnow\b|\bcurrently\b|\bright now\b",
        text
    ):
        return "NOW"

    if "tomorrow" in text:
        return "TOMORROW"

    if "today" in text:
        return "TODAY"

    if (
        "this weekend" in text
        or "weekend" in text
    ):
        return "THIS_WEEKEND"

    if (
        "this week" in text
        or "weekly" in text
        or "week" in text
    ):
        return "THIS_WEEK"

    if (
        "next week" in text
        or "future" in text
    ):
        return "FUTURE"

    return "UNKNOWN"


# =========================================================
# INTENT DETECTION
# =========================================================

def detect_intent(question):

    text = question.lower()

    if any(
        word in text
        for word in [
            "rain",
            "raining",
            "rainfall",
            "shower"
        ]
    ):
        return "RAIN"

    if any(
        word in text
        for word in [
            "temperature",
            "hot",
            "cold",
            "heat"
        ]
    ):
        return "TEMPERATURE"

    if any(
        word in text
        for word in [
            "humidity",
            "humid"
        ]
    ):
        return "HUMIDITY"

    if any(
        word in text
        for word in [
            "wind",
            "windy"
        ]
    ):
        return "WIND"

    if any(
        word in text
        for word in [
            "forecast",
            "tomorrow",
            "next week",
            "this week",
            "weekend"
        ]
    ):
        return "FORECAST"

    if any(
        word in text
        for word in [
            "should i",
            "can i",
            "advice",
            "recommend",
            "wear",
            "carry"
        ]
    ):
        return "WEATHER_ADVICE"

    if any(
        word in text
        for word in [
            "weather",
            "condition",
            "conditions"
        ]
    ):
        return "CURRENT_WEATHER"

    return "GENERAL_WEATHER"


# =========================================================
# QUESTION UNDERSTANDING
# =========================================================

def understand_question(
    question,
    conversation_context=None
):

    if conversation_context is None:
        conversation_context = {}

    city = extract_city(question)

    intent = detect_intent(question)

    time_period = detect_time(question)

    # -----------------------------------------------------
    # MEMORY FALLBACK
    # -----------------------------------------------------

    if city == "UNKNOWN":

        previous_city = conversation_context.get(
            "city"
        )

        if previous_city:
            city = previous_city

    if intent == "GENERAL_WEATHER":

        previous_intent = conversation_context.get(
            "intent"
        )

        if previous_intent:
            intent = previous_intent

    if time_period == "UNKNOWN":

        previous_time = conversation_context.get(
            "time"
        )

        if previous_time:
            time_period = previous_time

    # -----------------------------------------------------
    # Common questions are handled locally.
    # This avoids an unnecessary Gemini call.
    # -----------------------------------------------------

    if (
        city != "UNKNOWN"
        and intent != "GENERAL_WEATHER"
        and time_period != "UNKNOWN"
    ):

        return {
            "city": city,
            "intent": intent,
            "time": time_period
        }

    # -----------------------------------------------------
    # If the question is ambiguous, use Gemini.
    # -----------------------------------------------------

    client = get_client()

    if client is None:

        return {
            "city": city,
            "intent": intent,
            "time": time_period,
            "error": (
                "Gemini API key is not configured."
            )
        }

    previous_city = conversation_context.get(
        "city",
        "UNKNOWN"
    )

    previous_intent = conversation_context.get(
        "intent",
        "UNKNOWN"
    )

    previous_time = conversation_context.get(
        "time",
        "UNKNOWN"
    )

    previous_question = conversation_context.get(
        "last_question",
        "NONE"
    )

    prompt = f"""
You are the query understanding system for WeatherGPT.

PREVIOUS CONVERSATION:

City:
{previous_city}

Intent:
{previous_intent}

Time:
{previous_time}

Previous question:
{previous_question}

CURRENT QUESTION:
"{question}"

Return EXACTLY:

CITY: <city or UNKNOWN>
INTENT: <intent>
TIME: <time>

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

Return ONLY the three lines.
"""

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        result = getattr(
            response,
            "text",
            ""
        ).strip()

    except Exception as error:

        return {
            "city": city,
            "intent": intent,
            "time": time_period,
            "error": gemini_error_message(error)
        }

    ai_city = "UNKNOWN"
    ai_intent = "GENERAL_WEATHER"
    ai_time = "UNKNOWN"

    for line in result.splitlines():

        line = line.strip()

        if line.startswith("CITY:"):

            ai_city = line.replace(
                "CITY:",
                "",
                1
            ).strip()

        elif line.startswith("INTENT:"):

            ai_intent = line.replace(
                "INTENT:",
                "",
                1
            ).strip().upper()

        elif line.startswith("TIME:"):

            ai_time = line.replace(
                "TIME:",
                "",
                1
            ).strip().upper()

    return {
        "city": (
            ai_city
            if ai_city
            else city
        ),
        "intent": (
            ai_intent
            if ai_intent
            else intent
        ),
        "time": (
            ai_time
            if ai_time
            else time_period
        )
    }