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
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}"},
            json={"model": model, "messages": [{"role": "user", "content": prompt}]},
            timeout=300,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"OpenRouter error ({resp.status_code}): {resp.text}")
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        if model == "google/gemma-4-31b-it:free":
            fallback_model = "nvidia/nemotron-3-ultra-550b-a55b:free"
            print(f"Warning: Failed to call {model}. Retrying with {fallback_model}. Error cause: {e}")
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}"},
                json={"model": fallback_model, "messages": [{"role": "user", "content": prompt}]},
                timeout=300,
            )
            if resp.status_code != 200:
                raise RuntimeError(f"OpenRouter error (fallback also failed) ({resp.status_code}): {resp.text}")
            return resp.json()["choices"][0]["message"]["content"]
        else:
            raise e


PROVIDERS = {
    "gemini": _call_gemini,
    "openrouter": _call_openrouter,
}


def call_role(role: str, prompt: str) -> str:
    role_cfg = CONFIG["roles"][role]
    fn = PROVIDERS[role_cfg["provider"]]
    result = fn(role_cfg["model"], prompt)
    if role_cfg["provider"] == "openrouter":
        time.sleep(3)  # Avoid rate limits on consecutive calls
    return result
