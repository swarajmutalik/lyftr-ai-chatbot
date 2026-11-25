
import os
from pathlib import Path
from time import perf_counter

import litellm
from dotenv import load_dotenv
from litellm.caching.caching import Cache

load_dotenv(
    Path(__file__).resolve().parent / ".env"
)

api_key = os.getenv("LLM_API_KEYS", "").split(",")[0].strip()
model = os.getenv("LLM_MODEL")

litellm.cache = Cache(type="local")

messages = [
    {
        "role": "system",
        "content": "You are a helpful AI assistant."
    },
    {
        "role": "user",
        "content": "What is the capital of Japan?"
    }
]

for attempt in range(1, 3):
    start = perf_counter()

    response = litellm.completion(
        model=model,
        messages=messages,
        api_key=api_key,
        caching=True,
        num_retries=0
    )

    elapsed = round(
        (perf_counter() - start) * 1000
    )

    hidden = getattr(
        response, "_hidden_params", {}
    ) or {}

    print(f"\nRequest {attempt}")
    print("Reply:", response.choices[0].message.content)
    print("Latency:", elapsed, "ms")
    print("Cache metadata:", {
        "cache_hit": hidden.get("cache_hit"),
        "cache_key": hidden.get("cache_key")
    })
    print("Input tokens:", response.usage.prompt_tokens)
    print("Output tokens:", response.usage.completion_tokens)
