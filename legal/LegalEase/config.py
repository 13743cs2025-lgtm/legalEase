"""
config.py
Centralized configuration loaded from environment variables (.env file).
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Gemini AI settings ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-3.8-flash")

# --- Backend (FastAPI) settings ---
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))

# --- Frontend (Streamlit) settings ---
# URL the Streamlit app uses to reach the FastAPI backend
BACKEND_URL = os.getenv("BACKEND_URL", f"http://localhost:{BACKEND_PORT}")

# --- Branding ---
# Optional path to a logo image (png/jpg) used in DOCX/PDF/Streamlit UI.
# Leave blank ("") if you don't have a logo yet.
LOGO_PATH = os.getenv("LOGO_PATH", "")
