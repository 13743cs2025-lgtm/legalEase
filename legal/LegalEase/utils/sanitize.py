"""
utils/sanitize.py
Cleans AI-generated text of characters that break DOCX/PDF/plain-text export
(typographic quotes, emoji, stray unicode, etc.).
"""

import re

_REPLACEMENTS = {
    "\u2018": "'", "\u2019": "'",   # curly single quotes
    "\u201c": '"', "\u201d": '"',   # curly double quotes
    "\u2013": "-", "\u2014": "-",   # en/em dash
    "\u2026": "...",                 # ellipsis
    "\u00a0": " ",                    # non-breaking space
}


def sanitize_text(text: str) -> str:
    """Normalize quotes/dashes and strip characters unsupported by the
    default PDF font (fpdf2's core fonts are Latin-1 only)."""
    if not text:
        return ""
    for old, new in _REPLACEMENTS.items():
        text = text.replace(old, new)
    # Drop anything outside printable ASCII + newline/tab to keep PDF/DOCX safe
    text = re.sub(r"[^\x09\x0A\x20-\x7E]+", "", text)
    return text.strip()
