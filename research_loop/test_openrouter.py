# test_openrouter.py
import os
from dotenv import load_dotenv
load_dotenv()

from llm_router import _call_openrouter

model = "google/gemma-4-31b-it:free"
print(f"Testing _call_openrouter with model: {model}")
try:
    result = _call_openrouter(model, "1+1は？")
    print(f"Success! Result: {result}")
except Exception as e:
    print(f"Failed with exception: {e}")
