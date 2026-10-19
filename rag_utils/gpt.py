import os
from openai import OpenAI

def _client():
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip().rstrip("/")
    key = os.getenv("AZURE_OPENAI_KEY", "").strip()
    if not endpoint or not key:
        raise RuntimeError("Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY in .env.")
    base_url = endpoint if endpoint.endswith("/openai/v1") else f"{endpoint}/openai/v1"
    return OpenAI(base_url=base_url + "/", api_key=key)

def generate_answer(question, context, history=None):
    deployment = os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT", "").strip()
    if not deployment:
        raise RuntimeError("Set AZURE_OPENAI_GPT_DEPLOYMENT to your chat deployment name.")
    messages = [
        {"role": "system", "content": (
            "You are a helpful HR policy assistant. Answer using the supplied policy context. "
            "If the context does not contain the answer, say you could not find it in the uploaded HR documents. "
            "Do not invent company policies."
        )}
    ]
    for item in (history or [])[-8:]:
        role = item.get("role")
        content = item.get("content")
        if role in {"user", "assistant"} and isinstance(content, str):
            messages.append({"role": role, "content": content[:4000]})
    messages.append({"role": "user", "content": f"Policy context:\n{context or '(No matching policy documents found.)'}\n\nQuestion: {question}"})
    result = _client().chat.completions.create(model=deployment, messages=messages, temperature=0.2)
    return result.choices[0].message.content or "I couldn't generate an answer."
