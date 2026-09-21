from ai.ollama import Ollama

bot = Ollama()

reply = bot.ask("Say only the word SUCCESS.")
print(reply)