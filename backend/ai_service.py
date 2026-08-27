import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)


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

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text

def extract_city(question):

    prompt = f"""
You are a location extraction system.

Read the user's question:

"{question}"

Find the city or location mentioned in the question.

Return ONLY the city or location name.
Do not provide any explanation.
Do not use quotation marks.

If no location is mentioned, return:
UNKNOWN
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    city = response.text.strip()

    return city

def extract_intent(question):

    prompt = f"""
You are a weather query understanding system.

Analyze this user question:

"{question}"

Identify the user's weather-related intent.

Choose ONLY ONE of these intents:

CURRENT_WEATHER
FORECAST
RAIN
TEMPERATURE
HUMIDITY
WIND
WEATHER_ADVICE
GENERAL_WEATHER

Return ONLY the intent name.
Do not provide any explanation.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text.strip().upper()