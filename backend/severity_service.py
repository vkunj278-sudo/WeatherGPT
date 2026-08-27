def determine_severity(conditions):

    if not conditions:
        return "normal"

    severe_conditions = [
        "extreme_heat",
        "thunderstorm"
    ]

    moderate_conditions = [
        "hot",
        "cold",
        "rain",
        "strong_wind",
        "very_humid"
    ]

    # Check for severe conditions
    for condition in conditions:

        if condition in severe_conditions:
            return "severe"

    # Check for moderate conditions
    for condition in conditions:

        if condition in moderate_conditions:
            return "moderate"

    return "normal"