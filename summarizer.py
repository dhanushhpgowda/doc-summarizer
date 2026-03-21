"""
summarizer.py - AI Summarization via Groq
==========================================
Two-pass chunking pipeline for documents of ANY length.

  Pass 1 - Chunk summarization:
      Split the full text into overlapping chunks (~6 000 chars each).
      Summarize every chunk independently -> list of partial summaries.

  Pass 2 - Merge summarization:
      Feed ALL partial summaries together to the LLM and ask it to
      produce one final, structured, holistic summary of the whole doc.
"""

import logging
import time
from groq import Groq

logger = logging.getLogger(__name__)

# ── Tuning constants ──────────────────────────────────────────────────────────
CHUNK_SIZE     = 6_000   # chars per chunk (~1 500 tokens)
CHUNK_OVERLAP  = 400     # overlap to avoid cutting ideas mid-sentence
MAX_CHUNKS     = 40      # hard cap to prevent runaway API calls on huge docs
RETRY_ATTEMPTS = 3       # retries on transient Groq errors
RETRY_DELAY    = 2       # seconds between retries


# ── System prompts ────────────────────────────────────────────────────────────

CHUNK_SYSTEM_PROMPT = """You are an expert document analyst.
You will receive a SECTION of a larger document.
Extract the most important information from this section only.
Be concise. Output plain prose - no headers needed.
Do NOT fabricate any information."""

FINAL_SYSTEM_PROMPT = """You are an expert document analyst and summarizer.
Your job is to produce clear, structured, insightful summaries for any document provided.

Always follow this output format:

## 📄 Document Overview
One or two sentences describing what the whole document is about.

## 🔑 Key Points
- Bullet-point list of the most important ideas (8-12 bullets covering the ENTIRE document).

## 📊 Main Topics Covered
Brief paragraph about the primary themes or sections found across the entire document.

## 💡 Key Takeaways
Three to five actionable insights or conclusions drawn from the full document.

## 📝 Summary
A concise paragraph (4-6 sentences) summarising the entire document end-to-end.

Be accurate, professional, and thorough. Represent the FULL document, not just the beginning.
Do not fabricate information."""


# ── Internal helpers ──────────────────────────────────────────────────────────

def _split_into_chunks(text):
    """
    Split text into overlapping chunks of ~CHUNK_SIZE characters.
    Tries to break on paragraph/sentence boundaries so context is preserved.
    """
    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + CHUNK_SIZE, length)

        # Prefer to break on a newline or period near the end of the window
        if end < length:
            split_at = text.rfind('\n', start + CHUNK_SIZE - 300, end)
            if split_at == -1:
                split_at = text.rfind('. ', start + CHUNK_SIZE - 300, end)
            if split_at != -1:
                end = split_at + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Advance with overlap so we don't cut context cold
        start = end - CHUNK_OVERLAP if end < length else length

    return chunks[:MAX_CHUNKS]


def _call_groq(client, model, system, user, max_tokens=512):
    """Call Groq with simple retry logic for transient failures."""
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
                temperature=0.3,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            logger.warning("Groq attempt %d/%d failed: %s", attempt, RETRY_ATTEMPTS, exc)
            if attempt < RETRY_ATTEMPTS:
                time.sleep(RETRY_DELAY)
            else:
                raise RuntimeError(f"Groq API failed: {exc}") from exc


# ── Public API ────────────────────────────────────────────────────────────────

def summarize(text: str, api_key: str, model: str = "llama-3.3-70b-versatile") -> str:
    """
    Summarize a document of ANY length using a chunk -> merge pipeline.

    Args:
        text:    Full extracted document text (no length limit imposed here).
        api_key: Groq API key.
        model:   Groq model identifier.

    Returns:
        Markdown-formatted final summary covering the entire document.

    Raises:
        RuntimeError: If the API key is missing or all API calls fail.
    """
    if not api_key:
        raise RuntimeError(
            "Groq API key is not configured. "
            "Please set GROQ_API_KEY in your .env file."
        )

    client = Groq(api_key=api_key)
    text = text.strip()

    # ── Short document: single call, no chunking needed ──────────────────
    if len(text) <= CHUNK_SIZE:
        logger.info("Short document (%d chars) – single-pass summarization.", len(text))
        return _call_groq(
            client, model,
            system=FINAL_SYSTEM_PROMPT,
            user=f"Please summarize the following document:\n\n---\n{text}\n---",
            max_tokens=1024,
        )

    # ── Long document: chunk -> partial summaries -> final merge ─────────
    chunks = _split_into_chunks(text)
    logger.info(
        "Large document (%d chars) split into %d chunks – starting chunk summarization.",
        len(text), len(chunks),
    )

    # Pass 1: summarize each chunk individually
    partial_summaries = []
    for i, chunk in enumerate(chunks, start=1):
        logger.info("Summarizing chunk %d / %d …", i, len(chunks))
        partial = _call_groq(
            client, model,
            system=CHUNK_SYSTEM_PROMPT,
            user=(
                f"This is section {i} of {len(chunks)} from a larger document.\n\n"
                f"---\n{chunk}\n---\n\n"
                f"Extract the key information from this section."
            ),
            max_tokens=400,
        )
        partial_summaries.append(f"[Section {i}]\n{partial}")
        # Small pause to stay within Groq rate limits
        if i < len(chunks):
            time.sleep(0.3)

    # Pass 2: merge all partial summaries into one final structured summary
    logger.info("All chunks done – running final merge summarization.")
    merged_notes = "\n\n".join(partial_summaries)

    # If merged notes are still huge, truncate to fit context window
    if len(merged_notes) > 24_000:
        merged_notes = merged_notes[:24_000] + "\n\n[... additional sections omitted ...]"

    return _call_groq(
        client, model,
        system=FINAL_SYSTEM_PROMPT,
        user=(
            f"Below are section-level notes extracted from a {len(chunks)}-section document.\n"
            f"Use ALL of them to write one complete, coherent summary of the ENTIRE document.\n\n"
            f"---\n{merged_notes}\n---"
        ),
        max_tokens=1200,
    )