from ai.intent import detect_intent

tests = [

    "Open Chrome",

    "Launch Calculator",

    "Search Python",

    "Google AI",

    "Search YouTube for music",

    "Take Screenshot",

    "Shutdown computer",

    "Hello Boss"
]

print("===== Intent Test =====\n")

for t in tests:

    print("Input :", t)

    print("Intent:", detect_intent(t))

    print("-" * 40)