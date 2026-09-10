from backend.ai_service import understand_question


def understand_weather_question(
    question,
    conversation_context=None,
    selected_city=None
):
    return understand_question(
        question,
        conversation_context,
        selected_city=selected_city
    )
