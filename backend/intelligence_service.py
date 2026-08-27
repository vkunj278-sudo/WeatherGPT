def analyze_weather(weather_data):
    if "error" in weather_data:
        return weather_data

    temperature = weather_data.get("temperature", 0)
    humidity = weather_data.get("humidity", 0)
    wind_speed = weather_data.get("wind_speed", 0)
    condition = weather_data.get("weather", "")

    risks = []
    advice = []

    # Heat detection
    if temperature >= 40:
        risks.append("Extreme heat")
        advice.append("Avoid prolonged outdoor exposure and stay hydrated.")

    elif temperature >= 35:
        risks.append("High temperature")
        advice.append("Stay hydrated and avoid unnecessary exposure to direct sunlight.")

    # Rain detection
    if "rain" in condition.lower():
        risks.append("Rain")
        advice.append("Carry an umbrella and consider rain protection.")

    # Strong wind detection
    if wind_speed >= 10:
        risks.append("Strong wind")
        advice.append("Be cautious around trees, temporary structures, and open areas.")

    # Humidity
    if humidity >= 80:
        risks.append("High humidity")
        advice.append("The temperature may feel warmer than the actual temperature.")

    if not risks:
        risks.append("No major weather risk detected.")

    return {
        "risks": risks,
        "advice": advice
    }