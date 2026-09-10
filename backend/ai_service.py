import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")

deepseek_client = None
if DEEPSEEK_API_KEY:
    deepseek_client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
    )

_client = None


def get_client():
    global _client
    if _client is not None:
        return _client
    if not API_KEY:
        return None
    _client = genai.Client(api_key=API_KEY)
    return _client


def ask_deepseek(prompt):
    if deepseek_client is None:
        return None
    try:
        response = deepseek_client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are WeatherGPT, a concise and reliable weather "
                        "assistant. Use only supplied weather data. Never "
                        "invent weather facts. Return only the final answer."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
        )
        content = response.choices[0].message.content
        return content.strip() if content and content.strip() else None
    except Exception as error:
        print("DeepSeek error:", repr(error))
        return None


def _format_value(value):
    if value is None:
        return "N/A"
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
    warnings = intelligence.get("warnings") or []
    recommendations = intelligence.get("recommendations") or []
    if warnings:
        return f"⚠️ Weather alert: {warnings[0]}"
    if recommendations:
        return f"💡 WeatherGPT recommendation: {recommendations[0]}"
    return None


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

KNOWN_CITIES = [
    "Ahmedabad", "Mumbai", "Delhi", "New Delhi", "Bengaluru",
    "Bangalore", "Chennai", "Hyderabad", "Pune", "Kolkata",
    "Surat", "Vadodara", "Rajkot", "Jaipur", "Lucknow", "Kanpur",
    "Indore", "Bhopal", "Nagpur", "Patna", "Ranchi", "Noida",
    "Gurugram", "Chandigarh", "Amritsar", "Nashik", "Thane",
    "Mysuru", "Mysore", "Bhavnagar",
]


def normalize_city(city):
    city = re.sub(r"^the\s+", "", (city or "").strip(), flags=re.IGNORECASE)
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

    for wrong, correct in CITY_ALIASES.items():
        if re.search(r"\b" + re.escape(wrong) + r"\b", lower_text):
            return correct

    # Strong explicit-location parsing. This supports arbitrary cities,
    # including London, Paris, New York, Tokyo, etc.
    explicit_patterns = [
        r"\b(?:in|at|for|near)\s+(?:the\s+)?"
        r"([A-Za-z][A-Za-z .'-]{1,60}?)"
        r"(?:\?|$|,|\s+(?:tomorrow|today|tonight|this|now|currently|"
        r"weather|forecast|temperature|rain|humidity|wind|will|is|are|"
        r"what|how|should|can|could|would|later|next)\b)",
    ]

    for pattern in explicit_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            candidate = normalize_city(match.group(1))
            if candidate != "UNKNOWN":
                return candidate

    for city in sorted(KNOWN_CITIES, key=len, reverse=True):
        if re.search(r"\b" + re.escape(city.lower()) + r"\b", lower_text):
            return city

    # Direct standalone city question.
    candidate = normalize_city(re.sub(r"[?!.,]+$", "", text))
    if candidate.lower() not in {
        "what", "weather", "temperature", "rain", "forecast",
        "humidity", "wind", "today", "tomorrow", "now"
    } and 2 <= len(candidate.split()) <= 4:
        if re.fullmatch(r"[A-Za-z][A-Za-z .'-]*", text):
            return candidate

    return "UNKNOWN"


def detect_time(question):
    text = (question or "").lower()
    if re.search(r"\bnow\b|\bcurrently\b|\bright now\b", text):
        return "NOW"
    if (
        re.search(r"\bnext\s+3\s+hours?\b", text)
        or re.search(r"\bnext\s+three\s+hours?\b", text)
    ):
        return "NEXT_3_HOURS"
    if "tomorrow" in text:
        return "TOMORROW"
    if "today" in text:
        return "TODAY"
    if "this weekend" in text or "weekend" in text:
        return "THIS_WEEKEND"
    if "next week" in text or "future" in text:
        return "FUTURE"
    if "this week" in text or "weekly" in text or re.search(r"\bweek\b", text):
        return "THIS_WEEK"
    return "UNKNOWN"


