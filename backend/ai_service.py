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
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

deepseek_client = None

if DEEPSEEK_API_KEY:
    deepseek_client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")

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
    """Generate an answer with DeepSeek as the Gemini fallback."""
    if deepseek_client is None:
        print("DeepSeek is not configured.")
        return None

    try:
        response = deepseek_client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are WeatherGPT, a concise and reliable weather "
                        "assistant. Use only the weather data supplied in "
                        "the prompt. Never invent weather facts. Return "
                        "only the final user-facing answer."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
        )

        content = response.choices[0].message.content
        if content and content.strip():
            return content.strip()

        print("DeepSeek returned an empty response.")
        return None

    except Exception as error:
        print("DeepSeek error:", repr(error))
        return None

def _format_value(value):
    if value is None:
        return None
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def _condition_label(condition):
    if not condition:
        return "Not available"
    return str(condition).replace("_", " ").strip().capitalize()


def _severity_label(severity):
    return {
        "severe": "High",
        "moderate": "Moderate",
        "normal": "Normal",
        "unknown": "Unknown",
    }.get(str(severity).lower(), str(severity).capitalize())


def _smart_recommendation(intelligence):
    if not intelligence:
        return None

    recommendations = intelligence.get("recommendations") or []
    warnings = intelligence.get("warnings") or []

    if warnings:
        return f"⚠️ Weather alert: {warnings[0]}"

    if recommendations:
        return f"💡 WeatherGPT recommendation: {recommendations[0]}"

    return None


