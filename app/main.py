# app/main.py
# ---------------------------------------------------------------------------
# Smart AI Research Assistant – FastAPI backend
# ---------------------------------------------------------------------------

from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Tuple

from app.parsers import parse_document           # your PDF/TXT parser
from app.summarizer import generate_summary      # 150‑word summary
from app.retriever import (
    create_faiss_index,
    retrieve_chunks,
    answer_question_with_justification           # new QA helper
)

app = FastAPI(title="Smart AI Research Assistant")

# CORS (handy if you add a Streamlit/React frontend later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In‑memory stores (simple for local testing)
# ---------------------------------------------------------------------------
DocumentStore: Dict[str, str] = {}                         # doc_id -> raw text
RetrievalStore: Dict[str, Tuple[list, any, any]] = {}      # doc_id -> (chunks, embeddings, faiss_index)
doc_counter = 1                                            # incremental id


# ---------------------------------------------------------------------------
# POST /upload  – upload PDF/TXT, auto‑summary, build embeddings
# ---------------------------------------------------------------------------
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    global doc_counter

    # 1) Parse the document
    text, page_map = parse_document(file)

    # 2) Generate a ≤150‑word summary
    summary = generate_summary(text)

    # 3) Build semantic index
    chunks, embeddings, index = create_faiss_index(text)

    # 4) Save everything in memory
    doc_id = f"doc_{doc_counter}"
    docs_db[doc_id] = text
    DocumentStore[doc_id]   = text
    RetrievalStore[doc_id]  = (chunks, embeddings, index)
    doc_counter += 1

    return {
        "doc_id": doc_id,
        "summary": summary,
        "message": "Upload and processing successful!"
    }


# ---------------------------------------------------------------------------
# GET /ask  – retrieve chunks + run extractive QA
# ---------------------------------------------------------------------------
@app.get("/ask")
def ask_question(
    doc_id: str   = Query(..., description="Document ID returned by /upload"),
    question: str = Query(..., description="Your question about the document"),
):
    # Validate doc_id
    if doc_id not in RetrievalStore:
        return {"error": f"Invalid doc_id '{doc_id}'. Upload first."}

    # 1) Retrieve top‑k relevant chunks
    chunks, embeddings, index = RetrievalStore[doc_id]
    top_chunks = retrieve_chunks(question, index, chunks, top_k=3)

    # 2) Run QA model on best chunk, get answer + confidence + justification
    result = answer_question_with_justification(question, top_chunks)

    return {
        "question":     question,
        "answer":       result["answer"],
        "confidence":   result["confidence"],
        "justification": result["justification"],
        "message":      f"Answer generated from {doc_id}."
    }
from fastapi import Request
from app.summarizer import generate_summary
from app.retriever import create_faiss_index, retrieve_chunks
from transformers import pipeline
from fastapi import FastAPI, UploadFile, File, Query, HTTPException


# Load models once
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")
gen_pipeline = pipeline("text-generation", model="gpt2")

# Store document content in memory
docs_db = {}  # e.g., docs_db["doc_1"] = full_text

@app.post("/challenge")
def challenge_mode(doc_id: str):
    text = docs_db.get(doc_id)
    if not text:
        raise HTTPException(status_code=404, detail="Document not found")

    prompt = f"Based on the following text, generate 3 logic-based or comprehension questions:\n{text[:800]}\nQuestions:"
    outputs = gen_pipeline(prompt, max_length=300, num_return_sequences=1, do_sample=True)

    raw_output = outputs[0]["generated_text"]
    questions = raw_output.split("Questions:")[-1].strip().split("\n")

    # Clean and take top 3 non-empty
    questions = [q.strip("-•123. ") for q in questions if q.strip()]
    return {"questions": questions[:3]}
from pydantic import BaseModel
from typing import List

class QAInput(BaseModel):
    doc_id: str
    questions: List[str]
    answers: List[str]
    docs_db: Dict[str, str] = {}     # add this line once


@app.post("/challenge/evaluate")
def evaluate_answers(data: QAInput):
    text = docs_db.get(data.doc_id)
    # inside /upload endpoint after you parse text
    #docs_db[doc_id] = text     # MUST be here for Challenge Mode
  
    if not text:
        raise HTTPException(status_code=404, detail="Document not found")

    chunks, embeddings, index = create_faiss_index(text)

    results = []
    for question, user_answer in zip(data.questions, data.answers):
        top_chunks = retrieve_chunks(question, index, chunks, top_k=1)
        context = top_chunks[0] if top_chunks else ""
        model_answer = qa_pipeline(question=question, context=context)["answer"]

        if user_answer.lower().strip() in model_answer.lower():
            feedback = "✅ Correct"
        else:
            feedback = f"❌ Not quite. Correct answer is: '{model_answer}'"

        results.append({
            "question": question,
            "your_answer": user_answer,
            "feedback": feedback,
            "justification": context
        })

    return {"results": results}
