
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent

def patch_main():
    path = ROOT / "backend" / "main.py"
    text = path.read_text(encoding="utf-8")

    old_sig = '''@app.get("/smart-weather")
def smart_weather(
    question: str,
    session_id: str = "default"
):'''
    new_sig = '''@app.get("/smart-weather")
def smart_weather(
    question: str,
    session_id: str = "default",
    selected_city: str = None
):'''
    if old_sig in text:
        text = text.replace(old_sig, new_sig, 1)

    old_call = '''understanding = understand_weather_question(
        question,
        memory
    )'''
    new_call = '''understanding = understand_weather_question(
        question,
        memory,
        selected_city=selected_city
    )'''
    if old_call in text:
        text = text.replace(old_call, new_call, 1)

    path.write_text(text, encoding="utf-8")
    print("Patched backend/main.py")


def patch_understanding_service():
    path = ROOT / "backend" / "understanding_service.py"
    text = path.read_text(encoding="utf-8")

    text = re.sub(
        r"def understand_weather_question\(\s*question,\s*conversation_context=None\s*(?:,\s*selected_city=None\s*)?\):",
        '''def understand_weather_question(
    question,
    conversation_context=None,
    selected_city=None
):''',
        text, count=1
    )

    text = re.sub(
        r"return understand_question\(\s*question,\s*conversation_context\s*(?:,\s*selected_city=selected_city)?\s*\)",
        '''return understand_question(
        question,
        conversation_context,
        selected_city=selected_city
    )''',
        text, count=1
    )

    path.write_text(text, encoding="utf-8")
    print("Patched backend/understanding_service.py")


def patch_ai_service():
    path = ROOT / "backend" / "ai_service.py"
    text = path.read_text(encoding="utf-8")

    text = re.sub(
        r"def understand_question\(\s*question,\s*conversation_context=None\s*\):",
        '''def understand_question(
    question,
    conversation_context=None,
    selected_city=None
):''',
        text, count=1
    )

    old = '''    city = extract_city(question)
    intent = detect_intent(question)
    time_period = detect_time(question)

    # Preserve conversation context for follow-up questions.
    if city == "UNKNOWN":
        previous_city = conversation_context.get("city")
        if previous_city:
            city = normalize_city(previous_city)'''

    new = '''    city = extract_city(question)
    intent = detect_intent(question)
    time_period = detect_time(question)

    # City priority:
    # 1. Explicit city in current question
    # 2. Selected UI city
    # 3. Previous conversation city
    if city == "UNKNOWN" and selected_city:
        city = normalize_city(selected_city)

    if city == "UNKNOWN":
        previous_city = conversation_context.get("city")
        if previous_city:
            city = normalize_city(previous_city)'''

    if old in text:
        text = text.replace(old, new, 1)
    elif "if city == \"UNKNOWN\" and selected_city:" not in text:
        marker = "    time_period = detect_time(question)"
        if marker in text:
            text = text.replace(
                marker,
                marker + '''\n\n    # Explicit current-question city wins.
    if city == "UNKNOWN" and selected_city:
        city = normalize_city(selected_city)''',
                1
            )

    path.write_text(text, encoding="utf-8")
    print("Patched backend/ai_service.py")


def patch_frontend():
    path = ROOT / "frontend" / "src" / "components" / "ChatBox.jsx"
    text = path.read_text(encoding="utf-8")

    old_pattern = re.compile(
        r"const lower = question\.toLowerCase\(\);.*?"
        r"url\.searchParams\.set\(\"session_id\", sessionId\);",
        re.S,
    )

    replacement = '''// Do NOT append the selected city to the user's question.
    // Send it separately so the backend can use it only as a fallback.
    url.searchParams.set("question", question);
    url.searchParams.set("session_id", sessionId);
    url.searchParams.set("selected_city", locationName);'''

    text, count = old_pattern.subn(replacement, text, count=1)

    if count == 0:
        text = text.replace(
            'url.searchParams.set("question", finalQuestion);',
            'url.searchParams.set("question", question);',
            1
        )
        if 'url.searchParams.set("selected_city", locationName);' not in text:
            text = text.replace(
                'url.searchParams.set("session_id", sessionId);',
                'url.searchParams.set("session_id", sessionId);\n    url.searchParams.set("selected_city", locationName);',
                1
            )

    path.write_text(text, encoding="utf-8")
    print("Patched frontend/src/components/ChatBox.jsx")


if __name__ == "__main__":
    print("Applying WeatherGPT city-priority fix...")
    patch_main()
    patch_understanding_service()
    patch_ai_service()
    patch_frontend()
    print("\nDONE. Restart backend:")
    print("uvicorn backend.main:app --reload")
