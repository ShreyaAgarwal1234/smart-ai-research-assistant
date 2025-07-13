"""
parsers.py
----------
Reads PDF or TXT and returns:
  - full text
  - paragraph‑to‑page mapping for justifications
Works with Python 3.13 via pdfplumber (pure‑Python).
"""

import io
from typing import Tuple, Dict, List

import pdfplumber


def _parse_pdf(file_bytes: bytes) -> Tuple[str, Dict[int, int]]:
    """
    Extract text from a PDF, keeping page numbers.
    """
    paragraphs: List[str] = []
    page_map: Dict[int, int] = {}

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text(x_tolerance=1.5) or ""
            for para in [p.strip() for p in page_text.split("\n\n") if p.strip()]:
                page_map[len(paragraphs)] = page_num
                paragraphs.append(para)

    return "\n\n".join(paragraphs), page_map


def _parse_txt(file_bytes: bytes) -> Tuple[str, Dict[int, int]]:
    """
    Simple TXT reader (no pages, page = 1).
    """
    text = file_bytes.decode("utf-8", errors="ignore")
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    page_map = {idx: 1 for idx in range(len(paragraphs))}
    return text, page_map


def parse_document(upload_file) -> Tuple[str, Dict[int, int]]:
    """
    Public helper. Accepts FastAPI UploadFile or any file‑like object.
    """
    file_bytes = upload_file.file.read()
    name = upload_file.filename.lower()

    if name.endswith(".pdf"):
        return _parse_pdf(file_bytes)
    elif name.endswith(".txt"):
        return _parse_txt(file_bytes)
    else:
        raise ValueError("Unsupported file type (use PDF or TXT)")
