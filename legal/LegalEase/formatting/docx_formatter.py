"""
formatting/docx_formatter.py
Converts raw AI-generated document text into a formatted .docx file:
logo, Times New Roman body font, heading styles, a terms table, and a footer.
"""

import io
import os

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

from config import LOGO_PATH
from utils.sanitize import sanitize_text


def _split_terms(terms: str):
    return [t.strip() for t in terms.split(";") if t.strip()]


def format_docx(text: str, doc_type: str, parties: str = "", terms: str = "", dates: str = "") -> bytes:
    """Returns the raw bytes of a generated .docx file."""
    text = sanitize_text(text)
    document = Document()

    base_style = document.styles["Normal"]
    base_style.font.name = "Times New Roman"
    base_style.font.size = Pt(11)

    if LOGO_PATH and os.path.exists(LOGO_PATH):
        logo_p = document.add_paragraph()
        logo_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = logo_p.add_run()
        try:
            run.add_picture(LOGO_PATH, width=Inches(1.5))
        except Exception:
            pass  # invalid/corrupt image — skip silently rather than fail export

    title = document.add_heading(doc_type or "Legal Document", level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    if parties:
        p = document.add_paragraph(f"Parties: {parties}")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if dates:
        p = document.add_paragraph(f"Effective Date: {dates}")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    document.add_paragraph()  # spacer

    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("## "):
            document.add_heading(line[3:].strip(), level=1)
        elif line.startswith("### "):
            document.add_heading(line[4:].strip(), level=2)
        elif line.startswith("**") and line.endswith("**") and len(line) > 4:
            p = document.add_paragraph()
            p.add_run(line.strip("*")).bold = True
        else:
            document.add_paragraph(line)

    term_list = _split_terms(terms)
    if term_list:
        document.add_heading("Terms Summary", level=2)
        table = document.add_table(rows=1, cols=2)
        try:
            table.style = "Light Grid Accent 1"
        except KeyError:
            pass  # style not available in this docx template — default grid still works
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "#"
        hdr_cells[1].text = "Term"
        for i, term in enumerate(term_list, start=1):
            row_cells = table.add_row().cells
            row_cells[0].text = str(i)
            row_cells[1].text = term

    document.add_paragraph()
    footer_p = document.add_paragraph("LegalEase Inc. | contact@legalease.com | All Rights Reserved.")
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in footer_p.runs:
        run.font.size = Pt(8)
        run.italic = True

    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()
