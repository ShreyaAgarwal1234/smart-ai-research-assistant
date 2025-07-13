# ui/streamlit_app.py
import streamlit as st
import requests

BACKEND = "http://127.0.0.1:8000"   # fastapi base‑url

st.set_page_config(page_title="Smart AI Assistant", layout="centered")
st.title("🤖 Smart AI Research Assistant")

# ──────────────────────────────────────────────────────────────────────────────
# 1) Upload a document
# ──────────────────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("Upload a .txt or .pdf file", type=["txt", "pdf"])

if uploaded_file:
    with st.spinner("Uploading and processing…"):
        res = requests.post(f"{BACKEND}/upload", files={"file": uploaded_file})
    if res.status_code != 200:
        st.error("Upload failed. Try again.")
        st.stop()

    data   = res.json()
    doc_id = data["doc_id"]

    st.success("Document uploaded successfully ✅")
    st.write("### 📄 Auto‑Summary")
    st.info(data["summary"])

    # ──────────────────────────────────────────────────────────────────────────
    # 2) Ask Anything mode
    # ──────────────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("❓ Ask Anything")
    question = st.text_input("Type your question…")
    if st.button("Get Answer"):
        with st.spinner("Thinking…"):
            ask_url = f"{BACKEND}/ask?doc_id={doc_id}&question={question}"
            ans_res = requests.get(ask_url).json()

        st.write("### ✅ Answer")
        st.success(ans_res["answer"])
        st.caption(f"Confidence {round(ans_res['confidence']*100,2)} %")

        st.write(
            f"**Justification (Paragraph {ans_res['justification']['paragraph']}):**"
        )
        st.code(ans_res["justification"]["text"])

    # ──────────────────────────────────────────────────────────────────────────
    # 3) Challenge Me mode
    # ──────────────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🧠 Challenge Me")

    if st.button("Generate 3 Questions"):
        with st.spinner("Generating questions…"):
            q_res = requests.post(f"{BACKEND}/challenge", params={"doc_id": doc_id})
        if q_res.status_code != 200:
            st.error("Failed to generate questions.")
            st.stop()

        st.session_state.challenge_qs = q_res.json()["questions"]
        st.success("Questions ready!")

    # Show questions & collect answers
    if "challenge_qs" in st.session_state:
        answers = []
        for i, q in enumerate(st.session_state.challenge_qs):
            st.markdown(f"**Q{i+1}: {q}**")
            ans = st.text_input(f"Your answer:", key=f"ans_{i}")
            answers.append(ans)

        if st.button("Submit Answers"):
            payload = {
                "doc_id":    doc_id,
                "questions": st.session_state.challenge_qs,
                "answers":   answers,
            }
            with st.spinner("Evaluating…"):
                eval_res = requests.post(f"{BACKEND}/challenge/evaluate", json=payload)
            if eval_res.status_code != 200:
                st.error("Evaluation failed.")
            else:
                for result in eval_res.json()["results"]:
                    st.markdown(f"**Q:** {result['question']}")
                    st.write(f"**Your Answer:** {result['your_answer']}")
                    st.write(f"**Feedback:** {result['feedback']}")
                    st.write("**Justification:**")
                    st.code(result["justification"])
                    st.markdown("---")
