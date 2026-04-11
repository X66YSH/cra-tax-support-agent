"""
LLM client configuration.
Uses the course-provided qwen3-30b-a3b-fp8 endpoint via OpenAI-compatible API.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://rsm-8430-finalproject.bjlkeng.io")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen3-30b-a3b-fp8")
LLM_API_KEY = os.getenv("LLM_API_KEY", "none")


_client = None

def get_client() -> OpenAI:
    """Return a cached OpenAI-compatible client pointed at the course endpoint."""
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=LLM_BASE_URL,
            api_key=LLM_API_KEY,
        )
    return _client


def chat(messages: list[dict], **kwargs) -> str:
    """
    Send a chat request to the LLM and return the response text.

    Args:
        messages: List of {"role": ..., "content": ...} dicts
        **kwargs: Extra params passed to the API (temperature, max_tokens, etc.)

    Returns:
        The assistant's reply as a string.
    """
    client = get_client()
    kwargs.setdefault("max_tokens", 2000)
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        **kwargs,
    )
    msg = response.choices[0].message
    # qwen3 reasoning model: actual answer is in content,
    # but if content is empty/null, fall back to reasoning_content
    content = msg.content
    if not content:
        content = getattr(msg, "reasoning_content", None) or ""
    return content


if __name__ == "__main__":
    # Quick smoke test
    reply = chat([{"role": "user", "content": "Say hello in one sentence."}])
    print(f"Model: {LLM_MODEL}")
    print(f"Response: {reply}")
