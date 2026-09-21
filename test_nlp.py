from ai.nlp import process

tests = [
    "Open Chrome",
    "Launch Calculator",
    "Search Google for Python",
    "Search YouTube for AI news",
]

print("===== NLP Pipeline =====\n")

for t in tests:

    result = process(t)

    print(result)