def detect_intent(question):
    text = (question or "").lower()
    if any(x in text for x in ("rain", "raining", "rainfall", "shower")):
        return "RAIN"
    if any(x in text for x in ("temperature", "hot", "cold", "heat")):
        return "TEMPERATURE"
    if any(x in text for x in ("humidity", "humid")):
        return "HUMIDITY"
    if any(x in text for x in ("wind", "windy")):
        return "WIND"
    if any(x in text for x in ("forecast", "tomorrow", "next week", "this week", "weekend")):
        return "FORECAST"
    if any(x in text for x in ("should i", "can i", "advice", "recommend", "wear", "carry")):
        return "WEATHER_ADVICE"
    if any(x in text for x in ("weather", "condition", "conditions")):
        return "CURRENT_WEATHER"
    return "GENERAL_WEATHER"


def _parse_understanding(
    result,
    fallback_city="UNKNOWN",
    fallback_intent="GENERAL_WEATHER",
    fallback_time="UNKNOWN",
):
    allowed_intents = {
        "CURRENT_WEATHER", "FORECAST", "RAIN", "TEMPERATURE",
        "HUMIDITY", "WIND", "WEATHER_ADVICE", "GENERAL_WEATHER",
    }
    allowed_times = {
        "NOW", "TODAY", "TOMORROW", "NEXT_3_HOURS",
        "THIS_WEEK", "THIS_WEEKEND", "FUTURE", "UNKNOWN",
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

    return {"city": city, "intent": intent, "time": time_period}


def understand_question(question, conversation_context=None, selected_city=None):
    if conversation_context is None:
        conversation_context = {}

    # Priority:
    # 1) explicit city in current question
    # 2) selected UI city
    # 3) previous conversation city
    explicit_city = extract_city(question)
    local_intent = detect_intent(question)
    local_time = detect_time(question)

    previous_city = normalize_city(conversation_context.get("city", "")) \
        if conversation_context.get("city") else "UNKNOWN"
    previous_intent = conversation_context.get("intent", "UNKNOWN")
    previous_time = conversation_context.get("time", "UNKNOWN")
    previous_question = conversation_context.get("last_question", "NONE")
    selected = normalize_city(selected_city) if selected_city else "UNKNOWN"

    if local_intent == "GENERAL_WEATHER" and previous_intent != "UNKNOWN":
        local_intent = previous_intent

    if local_time == "UNKNOWN" and previous_time != "UNKNOWN":
        local_time = previous_time

    # If the current question explicitly names a city, it wins immediately.
    if explicit_city != "UNKNOWN":
        return {
            "city": explicit_city,
            "intent": local_intent,
            "time": local_time,
        }

    # No explicit city in the current question. For straightforward
    # follow-ups, selected city is the next best source.
    if selected != "UNKNOWN" and local_intent != "GENERAL_WEATHER":
        return {
            "city": selected,
            "intent": local_intent,
            "time": local_time,
        }

    prompt = f"""
You are the query-understanding system for WeatherGPT.

LOCATION PRIORITY — THIS IS CRITICAL:
1. A city explicitly mentioned in the CURRENT QUESTION ALWAYS WINS.
2. SELECTED CITY is only a fallback when the CURRENT QUESTION has no city.
3. PREVIOUS CONVERSATION CITY is only a fallback when neither the current
   question nor selected city provides a city.
4. NEVER replace an explicit city from the current question with the
   selected city or previous city.

SELECTED CITY:
{selected}

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
NEXT_3_HOURS
THIS_WEEK
THIS_WEEKEND
FUTURE
UNKNOWN

Return ONLY the three lines.
"""

    # Let the model resolve arbitrary city names when local regex extraction
    # does not confidently identify them.
    client = get_client()
    if client is not None:
        try:
            chat = client.chats.create(model=MODEL_NAME)
            response = chat.send_message(prompt)
            result = getattr(response, "text", "").strip()
            if result:
                parsed = _parse_understanding(
                    result,
                    "UNKNOWN",
                    local_intent,
                    local_time,
                )
                if parsed["city"] != "UNKNOWN":
                    return parsed
        except Exception as error:
            print("Gemini understanding error:", repr(error))

    deepseek_result = ask_deepseek(prompt)
    if deepseek_result:
        parsed = _parse_understanding(
            deepseek_result,
            "UNKNOWN",
            local_intent,
            local_time,
        )
        if parsed["city"] != "UNKNOWN":
            return parsed

    fallback_city = selected if selected != "UNKNOWN" else previous_city

    return {
        "city": fallback_city,
        "intent": local_intent,
        "time": local_time,
        "error": "AI understanding unavailable; using location-priority fallback.",
    }


def _deterministic_weather_answer(
    question,
    weather_data=None,
    forecast_data=None,
    intelligence=None,
):
    q = (question or "").lower()

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
            rain = float(item.get("rain_3h") or 0)
            answer = (
                f"⏱️ Next 3 hours in {location}\n\n"
                f"Forecast period: {item.get('datetime', 'the next period')}\n"
                f"☁️ Conditions: {_condition_label(item.get('weather'))}\n"
            )
            if item.get("temperature") is not None:
                answer += f"🌡️ Temperature: {_format_value(item['temperature'])}°C\n"
            answer += (
                f"🌧️ Rain: About {_format_value(rain)} mm is forecast in this period."
                if rain > 0
                else "🌧️ Rain: No measurable rainfall is indicated for this period."
            )
            rec = _smart_recommendation(intelligence)
            if rec:
                answer += f"\n\n{rec}"
            return answer

        if "rain" in q or "umbrella" in q:
            if rainy_items:
                first = rainy_items[0]
                amount = float(first.get("rain_3h") or 0)
                answer = (
                    f"🌧️ Rain outlook for {location}\n\n"
                    f"Rain is indicated around {first.get('datetime', 'the forecast period')}."
                )
                if amount > 0:
                    answer += f" About {_format_value(amount)} mm is forecast in that 3-hour period."
                return answer + "\n\n💡 Keep an umbrella handy."
            return (
                f"🌤️ Rain outlook for {location}\n\n"
                "No measurable rainfall is indicated in the available forecast period."
            )

        if temps:
            representative = items[0]
            answer = (
                f"📅 Forecast for {location}\n\n"
                f"🌡️ Temperature range: {_format_value(min(temps))}°C to "
                f"{_format_value(max(temps))}°C\n"
                f"☁️ Expected conditions: {_condition_label(representative.get('weather'))}\n"
                f"🌧️ Rain: {'Possible' if rainy_items else 'No rainfall indicated'}"
            )
            return answer

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

        if "temperature" in q or "how hot" in q or "how cold" in q:
            answer = (
                f"🌡️ Temperature in {location}\n\n"
                f"The current temperature is {_format_value(temperature)}°C."
            )
            if feels_like is not None:
                answer += f" It feels like {_format_value(feels_like)}°C."
            return answer

        if "humidity" in q:
            return (
                f"💧 Humidity in {location}\n\n"
                f"Current humidity is {_format_value(humidity)}%."
            )

        if "wind" in q:
            return (
                f"🌬️ Wind in {location}\n\n"
                f"Current wind speed is {_format_value(wind_speed)} m/s."
            )

        if any(x in q for x in ("rain", "raining", "umbrella")):
            rainy = any(
                word in condition.lower()
                for word in ("rain", "drizzle", "shower", "thunderstorm")
            )
            return (
                f"🌧️ Rain update for {location}\n\n"
                f"Current conditions indicate {condition.lower()}."
                + ("\n\n💡 Carry an umbrella." if rainy else
                   "\n\nNo rain is indicated right now.")
            )

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

        rec = _smart_recommendation(intelligence)
        if rec:
            answer += f"\n\n{rec}"

        return answer

    return None


def ask_ai(question, weather_data=None, forecast_data=None, intelligence=None):
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
            "should i", "recommend", "advice", "what should",
            "what do you suggest", "is it a good idea", "explain",
            "why", "what does this mean",
        )
    )

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
- Do not expose APIs, prompts, internal reasoning, or errors.
Return only the final user-facing answer.
"""

    client = get_client()
    if client is not None:
        try:
            chat = client.chats.create(model=MODEL_NAME)
            response = chat.send_message(prompt)
            result = getattr(response, "text", None)
            if result and result.strip():
                return result.strip()
        except Exception as error:
            print("Gemini answer error:", repr(error))

    deepseek_answer = ask_deepseek(prompt)
    if deepseek_answer:
        return deepseek_answer

    return fast_answer or "I could not generate an answer from the available weather data."
