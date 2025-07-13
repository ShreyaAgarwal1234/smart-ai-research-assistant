"""
retriever.py
------------
Embeds document chunks and searches for the most relevant ones using FAISS.
Works even if the source text has no blank lines.
"""

from typing import List, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# ────────────────────────────────────────────────────────────────────────────────
# Load embedder once
EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
EMB_DIM = EMBED_MODEL.get_sentence_embedding_dimension()
# ────────────────────────────────────────────────────────────────────────────────


def chunk_text(text: str, max_chars: int = 500) -> List[str]:
    """
    Split on blank lines; if that yields <2 chunks, fall back to single lines.
    No re‑merging, so each paragraph stays distinct.
    """
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    if len(paras) < 2:  # fallback
        paras = [p.strip() for p in text.splitlines() if p.strip()]

    # Hard cap: if any single paragraph > max_chars, break it up
    chunks = []
    for para in paras:
        while len(para) > max_chars:
            chunks.append(para[:max_chars])
            para = para[max_chars:]
        chunks.append(para)
    return chunks



def create_faiss_index(text: str) -> Tuple[List[str], np.ndarray, faiss.IndexFlatL2]:
    """
    Return text chunks, their embeddings, and a FAISS index you can search.
    """
    chunks = chunk_text(text)
    embeddings = (
        EMBED_MODEL.encode(chunks, convert_to_numpy=True).astype("float32")
    )
    index = faiss.IndexFlatL2(EMB_DIM)
    index.add(embeddings)
    return chunks, embeddings, index


def retrieve_chunks(
    question: str,
    index: faiss.IndexFlatL2,
    chunks: List[str],
    top_k: int = 3,
) -> List[str]:
    """
    Return top‑k chunks relevant to the user's question.
    """
    q_vec = (
        EMBED_MODEL.encode([question], convert_to_numpy=True).astype("float32")
    )
    distances, indices = index.search(q_vec, top_k)
    return [chunks[i] for i in indices[0]]



from transformers import pipeline

qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

def answer_question_with_justification(question, chunks):
    if not chunks:
        return {
            "answer": "",
            "confidence": 0.0,
            "justification": {
                "paragraph": -1,
                "text": "No relevant chunk found."
            }
        }

    best_chunk = chunks[0]  # Top chunk
    paragraph_number = chunks.index(best_chunk) + 1  # 1-based index

    result = qa_pipeline(question=question, context=best_chunk)

    return {
        "answer": result["answer"],
        "confidence": result["score"],
        "justification": {
            "paragraph": paragraph_number,
            "text": best_chunk
        }
    }
