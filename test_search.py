from commands.search import handle_search


tests = [
    "Search Google for quantum physics",
    "Search YouTube for Python tutorial"
]


print("===== Search Test =====\n")


for text in tests:

    print("Input:", text)

    result = handle_search(text)

    print("Result:", result)

    print("-" * 40)