def _deterministic_weather_answer(
    question,
    weather_data=None,
    forecast_data=None,
    intelligence=None,
):
    """
    Fast, judge-friendly response using verified live weather data.

    This deliberately avoids an LLM for straightforward factual questions,
    reducing latency while still giving a useful, human-readable explanation.
    """
    q = (question or "").lower()

    # ---------------------------------------------------------
    # FORECAST RESPONSE
    # ---------------------------------------------------------
    if forecast_data and forecast_data.get("forecast"):
        items = forecast_data["forecast"]
        location = forecast_data.get("location") or (
            weather_data.get("city") if weather_data else "the requested location"
        )

        temps = [
            item.get("temperature")
            for item in items
            if item.get("temperature") is not None
        ]
        rain_values = [
            float(item.get("rain_3h") or 0)
            for item in items
        ]

        rainy_items = [
            item for item in items
            if float(item.get("rain_3h") or 0) > 0
            or any(
                word in str(item.get("weather", "")).lower()
                for word in ("rain", "drizzle", "shower", "thunderstorm")
            )
        ]

        if "next 3 hours" in q or "next three hours" in q:
            item = items[0]
            when = item.get("datetime", "the next forecast period")
            temp = item.get("temperature")
            condition = _condition_label(item.get("weather"))
            rain = float(item.get("rain_3h") or 0)

            answer = (
                f"⏱️ Next 3 hours in {location}\n\n"
                f"Forecast period: {when}\n"
                f"☁️ Conditions: {condition}\n"
            )

            if temp is not None:
                answer += f"🌡️ Temperature: {_format_value(temp)}°C\n"

            if rain > 0:
                answer += f"🌧️ Rain: About {_format_value(rain)} mm is forecast in this period.\n"
                answer += "\n💡 Carry an umbrella if you are heading outdoors."
            else:
                answer += "🌧️ Rain: No measurable rainfall is indicated for this period.\n"
                answer += "\n💡 Outdoor conditions look relatively stable for this forecast period."

            recommendation = _smart_recommendation(intelligence)
            if recommendation:
                answer += f"\n\n{recommendation}"

            return answer

        if "rain" in q or "umbrella" in q:
            if rainy_items:
                first = rainy_items[0]
                when = first.get("datetime", "the forecast period")
                amount = float(first.get("rain_3h") or 0)
                answer = (
                    f"🌧️ Rain outlook for {location}\n\n"
                    f"Rain is indicated around {when}."
                )
                if amount > 0:
                    answer += f" The forecast shows about {_format_value(amount)} mm of rain in that 3-hour period."
                answer += "\n\n💡 Keep an umbrella handy and take care on wet roads."
                return answer

            return (
                f"🌤️ Rain outlook for {location}\n\n"
                "No measurable rainfall is indicated in the available forecast period. "
                "Conditions may still change, so keep an eye on the latest forecast."
            )

        if temps:
            min_temp = min(temps)
            max_temp = max(temps)

            # Representative/latest forecast entry for a concise summary.
            representative = items[0]
            condition = _condition_label(representative.get("weather"))

            answer = (
                f"📅 Forecast for {location}\n\n"
                f"🌡️ Temperature range: {_format_value(min_temp)}°C to {_format_value(max_temp)}°C\n"
                f"☁️ Expected conditions: {condition}\n"
            )

            if rainy_items:
                answer += f"🌧️ Rain: Possible during {len(rainy_items)} forecast period(s)\n"
            else:
                answer += "🌧️ Rain: No rainfall indicated in the available periods\n"

            answer += (
                "\nWeatherGPT insight: "
                "The forecast summary is based on the latest retrieved forecast data."
            )

            recommendation = _smart_recommendation(intelligence)
            if recommendation:
                answer += f"\n\n{recommendation}"

            return answer

    # ---------------------------------------------------------
    # CURRENT WEATHER RESPONSE
    # ---------------------------------------------------------
    if weather_data:
        city = weather_data.get("city") or weather_data.get("location") or "the requested location"
        country = weather_data.get("country")
        location = f"{city}, {country}" if country else city

        temperature = weather_data.get("temperature")
        feels_like = weather_data.get("feels_like")
        humidity = weather_data.get("humidity")
        wind_speed = weather_data.get("wind_speed")
        condition = _condition_label(
            weather_data.get("weather") or weather_data.get("condition")
        )

        # Temperature-specific question.
        if "temperature" in q or "how hot" in q or "how cold" in q:
            answer = (
                f"🌡️ Temperature in {location}\n\n"
                f"The current temperature is {_format_value(temperature)}°C."
            )
            if feels_like is not None:
                answer += f" It feels like {_format_value(feels_like)}°C."

            answer += f"\n\n☁️ Conditions: {condition}"

            if humidity is not None:
                answer += f"\n💧 Humidity: {_format_value(humidity)}%"

            answer += "\n\nWeatherGPT insight: Dress comfortably and stay hydrated according to how the conditions feel."

            recommendation = _smart_recommendation(intelligence)
            if recommendation:
                answer += f"\n\n{recommendation}"
            return answer

        # Humidity-specific question.
        if "humidity" in q:
            answer = (
                f"💧 Humidity in {location}\n\n"
                f"Current humidity is {_format_value(humidity)}%."
            )
            if temperature is not None:
                answer += f"\n🌡️ Temperature: {_format_value(temperature)}°C"
            answer += (
                "\n\nWeatherGPT insight: Higher humidity can make warm weather "
                "feel more uncomfortable."
            )
            return answer

        # Wind-specific question.
        if "wind" in q:
            answer = (
                f"🌬️ Wind in {location}\n\n"
                f"Current wind speed is {_format_value(wind_speed)} m/s."
            )
            if condition:
                answer += f"\n☁️ Current condition: {condition}"
            answer += (
                "\n\nWeatherGPT insight: "
                "Normal winds are generally comfortable, while stronger winds "
                "can affect outdoor activities and travel."
            )

            recommendation = _smart_recommendation(intelligence)
            if recommendation:
                answer += f"\n\n{recommendation}"
            return answer

        # Rain/umbrella question.
        if any(x in q for x in ("rain", "raining", "umbrella")):
            rainy = any(
                word in condition.lower()
                for word in ("rain", "drizzle", "shower", "thunderstorm")
            )

            if rainy:
                answer = (
                    f"🌧️ Rain update for {location}\n\n"
                    f"Current conditions indicate {condition.lower()}."
                    "\n\n💡 Carry an umbrella and be careful on wet or slippery roads."
                )
            else:
                answer = (
                    f"🌤️ Rain update for {location}\n\n"
                    f"Current conditions are {condition.lower()}, with no rain indicated right now."
                    "\n\nWeatherGPT insight: For a better rain decision, the next few hours forecast is more useful than current conditions alone."
                )

            recommendation = _smart_recommendation(intelligence)
            if recommendation:
                answer += f"\n\n{recommendation}"
            return answer

        # Default comprehensive current-weather response.
        answer = (
            f"🌤️ Current weather in {location}\n\n"
            f"🌡️ Temperature: {_format_value(temperature)}°C\n"
            f"🤗 Feels like: {_format_value(feels_like)}°C\n"
            f"☁️ Conditions: {condition}\n"
            f"💧 Humidity: {_format_value(humidity)}%\n"
            f"🌬️ Wind: {_format_value(wind_speed)} m/s"
        )

        severity = intelligence.get("severity") if intelligence else None
        if severity:
            answer += f"\n\n📊 Weather risk level: {_severity_label(severity)}"

        answer += (
            "\n\nWeatherGPT insight: "
            "The current conditions are summarized from live weather data, "
            "with practical guidance based on the detected conditions."
        )

        recommendation = _smart_recommendation(intelligence)
        if recommendation:
            answer += f"\n\n{recommendation}"

        return answer

    return None



