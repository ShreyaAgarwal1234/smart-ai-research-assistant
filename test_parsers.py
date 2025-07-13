import io
from types import SimpleNamespace
from app.parsers import parse_document

# Fake in‑memory TXT file for a quick check
dummy_text = b"First paragraph.\n\nSecond paragraph (testing)."

# SimpleNamespace mimics FastAPI's UploadFile for this test
fake_file = SimpleNamespace(filename="demo.txt", file=io.BytesIO(dummy_text))

text, page_map = parse_document(fake_file)

print("=== Extracted Text ===")
print(text)
print("\n=== Paragraph‑to‑page map ===")
print(page_map)

