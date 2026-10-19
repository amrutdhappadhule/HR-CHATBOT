# HR Assistant RAG Chatbot

A compact Flask + Azure OpenAI + FAISS RAG chatbot for `.txt` HR policy documents.

## 1. Local setup (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` with your own Azure endpoint, key, and **deployment names**. Never commit `.env`.

## 2. Azure deployments

Create one chat deployment and one embedding deployment in your own Azure resource. Deployment names in `.env` must match the names shown in Azure. Endpoint format depends on your resource; this starter uses the Azure OpenAI-compatible `/openai/v1/` API. Verify your resource supports this endpoint style before testing.

## 3. Run

```powershell
python main.py
```

Open http://localhost:8000. Upload `.txt` HR policy documents at `/manage`, then ask questions in the chat.

## 4. Important behavior

- Documents are split into character chunks (500 characters, 80-character overlap).
- The app embeds chunks, stores normalized vectors in a FAISS inner-product index, and retrieves up to four chunks per question.
- Uploaded source files and FAISS data are local. They are ignored by Git. Rebuild the index after changing the embedding model.
- This is a learning starter, not a hardened multi-user HR system. Add authentication, authorization, persistent storage, request limits, monitoring, and privacy controls before production use.
- Chat history is sent by the browser; do not treat it as trusted or confidential server-side state.

## 5. Docker

```powershell
docker build -t hr-assistant-rag .
docker run --rm -p 8000:8000 --env-file .env hr-assistant-rag
```

For cloud deployment, persist `data/uploads` and `vector_db` using a durable storage design before relying on uploaded documents across container replacements.