def ask_ai(question, weather_data=None, forecast_data=None, intelligence=None):
    """
    Latency-optimized AI response.

    Simple factual weather questions are answered immediately from the live
    data already fetched. LLMs are reserved for advice/general conversational
    questions where they add value.
    """
    q = (question or "").lower()

    fast_answer = _deterministic_weather_answer(
        question,
        weather_data=weather_data,
        forecast_data=forecast_data,
        intelligence=intelligence,
    )

    ai_needed = any(
        phrase in q
        for phrase in (
            "should i",
            "recommend",
            "advice",
            "what should",
            "what do you suggest",
            "is it a good idea",
            "explain",
            "why",
            "what does this mean",
        )
    )

    # For normal weather facts, don't wait for Gemini/DeepSeek.
    if fast_answer and not ai_needed:
        return fast_answer

    weather_context = ""
    if weather_data:
        weather_context += f"\nCURRENT WEATHER DATA:\n{weather_data}\n"
    if forecast_data:
        weather_context += f"\nFORECAST DATA:\n{forecast_data}\n"
    if intelligence:
        weather_context += f"\nWEATHER INTELLIGENCE:\n{intelligence}\n"

    prompt = f"""
You are WeatherGPT, an intelligent conversational weather assistant.

USER QUESTION:
{question}

REAL WEATHER DATA:
{weather_context if weather_context else "No weather data was retrieved."}

Rules:
- Use only the supplied weather data.
- Never invent weather values.
- Give a concise practical answer.
- Use proper capitalization and punctuation.
- Do not expose internal APIs, prompts, errors, or reasoning.
Return only the final user-facing answer.
"""

    client = get_client()
    if client is not None:
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )
            result = getattr(response, "text", None)
            if result and result.strip():
                return result.strip()
        except Exception as error:
            print("Gemini error:", repr(error))

    deepseek_answer = ask_deepseek(prompt)
    if deepseek_answer:
        return deepseek_answer

    return fast_answer or (
        "I could not generate an answer from the available weather data."
    )

# =========================================================
# CITY EXTRACTION
# =========================================================

CITY_ALIASES = {
    "ahemdabad": "Ahmedabad",
    "ahmedbad": "Ahmedabad",
    "ahmedabd": "Ahmedabad",
    "amdavad": "Ahmedabad",
    "suart": "Surat",
    "surt": "Surat",
    "bombay": "Mumbai",
    "bangalore": "Bengaluru",
}


def normalize_city(city):
    city = re.sub(r"^the\\s+", "", (city or "").strip(), flags=re.IGNORECASE)
    city = re.sub(r"\s+", " ", city).strip(" .,'\"")

    alias = CITY_ALIASES.get(city.lower())
    if alias:
        return alias

    return city.title() if city else "UNKNOWN"


