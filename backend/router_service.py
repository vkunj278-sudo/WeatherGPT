def decide_data_source(intent):
    """
    Decide which weather data is needed based on the user's intent.
    """

    if intent == "CURRENT_WEATHER":
        return "current"

    elif intent == "TEMPERATURE":
        return "current"

    elif intent == "HUMIDITY":
        return "current"

    elif intent == "WIND":
        return "current"

    elif intent == "RAIN":
        return "forecast"

    elif intent == "FORECAST":
        return "forecast"

    elif intent == "WEATHER_ADVICE":
        return "both"

    elif intent == "GENERAL_WEATHER":
        return "current"

    else:
        return "current"