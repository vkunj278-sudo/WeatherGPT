conversation_memory = {}


def save_conversation(
    session_id,
    city=None,
    intent=None,
    time_period=None,
    last_question=None
):

    if session_id not in conversation_memory:
        conversation_memory[session_id] = {}

    if city and city != "UNKNOWN":
        conversation_memory[session_id]["city"] = city

    if intent and intent != "GENERAL_WEATHER":
        conversation_memory[session_id]["intent"] = intent

    if time_period and time_period != "UNKNOWN":
        conversation_memory[session_id]["time"] = time_period

    if last_question:
        conversation_memory[session_id]["last_question"] = last_question


def get_conversation(session_id):

    return conversation_memory.get(session_id, {})


def clear_conversation(session_id):

    if session_id in conversation_memory:
        del conversation_memory[session_id]