
import os
from pathlib import Path

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
)
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from rag_utils.faiss_utils import (
    add_document,
    answer_question,
    list_documents,
    delete_document,
)
from rag_utils.document_loader import (
    extract_text,
    SUPPORTED_EXTENSIONS,
)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("Set FLASK_SECRET_KEY in your .env file.")

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS
}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/manage")
def manage():
    return render_template(
        "manage.html",
        documents=list_documents(),
    )


@app.post("/upload")
def upload():
    uploaded_files = request.files.getlist("files")

    if not uploaded_files or all(
        not file.filename for file in uploaded_files
    ):
        flash("Please select at least one document.")
        return redirect(url_for("manage"))

    added = []
    errors = []

    for file in uploaded_files:
        if not file.filename:
            continue

        if not allowed_file(file.filename):
            errors.append(
                f"{file.filename}: unsupported file format."
            )
            continue

        filename = secure_filename(file.filename)

        if not filename:
            errors.append("Invalid filename.")
            continue

        try:
            file_bytes = file.read()

            # Extract text from TXT, PDF, DOCX, CSV, MD, or HTML.
            text = extract_text(filename, file_bytes).strip()

            if not text:
                errors.append(
                    f"{filename}: no readable text found."
                )
                continue

            # Index extracted text through the existing RAG pipeline.
            add_document(filename, text)

            # Save original only after successful indexing.
            destination = UPLOAD_DIR / filename
            destination.write_bytes(file_bytes)

            added.append(filename)

        except Exception as exc:
            app.logger.exception(
                "Failed to process %s", filename
            )
            errors.append(
                f"{filename}: processing failed ({exc})."
            )

    if added:
        flash("Successfully indexed: " + ", ".join(added))

    if errors:
        flash(" | ".join(errors))

    return redirect(url_for("manage"))


@app.post("/delete/<path:filename>")
def delete(filename):
    safe_name = secure_filename(filename)

    delete_document(safe_name)
    (UPLOAD_DIR / safe_name).unlink(missing_ok=True)

    flash(f"Deleted {safe_name} from the document store.")
    return redirect(url_for("manage"))


@app.post("/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    history = payload.get("history") or []

    if not question:
        return jsonify({
            "answer": "Please enter a question.",
            "sources": [],
        }), 400

    try:
        answer, sources = answer_question(question, history)

        return jsonify({
            "answer": answer,
            "sources": sources,
        })

    except Exception:
        app.logger.exception("Chat request failed")

        return jsonify({
            "answer": (
                "Sorry, the request failed. "
                "Check the server terminal for details."
            ),
            "sources": [],
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        debug=False,
    )
