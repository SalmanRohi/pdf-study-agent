"""Sends the question and retrieved PDF passages to Gemini."""

import os

import streamlit as st
from google import genai

# Change this if Google retires the model. Check the current name in AI Studio.
MODEL_NAME = "gemini-3.8-flash"


def get_api_key() -> str | None:
    """Read the key from Streamlit secrets (online) or an environment variable (local)."""
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.environ.get("GEMINI_API_KEY")


def ask_with_context(question: str, passages: list[dict]) -> str:
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError(
            "No Gemini API key found. Add GEMINI_API_KEY in the app's Secrets settings."
        )

    if not passages:
        return (
            "I could not find this in your uploaded PDFs. "
            "Try different keywords, or check whether the topic is in the documents."
        )

    context = "\n\n".join(
        f"[Source: {p['doc']}, page {p['page']}]\n{p['text']}" for p in passages
    )

    prompt = f"""You are a study assistant for students.

Answer the student's question using ONLY the passages below.
Rules:
- If the passages do not contain the answer, say: "The uploaded PDFs do not seem to cover this."
- After each fact, cite its source in this exact form: (Source: document name, page N).
- Use only page numbers that appear in the passages. Never invent a page number.
- Keep the answer clear and simple.

PASSAGES:
{context}

STUDENT QUESTION:
{question}
"""

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return response.text or "The model returned an empty answer. Please try again."
