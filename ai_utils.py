"""Sends the question and retrieved PDF passages to Gemini, with retries and fallback models."""

import os
import time

import streamlit as st
from google import genai

# The app tries these models in order. If one is busy or unavailable, it moves to the next.
MODEL_NAMES = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3.8-flash",
]

RETRIES_PER_MODEL = 3


def get_api_key() -> str | None:
    """Read the key from Streamlit secrets (online) or an environment variable (local)."""
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.environ.get("GEMINI_API_KEY")


def build_prompt(question: str, passages: list[dict]) -> str:
    context = "\n\n".join(
        f"[Source: {p['doc']}, page {p['page']}]\n{p['text']}" for p in passages
    )
    return f"""You are a study assistant for students.

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

    prompt = build_prompt(question, passages)
    client = genai.Client(api_key=api_key)
    last_error = None

    for model_name in MODEL_NAMES:
        for attempt in range(RETRIES_PER_MODEL):
            try:
                response = client.models.generate_content(model=model_name, contents=prompt)
                if response.text:
                    return response.text
                last_error = "The model returned an empty answer."
            except Exception as error:
                last_error = f"{model_name}: {error}"
                message = str(error)
                busy = "503" in message or "429" in message or "UNAVAILABLE" in message
                if not busy:
                    # A different kind of error (for example, a wrong model name).
                    # Skip the remaining retries and try the next model.
                    break
            time.sleep(2 * (attempt + 1))  # wait 2s, then 4s, then 6s

    raise RuntimeError(f"All Gemini models are busy or unavailable. Last error: {last_error}")
