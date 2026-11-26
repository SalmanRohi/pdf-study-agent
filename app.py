"""PDF Study Agent: upload PDFs and ask questions. Answers cite page numbers."""

import streamlit as st

from ai_utils import ask_with_context
from pdf_utils import build_chunks, extract_pages, search_chunks

st.set_page_config(page_title="PDF Study Agent", page_icon="📚", layout="centered")

# Session state keeps uploaded documents and chat history while the app is open.
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "documents" not in st.session_state:
    st.session_state.documents = {}
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("📚 PDF Study Agent")
st.caption("Upload your study PDFs, then ask questions. Answers include page numbers.")

# ---- Upload section (in the sidebar; on phones, tap the ">" arrow at the top left) ----
with st.sidebar:
    st.header("Your PDFs")
    uploaded_files = st.file_uploader(
        "Upload one or more PDFs", type="pdf", accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded in uploaded_files:
            if uploaded.name in st.session_state.documents:
                continue
            with st.spinner(f"Reading {uploaded.name}..."):
                pages = extract_pages(uploaded.getvalue())
                text_pages = [p for p in pages if p["text"]]
                if not text_pages:
                    st.warning(
                        f"{uploaded.name} has no readable text. It may be a scanned PDF. "
                        "Scanned-PDF support (OCR) is planned for a later version."
                    )
                    st.session_state.documents[uploaded.name] = {"pages": 0}
                    continue
                st.session_state.chunks.extend(build_chunks(pages, uploaded.name))
                st.session_state.documents[uploaded.name] = {"pages": len(pages)}

    if st.session_state.documents:
        st.subheader("Loaded documents")
        for name, info in st.session_state.documents.items():
            st.write(f"• {name} ({info['pages']} pages)")

        if st.button("Clear all PDFs and chat"):
            st.session_state.chunks = []
            st.session_state.documents = {}
            st.session_state.messages = []
            st.rerun()

# ---- Chat section ----
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("Passages used"):
                for src in message["sources"]:
                    st.markdown(f"**{src['doc']}, page {src['page']}**")
                    st.caption(src["text"])

if not st.session_state.chunks:
    st.info("Upload a PDF from the sidebar to start. On a phone, tap the ＞ arrow at the top left.")

question = st.chat_input(
    "Ask a question about your PDFs",
    disabled=not st.session_state.chunks,
)

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    passages = search_chunks(question, st.session_state.chunks, top_k=6)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = ask_with_context(question, passages)
            except Exception as error:
                answer = (
                    "Sorry, something went wrong while contacting Gemini.\n\n"
                    f"Details: {error}\n\n"
                    "If this mentions a quota or 429 error, wait a minute and try again."
                )
        st.markdown(answer)
        with st.expander("Passages used"):
            if passages:
                for src in passages:
                    st.markdown(f"**{src['doc']}, page {src['page']}**")
                    st.caption(src["text"])
            else:
                st.write("No matching passages were found.")

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": passages}
    )