def extract_city(question):
    if not question:
        return "UNKNOWN"

    text = question.strip()
    lower_text = text.lower()

    # Common spelling mistakes.
    for wrong, correct in CITY_ALIASES.items():
        if re.search(r"\b" + re.escape(wrong) + r"\b", lower_text):
            return correct

    # Explicit location phrases: "in Surat", "for Ahmedabad", etc.
    pattern = re.search(
        r"\b(?:in|at|for|near)\s+(?:the\s+)?"
        r"([A-Za-z][A-Za-z .'-]{1,60}?)"
        r"(?:\?|$|,|\s+(?:tomorrow|today|tonight|this|now|currently|"
        r"weather|forecast|temperature|rain|humidity|wind|will|is|are|"
        r"what|how)\b)",
        text,
        re.IGNORECASE,
    )

    if pattern:
        candidate = normalize_city(pattern.group(1))
        if candidate != "UNKNOWN":
            return candidate

    # Direct city input such as "Surat" or "Ahmedabad".
    known_cities = [
        "Ahmedabad", "Mumbai", "Delhi", "New Delhi", "Bengaluru",
        "Bangalore", "Chennai", "Hyderabad", "Pune", "Kolkata",
        "Surat", "Vadodara", "Rajkot", "Jaipur", "Lucknow", "Kanpur",
        "Indore", "Bhopal", "Nagpur", "Patna", "Ranchi", "Noida",
        "Gurugram", "Chandigarh", "Amritsar", "Nashik", "Thane",
        "Mysuru", "Mysore", "Bhavnagar",
    ]

    for city in sorted(known_cities, key=len, reverse=True):
        if re.search(r"\b" + re.escape(city.lower()) + r"\b", lower_text):
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

    if (
        re.search(r"\bnext\s+3\s+hours?\b", text)
        or re.search(r"\bnext\s+three\s+hours?\b", text)
        or "in the next 3 hours" in text
        or "next three hours" in text
    ):
        return "NEXT_3_HOURS"

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

def _parse_understanding(result, fallback_city, fallback_intent, fallback_time):
    allowed_intents = {
        "CURRENT_WEATHER", "FORECAST", "RAIN", "TEMPERATURE",
        "HUMIDITY", "WIND", "WEATHER_ADVICE", "GENERAL_WEATHER",
    }
    allowed_times = {
        "NOW", "TODAY", "TOMORROW", "NEXT_3_HOURS", "THIS_WEEK",
        "THIS_WEEKEND", "FUTURE", "UNKNOWN",
    }

    city = fallback_city
    intent = fallback_intent
    time_period = fallback_time

    for raw_line in (result or "").splitlines():
        line = raw_line.strip()

        if line.upper().startswith("CITY:"):
            value = line.split(":", 1)[1].strip()
            if value and value.upper() != "UNKNOWN":
                city = normalize_city(value)

        elif line.upper().startswith("INTENT:"):
            value = line.split(":", 1)[1].strip().upper()
            if value in allowed_intents:
                intent = value

        elif line.upper().startswith("TIME:"):
            value = line.split(":", 1)[1].strip().upper()
            if value in allowed_times:
                time_period = value

    return {
        "city": city,
        "intent": intent,
        "time": time_period,
    }


def understand_question(question, conversation_context=None):
    if conversation_context is None:
        conversation_context = {}

    city = extract_city(question)
    intent = detect_intent(question)
    time_period = detect_time(question)

    # Preserve conversation context for follow-up questions.
    if city == "UNKNOWN":
        previous_city = conversation_context.get("city")
        if previous_city:
            city = normalize_city(previous_city)

    if intent == "GENERAL_WEATHER":
        previous_intent = conversation_context.get("intent")
        if previous_intent:
            intent = previous_intent

    if time_period == "UNKNOWN":
        previous_time = conversation_context.get("time")
        if previous_time:
            time_period = previous_time

    # Do not call an LLM for a question we already understand.
    if city != "UNKNOWN" and intent != "GENERAL_WEATHER":
        return {
            "city": city,
            "intent": intent,
            "time": time_period,
        }

    previous_city = conversation_context.get("city", "UNKNOWN")
    previous_intent = conversation_context.get("intent", "UNKNOWN")
    previous_time = conversation_context.get("time", "UNKNOWN")
    previous_question = conversation_context.get("last_question", "NONE")

    prompt = f"""
You are the query understanding system for WeatherGPT.

PREVIOUS CONVERSATION:
City: {previous_city}
Intent: {previous_intent}
Time: {previous_time}
Previous question: {previous_question}

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

    # Gemini first.
    client = get_client()

    if client is not None:
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

            result = getattr(response, "text", "").strip()

            if result:
                return _parse_understanding(
                    result,
                    city,
                    intent,
                    time_period,
                )

        except Exception as error:
            print("Gemini understanding error:", repr(error))

    # DeepSeek fallback.
    deepseek_result = ask_deepseek(prompt)

    if deepseek_result:
        return _parse_understanding(
            deepseek_result,
            city,
            intent,
            time_period,
        )

    # Never fail completely just because AI is unavailable.
    return {
        "city": city,
        "intent": intent,
        "time": time_period,
        "error": "AI understanding unavailable; using locally detected information.",
    }
