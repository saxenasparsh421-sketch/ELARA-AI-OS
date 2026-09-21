from ai.memory_engine import MemoryEngine

memory = MemoryEngine()

print("===== Memory Test =====\n")

memory.remember("name", "Boss")
memory.remember("city", "Delhi")

print(memory.recall("name"))
print(memory.recall("city"))

print()

print(memory.all())