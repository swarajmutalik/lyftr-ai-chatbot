
import os
import re

from dotenv import load_dotenv
from litellm import completion
from litellm.exceptions import (
    RateLimitError,
    ServiceUnavailableError,
    InternalServerError,
    BadGatewayError,
)

import litellm
from litellm.caching.caching import Cache

litellm.cache = Cache(type="local")

load_dotenv()

MODEL = os.getenv(
    "LLM_MODEL",
    "gemini/gemini-3.5-flash-lite"
)

API_KEYS = [
    key.strip()
    for key in os.getenv(
        "LLM_API_KEYS", ""
    ).split(",")
    if key.strip()
]


ENABLE_FAILURE_SIMULATION = (
    os.getenv(
        "ENABLE_FAILURE_SIMULATION",
        "false"
    ).lower() == "true"
)


def parse_simulated_failures(header):
    if not ENABLE_FAILURE_SIMULATION or not header:
        return {}

    failures = {}

    for entry in header.split(","):
        entry = entry.strip()

        match = re.fullmatch(
            r"(key_[1-9][0-9]*|\*)=(429|500|502|503)",
            entry
        )

        if match:
            key_id, status = match.groups()
            failures[key_id] = int(status)

    return failures

class AllProvidersUnavailable(Exception):
    pass


def generate_response(messages, simulate_failure=None):
    if len(API_KEYS) < 2:
        raise RuntimeError(
            "At least two API keys must be configured"
        )

    failed_attempts = 0
    
    failures = parse_simulated_failures(simulate_failure)

    simulation_active = bool(failures)

    for index, api_key in enumerate(API_KEYS):
        key_id = f"key_{index + 1}"

        try:
            # Simulate failure before contacting Gemini
            if (
                key_id in failures
                or "*" in failures
            ):
                status = failures.get(
                    key_id,
                    failures.get("*")
                )

                print(
                    f"Simulated failure: "
                    f"{key_id} -> HTTP {status}"
                )

                failed_attempts += 1
                continue

            print(f"Trying API key {index + 1}")

            response = completion(
                model=MODEL,
                messages=messages,
                api_key=api_key,
                caching=not simulation_active,
                num_retries=0
            )
        
            
            hidden_params = getattr(
                response,
                "_hidden_params",
                {}
            ) or {}

            cache_hit = (
                hidden_params.get("cache_hit") is True
            )

            print(
                "Resolution:",
                "LLM_CACHE" if cache_hit
                else "LIVE_INFERENCE"
            )

            reply = response.choices[0].message.content

            if not reply:
                raise ValueError(
                    "LLM returned an empty response"
                )

            
            return {
                "reply": reply,
                "model": MODEL,
                "resolution_source": (
                    "LLM_CACHE" if cache_hit
                    else "LIVE_INFERENCE"
                ),
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "key_id": (
                    None if cache_hit
                    else f"key_{index + 1}"
                ),
                "fallback_attempts": (
                    0 if cache_hit
                    else failed_attempts
                )
            }

               
        except (
            RateLimitError,
            ServiceUnavailableError,
            InternalServerError,
            BadGatewayError
        ) as error:
            failed_attempts += 1

            print(
            f"Key {index + 1} failed: "
            f"{type(error).__name__}"
        )

        print(
            "Provider HTTP status:",
            getattr(error, "status_code", None)
        )

    raise AllProvidersUnavailable(
        "all providers unavailable"
    )
    

