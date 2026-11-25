
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_keys = [
    key.strip()
    for key in os.getenv("LLM_API_KEYS", "").split(",")
    if key.strip()
]

if not api_keys:
    raise RuntimeError("No API keys configured")

url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models"
)

response = requests.get(
    url,
    headers={
        "x-goog-api-key": api_keys[0]
    },
    timeout=20
)

print("HTTP Status:", response.status_code)

if response.status_code != 200:
    print("Google API Error:")
    print(response.text)
else:
    print("\nAvailable models:\n")

    for model in response.json().get("models", []):
        if "generateContent" in model.get(
            "supportedGenerationMethods", []
        ):
            print(model["name"])
