import requests

r = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5:0.5b",
        "prompt": "Explain quantum physics",
        "stream": False,
    },
    timeout=120,
)

print(r.status_code)
print(r.json()["response"])