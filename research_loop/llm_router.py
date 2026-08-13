import os
import time
import yaml
import requests
from google import genai
from dotenv import load_dotenv

load_dotenv()

with open("config.yaml", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

_gemini_client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))


def _call_gemini(model: str, prompt: str) -> str:
    interaction = _gemini_client.interactions.create(model=model, input=prompt)
    return interaction.output_text


def _call_openrouter(model: str, prompt: str) -> str:
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}"},
        json={"model": model, "messages": [{"role": "user", "content": prompt}]},
        timeout=300,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"OpenRouterエラー ({resp.status_code}): {resp.text}")
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
