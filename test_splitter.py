from commands.splitter import split_commands

tests = [
    "Open Chrome and YouTube",
    "Launch VS Code and Notepad",
    "Run Calculator and Chrome",
    "Open Chrome and",
    "Chrome",
    "Open Chrome, Netflix and Amazon"
]

print("\n===== Splitter Test =====\n")

for test in tests:
    print(f"Input : {test}")
    print(f"Output: {split_commands(test)}")
    print("-" * 40)