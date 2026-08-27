def generate_warnings(conditions, severity):

    warnings = []

    if not conditions:
        return warnings

    # Extreme heat warning
    if "extreme_heat" in conditions:
        warnings.append(
            "⚠️ Extreme heat conditions detected. "
            "Avoid prolonged outdoor exposure and stay hydrated."
        )

    # Thunderstorm warning
    if "thunderstorm" in conditions:
        warnings.append(
            "⚠️ Thunderstorm conditions detected. "
            "Seek shelter and avoid open areas."
        )

    # Strong wind warning
    if "strong_wind" in conditions:
        warnings.append(
            "⚠️ Strong winds detected. "
            "Be cautious around trees, structures, and loose objects."
        )

    # Heavy rain-related warning
    if "rain" in conditions and severity == "severe":
        warnings.append(
            "⚠️ Severe weather conditions with rain detected. "
            "Exercise caution while traveling."
        )

    return warnings