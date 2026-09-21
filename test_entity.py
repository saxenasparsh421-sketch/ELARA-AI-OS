from ai.intent import detect_intent
from ai.entity import extract_entity

tests = [
    "Open Chrome",
    "Launch Calculator",
    "Search Google for Python",
    "Search YouTube for AI news",
    "Find machine learning",
]

print("===== Entity Test =====\n")

for text in tests:

    intent = detect_intent(text)

    entity = extract_entity(text, intent)

    print("Input :", text)
    print("Intent:", intent)
    print("Entity:", entity)
    print("-" * 40)