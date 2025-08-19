import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from pathlib import Path
import pickle

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def smart_chunk(text: str, max_chars: int = 1000, min_chars: int = 300):
    """Divide texto en fragmentos preservando coherencia"""
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks, current = [], ""
    for para in paragraphs:
        if len(current) + len(para) <= max_chars:
            current += " " + para
        else:
            if len(current) >= min_chars:
                chunks.append(current.strip())
                current = para
            else:
                current += " " + para
    if current:
        chunks.append(current.strip())
    return chunks

def embed_chunks(chunks):
    """Genera embeddings de los fragmentos"""
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return model.encode(chunks, normalize_embeddings=True).astype("float32")

def build_faiss_index(embeddings):
    """Crea un índice FAISS"""
    d = embeddings.shape[1]
    index = faiss.IndexFlatIP(d)  # similaridad por producto interno
    index.add(embeddings)
    return index

def save_index(chat_id, index, chunks):
    """Guarda índice FAISS y metadatos"""
    faiss.write_index(index, str(DATA_DIR / f"{chat_id}.index"))
    with open(DATA_DIR / f"{chat_id}.pkl", "wb") as f:
        pickle.dump(chunks, f)

def load_index(chat_id):
    """Carga índice y fragmentos"""
    index_path = DATA_DIR / f"{chat_id}.index"
    chunks_path = DATA_DIR / f"{chat_id}.pkl"
    if not index_path.exists() or not chunks_path.exists():
        return None, None
    index = faiss.read_index(str(index_path))
    with open(chunks_path, "rb") as f:
        chunks = pickle.load(f)
    return index, chunks

def search_chunks(chat_id, query, top_k=5):
    """Busca fragmentos relevantes"""
    index, chunks = load_index(chat_id)
    if not index:
        return []
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    q_emb = model.encode([query], normalize_embeddings=True).astype("float32")
    distances, ids = index.search(q_emb, top_k)
    return [chunks[i] for i in ids[0]]
