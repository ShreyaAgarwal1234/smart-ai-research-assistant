# test_summary.py  – place in project root
from app.summarizer import generate_summary
sample = "Artificial intelligence (AI) is transforming industries..." * 20
print(generate_summary(sample))
