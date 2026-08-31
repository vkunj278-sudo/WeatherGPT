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


def _deterministic_weather_answer(question, weather_data=None, forecast_data=None):
    """Safe final fallback using only retrieved weather data."""
    if weather_data:
        city = weather_data.get("city") or weather_data.get("location") or "the requested location"
        country = weather_data.get("country")
        location = f"{city}, {country}" if country else city

        parts = [f"Current weather in {location}:"]

        temperature = weather_data.get("temperature")
        feels_like = weather_data.get("feels_like")
        humidity = weather_data.get("humidity")
        wind_speed = weather_data.get("wind_speed")
        condition = weather_data.get("weather") or weather_data.get("condition")

        if temperature is not None:
            parts.append(f"Temperature: {_format_value(temperature)}°C.")
        if feels_like is not None:
            parts.append(f"Feels like: {_format_value(feels_like)}°C.")
        if condition:
            condition_text = str(condition).replace("_", " ").strip().capitalize()
            parts.append(f"Condition: {condition_text}.")
        if humidity is not None:
            parts.append(f"Humidity: {_format_value(humidity)}%.")
        if wind_speed is not None:
            parts.append(f"Wind: {_format_value(wind_speed)} m/s.")

        return " ".join(parts)

    if forecast_data:
        return "Forecast information was retrieved, but an AI summary could not be generated."

    return "I could not generate an answer because the required weather data is unavailable."


def _format_value(value):
    if value is None:
        return None
    if isinstance(value, float):
        return f"{value:.1f}".rstrip("0").rstrip(".")
    return str(value)


def _deterministic_weather_answer(question, weather_data=None, forecast_data=None, intelligence=None):
    """Fast response using only live data already retrieved."""
    q = (question or "").lower()

    if weather_data:
        city = weather_data.get("city") or "the requested location"
        country = weather_data.get("country")
        location = f"{city}, {country}" if country else city

        temp = weather_data.get("temperature")
        feels = weather_data.get("feels_like")
        humidity = weather_data.get("humidity")
        wind = weather_data.get("wind_speed")
        condition = weather_data.get("weather") or weather_data.get("condition")

        # Keep simple questions short.
        if "temperature" in q or "how hot" in q or "how cold" in q:
            if temp is not None:
                answer = f"The current temperature in {location} is {_format_value(temp)}°C."
                if feels is not None:
                    answer += f" It feels like {_format_value(feels)}°C."
                return answer

        if "humidity" in q:
            if humidity is not None:
                return f"The current humidity in {location} is {_format_value(humidity)}%."

        if "wind" in q:
            if wind is not None:
                return f"The current wind speed in {location} is {_format_value(wind)} m/s."

        if any(x in q for x in ("rain", "raining", "umbrella")):
            if condition:
                condition_text = str(condition).replace("_", " ").capitalize()
                answer = f"Current conditions in {location}: {condition_text}."
                if intelligence and intelligence.get("warnings"):
                    answer += " " + intelligence["warnings"][0]
                return answer

        parts = [f"Current weather in {location}:"]
        if temp is not None:
            parts.append(f"Temperature: {_format_value(temp)}°C.")
        if feels is not None:
            parts.append(f"Feels like: {_format_value(feels)}°C.")
        if condition:
            parts.append(f"Condition: {str(condition).replace('_', ' ').capitalize()}.")
        if humidity is not None:
            parts.append(f"Humidity: {_format_value(humidity)}%.")
        if wind is not None:
            parts.append(f"Wind: {_format_value(wind)} m/s.")
        return " ".join(parts)

    if forecast_data:
        entries = forecast_data.get("forecast") or forecast_data.get("data") or []
        if isinstance(entries, dict):
            entries = entries.get("forecast") or entries.get("list") or []

        if entries:
            lines = ["Here is the forecast:"]
            for item in entries[:5]:
                dt = item.get("datetime") or item.get("date") or "Forecast"
                temp = item.get("temperature")
                condition = item.get("weather") or item.get("condition")
                rain = item.get("rain_3h")
                line = str(dt)
                if temp is not None:
                    line += f" — {_format_value(temp)}°C"
                if condition:
                    line += f", {str(condition).replace('_', ' ')}"
                if rain is not None and float(rain or 0) > 0:
                    line += f", rain {_format_value(rain)} mm"
                lines.append(line + ".")
            return "\n".join(lines)

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
    city = re.sub(r"\\s+", " ", city).strip(" .,'\"")

    alias = CITY_ALIASES.get(city.lower())
    if alias:
        return alias

    return city.title() if city else "UNKNOWN"


def extract_city(question):
    if not question:
        return "UNKNOWN"

    text = question.strip()
    lower_text = text.lower()

    # Correct common misspellings before the general pattern.
    for wrong, correct in CITY_ALIASES.items():
        if re.search(r"\\b" + re.escape(wrong) + r"\\b", lower_text):
            return correct

    pattern = re.search(
        r"\\b(?:in|at|for|near)\\s+(?:the\\s+)?"
        r"([A-Za-z][A-Za-z .'-]{1,60}?)"
        r"(?:\\?|$|,|\\s+(?:tomorrow|today|this|now|currently|"
        r"weather|forecast|temperature|rain|humidity|wind)\\b)",
        text,
        re.IGNORECASE,
    )

    if pattern:
        city = normalize_city(pattern.group(1))
        if city != "UNKNOWN":
            return city

    known_cities = [
        "Ahmedabad", "Mumbai", "Delhi", "New Delhi", "Bengaluru",
        "Bangalore", "Chennai", "Hyderabad", "Pune", "Kolkata",
        "Surat", "Vadodara", "Rajkot", "Jaipur", "Lucknow", "Kanpur",
        "Indore", "Bhopal", "Nagpur", "Patna", "Ranchi", "Noida",
        "Gurugram", "Chandigarh", "Amritsar", "Nashik", "Thane",
        "Mysuru", "Mysore",
    ]

    for city in sorted(known_cities, key=len, reverse=True):
        if re.search(r"\\b" + re.escape(city.lower()) + r"\\b", lower_text):
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

def _parse_understanding(result, fallback_city, fallback_intent, fallback_time):
    allowed_intents = {
        "CURRENT_WEATHER", "FORECAST", "RAIN", "TEMPERATURE",
        "HUMIDITY", "WIND", "WEATHER_ADVICE", "GENERAL_WEATHER",
    }
    allowed_times = {
        "NOW", "TODAY", "TOMORROW", "THIS_WEEK",
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
