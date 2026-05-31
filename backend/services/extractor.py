"""Extract raw text from uploaded financial documents (PDF / CSV / TXT)."""
from __future__ import annotations

import io
from pathlib import Path
from typing import List

import pandas as pd
import pdfplumber


def _extract_pdf(data: bytes) -> str:
    parts: List[str] = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            parts.append(f"\n--- PDF Page {i + 1} ---\n{text}")
            # also pull tables when available
            try:
                tables = page.extract_tables() or []
                for t_idx, table in enumerate(tables):
                    rows = ["\t".join((cell or "") for cell in row) for row in table]
                    parts.append(
                        f"\n[PDF Page {i + 1} Table {t_idx + 1}]\n" + "\n".join(rows)
                    )
            except Exception:
                pass
    return "\n".join(parts)


def _extract_csv(data: bytes) -> str:
    try:
        df = pd.read_csv(io.BytesIO(data))
    except Exception:
        df = pd.read_csv(io.BytesIO(data), encoding="latin-1", engine="python")
    # limit size: 200 rows is enough for the LLM
    if len(df) > 200:
        df = df.head(200)
    return "[CSV CONTENT]\n" + df.to_csv(index=False)


def _extract_txt(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1", errors="ignore")


def extract_text(filename: str, data: bytes) -> str:
    """Dispatch on file extension and return cleaned text."""
    ext = Path(filename).suffix.lower()
    header = f"\n========== FILE: {filename} ==========\n"
    if ext == ".pdf":
        return header + _extract_pdf(data)
    if ext == ".csv":
        return header + _extract_csv(data)
    if ext in {".txt", ".md", ".text"}:
        return header + _extract_txt(data)
    # fallback: try text
    return header + _extract_txt(data)


def extract_many(files: List[tuple[str, bytes]]) -> str:
    chunks = [extract_text(name, blob) for name, blob in files]
    combined = "\n\n".join(chunks)
    # hard cap to keep LLM context manageable (Groq free tier ~12k TPM)
    if len(combined) > 14000:
        combined = combined[:14000] + "\n...[truncated]"
    return combined
