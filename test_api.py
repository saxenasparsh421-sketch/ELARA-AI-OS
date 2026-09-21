import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5:0.5b",
        "prompt": "Hello",
        "stream": False
    }
)

print(response.status_code)
print(response.text)