"""
summarizer.py
-------------
Generates a ≤150‑word summary using a pre‑trained BART model.
"""

from transformers import pipeline

# Load once – this will download the model the first time (~500 MB)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def generate_summary(text: str) -> str:
    """
    Returns a concise summary of the first 3,000 chars (to stay in model limit).
    """
    input_text = text[:3000]  # truncate very long docs
    result = summarizer(
        input_text,
        max_length=150,
        min_length=60,
        do_sample=False,
    )
    return result[0]["summary_text"]
