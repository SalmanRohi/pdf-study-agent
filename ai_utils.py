"""Sends the question and retrieved PDF passages to Groq."""

import os
import time

import streamlit as st
from groq import Groq

# If Groq retires this model, change this one line.
MODEL_NAME = "openai/gpt-oss-120b"
RETRIES = 2


def get_api_key() -> str | None:
    """Read the key from Streamlit secrets (online) or an environment variable (local)."""
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.environ.get("GROQ_API_KEY")


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
            "No Groq API key found. Add GROQ_API_KEY in the app's Secrets settings."
        )

    if not passages:
        return (
            "I could not find this in your uploaded PDFs. "
            "Try different keywords, or check whether the topic is in the documents."
        )

    client = Groq(api_key=api_key)
    prompt = build_prompt(question, passages)

    last_error = None
    for attempt in range(RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
            )
            answer = response.choices[0].message.content
            return answer or "The model returned an empty answer. Please try again."
        except Exception as error:
            last_error = error
            if attempt < RETRIES:
                time.sleep(2)  # short pause, then one more try
    raise RuntimeError(f"Groq did not answer: {last_error}")
