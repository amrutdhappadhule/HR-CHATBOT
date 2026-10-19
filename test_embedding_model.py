from dotenv import load_dotenv
from rag_utils.embedding import embed_texts

load_dotenv()

try:
    vectors = embed_texts(["Annual leave requires manager approval."])
    print("Embedding test successful!")
    print("Vector dimensions:", len(vectors[0]))
except Exception as e:
    print("Embedding test failed:")
    print(e)