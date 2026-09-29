"""
formatting/html_formatter.py
Converts raw AI-generated document text into styled HTML for the
Streamlit dark-mode preview card.
"""

import html

from utils.sanitize import sanitize_text


def format_html_preview(text: str) -> str:
    text = sanitize_text(text)
    parts = []
    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            parts.append("<br>")
            continue
        if line.startswith("## "):
            parts.append(f"<h2 style='color:#f5f5f5;margin:10px 0 4px;'>{html.escape(line[3:])}</h2>")
        elif line.startswith("### "):
            parts.append(f"<h3 style='color:#e6e6e6;margin:8px 0 4px;'>{html.escape(line[4:])}</h3>")
        elif line.startswith("**") and line.endswith("**") and len(line) > 4:
            parts.append(f"<p style='font-weight:bold;color:#f5f5f5;margin:4px 0;'>{html.escape(line.strip('*'))}</p>")
        else:
            parts.append(f"<p style='color:#cfcfcf;margin:4px 0;line-height:1.5;'>{html.escape(line)}</p>")
    return "".join(parts)
