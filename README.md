&nbsp;Smart AI Research Assistant



This is a full-stack NLP-based project built as part of a company assignment to develop an intelligent research assistant. The assistant can summarize documents, answer user questions with justification, and evaluate comprehension through generated questions.



---



&nbsp;Key Features



Auto-Summary : Generates a concise summary from uploaded PDF or TXT files

Ask Anything : Accepts natural language questions and answers from document context

Justified Answers : Includes relevant paragraph number and confidence score

Challenge Me : Automatically generates 3 document-based questions and evaluates user responses with feedback

Semantic Search : FAISS-powered retrieval for document grounding

Minimal Hallucination : All answers are strictly based on uploaded document



---



&nbsp;Tech Stack



| Layer      | Tools Used                            

|------------|--------------------------------------

| Frontend   | Streamlit                            

| Backend    | FastAPI                              

| NLP Models | Hugging Face Transformers (BART, RoBERTa, MiniLM) 

| Retrieval  | FAISS (semantic chunk search)        

| Parsing    | pdfplumber                           

| Deployment | GitHub                                



---



&nbsp;How to Run the Project Locally



&nbsp;1. Clone the repository



```bash

git clone https://github.com/ShreyaAgarwal1234/smart-ai-research-assistant.git

cd smart-ai-research-assistant

