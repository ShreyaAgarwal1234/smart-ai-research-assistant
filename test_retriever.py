"""
Run:  python test_retriever.py
Expect: 3 different chunks printed, most‑related first.
"""

from app.retriever import create_faiss_index, retrieve_chunks

text = (
    "Artificial Intelligence is transforming industries.\n\n"
    "It includes areas like NLP, computer vision, and robotics.\n\n"
    "Machine learning is a subset of AI that learns patterns from data.\n\n"
    "AI can help automate tasks, improve decision‑making, and boost efficiency."
)

chunks, _, index = create_faiss_index(text)
print("Chunks created:", len(chunks))

question = "What is machine learning?"
top_chunks = retrieve_chunks(question, index, chunks)

print("\nTop relevant chunks:")
for chunk in top_chunks:
    print("-", chunk)
