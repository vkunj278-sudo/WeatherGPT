def generate_recommendations(conditions):

    recommendations = []

    if not conditions:
        return recommendations

    # Extreme heat
    if "extreme_heat" in conditions:
        recommendations.append(
            "Avoid prolonged outdoor activity and stay hydrated."
        )

    # Hot weather
    elif "hot" in conditions:
        recommendations.append(
            "Stay hydrated and avoid prolonged exposure to direct sunlight."
        )

    # Cold weather
    if "cold" in conditions:
        recommendations.append(
            "Wear warm clothing and limit prolonged exposure to cold conditions."
        )

    # Rain
    if "rain" in conditions:
        recommendations.append(
            "Carry an umbrella and be careful on wet or slippery roads."
        )

    # Thunderstorm
    if "thunderstorm" in conditions:
        recommendations.append(
            "Avoid open areas and seek shelter during thunderstorms."
        )

    # Strong wind
    if "strong_wind" in conditions:
        recommendations.append(
            "Be cautious outdoors and avoid areas with loose objects or branches."
        )

    # Humidity
    if "very_humid" in conditions:
        recommendations.append(
            "Stay hydrated and take breaks from strenuous outdoor activity."
        )

    elif "humid" in conditions:
        recommendations.append(
            "Drink enough water and stay in well-ventilated areas."
        )

    # Clear weather
    if "clear" in conditions:
        recommendations.append(
            "Weather conditions are generally suitable for outdoor activities."
        )

    return recommendations
