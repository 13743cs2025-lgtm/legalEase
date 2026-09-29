"""
frontend/app.py
Streamlit UI for LegalEase. Collects user input, calls the FastAPI backend's
/generate endpoint, previews the result, allows inline editing, and offers
TXT / DOCX / PDF downloads.

Run with:  streamlit run frontend/app.py   (from the project root)
"""

import os
import sys

import requests
import streamlit as st

# Make the project root importable (config.py, formatting/, utils/ live there)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BACKEND_URL, LOGO_PATH  # noqa: E402
from formatting.docx_formatter import format_docx  # noqa: E402
from formatting.html_formatter import format_html_preview  # noqa: E402
from formatting.pdf_formatter import format_pdf  # noqa: E402

st.set_page_config(page_title="LegalEase", layout="centered")

if LOGO_PATH and os.path.exists(LOGO_PATH):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(LOGO_PATH, use_container_width=True)

st.markdown(
    "<h1 style='text-align:center;margin-bottom:0;'>⚖️ LegalEase</h1>"
    "<h4 style='text-align:center;font-weight:normal;color:gray;'>AI Legal Document Generator</h4>",
    unsafe_allow_html=True,
)
st.divider()

if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""
if "show_edit" not in st.session_state:
    st.session_state.show_edit = False

document_type = st.text_input(
    "Document Type", placeholder="e.g. Agreement, Contract, NDA, Lease Agreement"
)
parties = st.text_area(
    "Parties Involved", placeholder="e.g. Jane Doe (Service Provider), TechNova Inc. (Client)"
)
terms = st.text_area(
    "Terms & Conditions (use semicolons to separate clauses)",
    placeholder="Payment due within 30 days of invoice; Confidentiality must be maintained; ...",
)
dates = st.text_input("Effective Date", placeholder="e.g. April 15, 2025")

generate_clicked = st.button("Generate Document", type="primary")

if generate_clicked:
    if not all(v.strip() for v in (document_type, parties, terms, dates)):
        st.warning("Please fill in all four fields before generating a document.")
    else:
        with st.spinner("Generating your legal document..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json={
                        "document_type": document_type,
                        "parties": parties,
                        "terms": terms,
                        "dates": dates,
                    },
                    timeout=90,
                )
                if response.status_code == 200:
                    st.session_state.generated_text = response.json()["document"]
                    st.session_state.show_edit = False
                    st.success("✅ Document Generated Successfully!")
                else:
                    try:
                        detail = response.json().get("detail", response.text)
                    except ValueError:
                        detail = response.text
                    st.error(f"Generation failed: {detail}")
            except requests.exceptions.ConnectionError:
                st.error(
                    "⚠️ Could not connect to the backend API. Make sure the "
                    f"FastAPI server is running at {BACKEND_URL} "
                    "(see 'uvicorn legalEaseAPI.main:app --reload')."
                )
            except requests.exceptions.Timeout:
                st.error("The request timed out. Please try again.")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Unexpected error: {exc}")

if st.session_state.generated_text:
    styled_html = format_html_preview(st.session_state.generated_text)
    st.markdown(
        "<div style='background:#111318;padding:20px;border-radius:10px;"
        f"max-height:420px;overflow-y:auto;border:1px solid #333;'>{styled_html}</div>",
        unsafe_allow_html=True,
    )

    if st.button("✏️ Click to Edit Document"):
        st.session_state.show_edit = not st.session_state.show_edit

    if st.session_state.show_edit:
        edited_text = st.text_area(
            "Edit Document Below:", st.session_state.generated_text, height=300
        )
        st.session_state.generated_text = edited_text

    st.divider()
    safe_name = (document_type or "document").strip().replace(" ", "_").lower() or "document"

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.download_button(
            "📄 Download as .TXT",
            data=st.session_state.generated_text,
            file_name=f"{safe_name}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with col_b:
        st.download_button(
            "📝 Download as .DOCX",
            data=format_docx(st.session_state.generated_text, document_type, parties, terms, dates),
            file_name=f"{safe_name}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    with col_c:
        st.download_button(
            "📕 Download as .PDF",
            data=format_pdf(st.session_state.generated_text, document_type, terms),
            file_name=f"{safe_name}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
else:
    st.info("💡 Click 'Generate Document' to start.")
