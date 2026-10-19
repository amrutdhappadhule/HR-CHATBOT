
import os
from openai import OpenAI


def _client():
    endpoint = os.getenv(
        "AZURE_OPENAI_EMBEDDING_ENDPOINT", ""
    ).strip().rstrip("/")

    key = os.getenv(
        "AZURE_OPENAI_EMBEDDING_KEY", ""
    ).strip()

    if not endpoint or not key:
        raise RuntimeError(
            "Set AZURE_OPENAI_EMBEDDING_ENDPOINT and "
            "AZURE_OPENAI_EMBEDDING_KEY in .env."
        )

    base_url = (
        endpoint
        if endpoint.endswith("/openai/v1")
        else f"{endpoint}/openai/v1"
    )

    return OpenAI(
        base_url=base_url + "/",
        api_key=key
    )


def embed_texts(texts):
    if not texts:
        return []

    deployment = os.getenv(
        "AZURE_OPENAI_EMBEDDING_MODEL", ""
    ).strip()

    if not deployment:
        raise RuntimeError(
            "Set AZURE_OPENAI_EMBEDDING_MODEL in .env."
        )

    response = _client().embeddings.create(
        model=deployment,
        input=texts
    )

    return [item.embedding for item in response.data]
