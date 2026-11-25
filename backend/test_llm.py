
from llm_service import (
    generate_response,
    AllProvidersUnavailable
)

messages = [
    {
        "role": "user",
        "content": "What is the capital of France?"
    }
]

try:
    result = generate_response(messages)

    print("\nReply:", result["reply"])
    print("Model:", result["model"])
    print("Input tokens:", result["input_tokens"])
    print("Output tokens:", result["output_tokens"])
    print("Key used:", result["key_id"])
    print(
        "Fallback attempts:",
        result["fallback_attempts"]
    )

except AllProvidersUnavailable:
    print(
        "Both API keys failed. "
        "All providers unavailable."
    )
