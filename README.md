# HR Assistant RAG Chatbot

A document-based RAG chatbot built with Flask, Azure OpenAI, and FAISS. Upload documents, ask questions about their contents, and receive answers with source references.

## Features

- Retrieval-Augmented Generation (RAG) using FAISS vector similarity search.
- Azure OpenAI integration for chat responses and text embeddings.
- Multiple document uploads.
- Supported formats: TXT, PDF, DOCX, CSV, Markdown, and HTML.
- Document management, including upload and deletion.
- Source references in chatbot responses.
- Flask-based web interface.
- Docker support for local containerized execution.

## Tech Stack

- **Backend:** Python, Flask
- **LLM:** Azure OpenAI GPT-4o
- **Embeddings:** Azure OpenAI `text-embedding-3-small`
- **Vector search:** FAISS
- **Document processing:** pypdf, python-docx, Beautiful Soup
- **Containerization:** Docker
- **Version control:** Git and GitHub

## 1. Local Setup (Windows PowerShell)

Clone the repository:

```powershell
git clone https://github.com/amrutdhappadhule/HR-CHATBOT.git
cd HR-CHATBOT
```

Create and activate a virtual environment:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Configure `.env` with your own Azure OpenAI endpoints, API keys, deployment names, and Flask secret key. Use the variable names expected by the application code.

**Never commit `.env` or expose API keys in source code.**

## 2. Azure OpenAI Configuration

Configure two Azure OpenAI deployments:

- **Chat deployment:** GPT-4o, or another compatible chat model.
- **Embedding deployment:** `text-embedding-3-small`, or another compatible embedding model.

The deployment names in `.env` must match the actual deployment names in your Azure resource. Follow the API configuration expected by the installed OpenAI SDK and your application code.

## 3. Run Locally

Start the Flask application:

```powershell
python main.py
```

Open the application:

- Chat interface: http://localhost:8000
- Document management: http://localhost:8000/manage

Upload supported documents, ask questions about their contents, and inspect the returned source references.

## 4. How the RAG Pipeline Works

1. The user uploads a document.
2. The document loader extracts its text.
3. The text is split into smaller chunks.
4. Azure OpenAI converts the chunks into numerical embeddings.
5. FAISS indexes the vectors for similarity search.
6. A user submits a question.
7. The application retrieves relevant chunks from the index.
8. GPT-4o generates an answer using the retrieved context.

The exact chunk size, overlap, retrieval count, and index persistence behavior depend on the current implementation in `rag_utils/`.

## 5. Docker

Build the Docker image:

```powershell
docker build -t hr-assistant-rag:latest .
```

Run the container locally:

```powershell
docker run -d --name hr-assistant-rag -p 8000:8000 --env-file .env hr-assistant-rag:latest
```

Open http://localhost:8000.

Check logs:

```powershell
docker logs hr-assistant-rag
```

Stop the container:

```powershell
docker stop hr-assistant-rag
```

## 6. Storage and Limitations

- Uploaded documents and vector index files may be stored locally, depending on the application configuration.
- Container filesystems are not a substitute for durable cloud storage. Configure persistent storage before relying on uploaded documents across container replacements.
- If the embedding model changes, rebuild the index using the new embedding model.
- Scanned PDFs may require OCR if their pages do not contain extractable text.
- This project is a learning and portfolio project, not a hardened multi-user HR system.

Before using real employee information, implement authentication, authorization, appropriate privacy controls, secure document access, monitoring, and reliable persistent storage.

## 7. Security

- Keep `.env` out of Git.
- Never include real API keys, passwords, or secret values in the README.
- Configure cloud secrets through the hosting platform's secure environment settings.
- Validate uploaded files and enforce suitable upload size limits.

## Project Status

The Flask application and Docker image have been tested locally. The project has been pushed to GitHub. Cloud deployment and automated CI/CD are not currently configured.
