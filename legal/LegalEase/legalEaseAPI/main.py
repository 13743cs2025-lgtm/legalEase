"""
legalEaseAPI/main.py
FastAPI application entrypoint for LegalEase.
Run with:  uvicorn legalEaseAPI.main:app --reload
(run from the project root so `config` and `ai_core` are importable)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from legalEaseAPI.routes import router

app = FastAPI(
    title="LegalEase - AI Legal Document Generator",
    description="Generates employment contracts, NDAs, lease agreements, and more using Gemini.",
    version="1.0.0",
)

# Allow the Streamlit frontend (running on a different port) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def home():
    return {"message": "Welcome to LegalEase AI Legal Document Generator API"}


if __name__ == "__main__":
    import uvicorn
    from config import BACKEND_HOST, BACKEND_PORT

    uvicorn.run("legalEaseAPI.main:app", host=BACKEND_HOST, port=BACKEND_PORT, reload=True)
