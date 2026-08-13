import os
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


def _call_hf_ollama(model: str, prompt: str) -> str:
    hf_url = os.environ.get("HF_SPACE_URL")
    resp = requests.post(
        f"{hf_url}/api/chat",
        json={"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False},
        timeout=600,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]


PROVIDERS = {
    "gemini": _call_gemini,
    "openrouter": _call_openrouter,
    "hf_ollama": _call_hf_ollama,
}


def call_role(role: str, prompt: str) -> str:
    role_cfg = CONFIG["roles"][role]
    fn = PROVIDERS[role_cfg["provider"]]
    return fn(role_cfg["model"], prompt)
