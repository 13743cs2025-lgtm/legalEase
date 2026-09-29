"""
formatting/pdf_formatter.py
Converts raw AI-generated document text into a branded .pdf file using fpdf2,
with a centered logo + title header and a footer on every page.
"""

import os

from fpdf import FPDF

from config import LOGO_PATH
from utils.sanitize import sanitize_text


def _split_terms(terms: str):
    return [t.strip() for t in terms.split(";") if t.strip()]


class _LegalPDF(FPDF):
    def __init__(self, doc_type: str):
        super().__init__()
        self.doc_type = doc_type or "Legal Document"
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if LOGO_PATH and os.path.exists(LOGO_PATH):
            try:
                self.image(LOGO_PATH, x=(self.w - 25) / 2, y=8, w=25)
                self.ln(22)
            except Exception:
                self.ln(4)
        self.set_font("Times", "B", 14)
        self.cell(0, 10, self.doc_type, align="C", ln=1)
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Times", "I", 8)
        self.cell(0, 10, "LegalEase Inc. | contact@legalease.com | All Rights Reserved.", align="C")


def format_pdf(text: str, doc_type: str, terms: str = "") -> bytes:
    """Returns the raw bytes of a generated .pdf file."""
    text = sanitize_text(text)
    pdf = _LegalPDF(doc_type)
    pdf.add_page()
    pdf.set_font("Times", size=11)

    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            pdf.ln(3)
            continue
        if line.startswith("## "):
            pdf.set_font("Times", "B", 13)
            pdf.multi_cell(0, 8, line[3:].strip())
            pdf.set_font("Times", size=11)
        elif line.startswith("### "):
            pdf.set_font("Times", "B", 12)
            pdf.multi_cell(0, 8, line[4:].strip())
            pdf.set_font("Times", size=11)
        elif line.startswith("**") and line.endswith("**") and len(line) > 4:
            pdf.set_font("Times", "B", 11)
            pdf.multi_cell(0, 7, line.strip("*"))
            pdf.set_font("Times", size=11)
        else:
            pdf.multi_cell(0, 7, line)

    term_list = _split_terms(terms)
    if term_list:
        pdf.ln(4)
        pdf.set_font("Times", "B", 12)
        pdf.cell(0, 8, "Terms Summary", ln=1)
        pdf.set_font("Times", size=11)
        for i, term in enumerate(term_list, start=1):
            pdf.multi_cell(0, 7, f"{i}. {term}")

    output = pdf.output(dest="S")
    # fpdf2 returns a bytearray in recent versions, a str in older ones.
    if isinstance(output, str):
        return output.encode("latin-1")
    return bytes(output)
