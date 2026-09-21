from ai.intent import detect_intent
from ai.entity import extract_entity


def process(text):

    intent = detect_intent(text)

    entity = extract_entity(text, intent)

    return {
        "intent": intent,
        "entity": entity,
        "text": text,
    }