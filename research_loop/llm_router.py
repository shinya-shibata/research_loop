import os
import time
import yaml
import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

with open("config.yaml") as f:
    CONFIG = yaml.safe_load(f)

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))


def _call_gemini(model: str, prompt: str) -> str:
    m = genai.GenerativeModel(model)
    return m.generate_content(prompt).text


def _call_openrouter(model: str, prompt: str) -> str:
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}"},
        json={"model": model, "messages": [{"role": "user", "content": prompt}]},
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


PROVIDERS = {
    "gemini": _call_gemini,
    "openrouter": _call_openrouter,
}


def call_role(role: str, prompt: str) -> str:
    role_cfg = CONFIG["roles"][role]
    fn = PROVIDERS[role_cfg["provider"]]
    result = fn(role_cfg["model"], prompt)
    if role_cfg["provider"] == "openrouter":
        time.sleep(3)  # 連続呼び出しでのレート制限回避
    return result
