from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT").rstrip("/")
key = os.getenv("AZURE_OPENAI_KEY")
deployment = os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT")

client = OpenAI(
    base_url=f"{endpoint}/openai/v1/",
    api_key=key
)

response = client.chat.completions.create(
    model=deployment,
    messages=[
        {"role": "user", "content": "Say hello in one sentence."}
    ]
)

print(response.choices[0].message.content)