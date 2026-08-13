# test_openrouter.py
import os
import requests
from dotenv import load_dotenv
load_dotenv()

model = "google/gemma-4-31b-it:free"
print(f"Testing model: {model} with 60s timeout...")
try:
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}"},
        json={"model": model, "messages": [{"role": "user", "content": "1+1は？"}]},
        timeout=60,
    )
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
