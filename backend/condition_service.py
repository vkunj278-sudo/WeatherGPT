def analyze_conditions(weather_data):

    if not weather_data:
        return {
            "conditions": [],
            "severity": "unknown"
        }

    conditions = []

    temperature = weather_data.get("temperature")
    humidity = weather_data.get("humidity")
    wind_speed = weather_data.get("wind_speed")
    weather = str(weather_data.get("weather", "")).lower()

    # Temperature analysis
    if temperature is not None:

        if temperature >= 40:
            conditions.append("extreme_heat")

        elif temperature >= 35:
            conditions.append("hot")

        elif temperature <= 10:
            conditions.append("cold")

    # Rain analysis
    if any(word in weather for word in [
        "rain",
        "drizzle",
        "shower"
    ]):
        conditions.append("rain")

    # Thunderstorm analysis
    if "thunderstorm" in weather:
        conditions.append("thunderstorm")

    # Cloud analysis
    if "cloud" in weather:
        conditions.append("cloudy")

    # Clear weather
    if "clear" in weather:
        conditions.append("clear")

    # Wind analysis
    if wind_speed is not None:

        if wind_speed >= 15:
            conditions.append("strong_wind")

        elif wind_speed >= 8:
            conditions.append("windy")

    # Humidity analysis
    if humidity is not None:

        if humidity >= 85:
            conditions.append("very_humid")

        elif humidity >= 70:
            conditions.append("humid")

    # Determine severity
    if any(condition in conditions for condition in [
        "extreme_heat",
        "thunderstorm"
    ]):
        severity = "severe"

    elif any(condition in conditions for condition in [
        "hot",
        "cold",
        "rain",
        "strong_wind"
    ]):
        severity = "moderate"

    else:
        severity = "normal"

    return {
        "conditions": conditions,
        "severity": severity
    }

def analyze_forecast_conditions(forecast_data):

    if not forecast_data or "forecast" not in forecast_data:
        return {
            "conditions": [],
            "severity": "unknown"
        }

    forecast_list = forecast_data["forecast"]

    all_conditions = []

    max_temperature = None
    max_wind_speed = None
    max_humidity = None

    for item in forecast_list:

        temperature = item.get("temperature")
        wind_speed = item.get("wind_speed")
        humidity = item.get("humidity")
        weather = str(item.get("weather", "")).lower()

        # Track maximum values
        if temperature is not None:
            if max_temperature is None or temperature > max_temperature:
                max_temperature = temperature

        if wind_speed is not None:
            if max_wind_speed is None or wind_speed > max_wind_speed:
                max_wind_speed = wind_speed

        if humidity is not None:
            if max_humidity is None or humidity > max_humidity:
                max_humidity = humidity

        # Weather conditions
        if any(word in weather for word in [
            "rain",
            "drizzle",
            "shower"
        ]):
            if "rain" not in all_conditions:
                all_conditions.append("rain")

        if "thunderstorm" in weather:
            if "thunderstorm" not in all_conditions:
                all_conditions.append("thunderstorm")

        if "cloud" in weather:
            if "cloudy" not in all_conditions:
                all_conditions.append("cloudy")

        if "clear" in weather:
            if "clear" not in all_conditions:
                all_conditions.append("clear")

    # Temperature conditions
    if max_temperature is not None:

        if max_temperature >= 40:
            all_conditions.append("extreme_heat")

        elif max_temperature >= 35:
            all_conditions.append("hot")

        elif max_temperature <= 10:
            all_conditions.append("cold")

    # Wind conditions
    if max_wind_speed is not None:

        if max_wind_speed >= 15:
            all_conditions.append("strong_wind")

        elif max_wind_speed >= 8:
            all_conditions.append("windy")

    # Humidity conditions
    if max_humidity is not None:

        if max_humidity >= 85:
            all_conditions.append("very_humid")

        elif max_humidity >= 70:
            all_conditions.append("humid")

    # Determine severity
    severe_conditions = [
        "extreme_heat",
        "thunderstorm",
        "strong_wind"
    ]

    moderate_conditions = [
        "hot",
        "cold",
        "rain",
        "very_humid"
    ]

    severity = "normal"

    for condition in all_conditions:

        if condition in severe_conditions:
            severity = "severe"
            break

        if condition in moderate_conditions:
            severity = "moderate"

    return {
        "conditions": all_conditions,
        "severity": severity
    }