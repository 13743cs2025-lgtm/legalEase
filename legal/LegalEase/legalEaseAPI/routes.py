"""
legalEaseAPI/routes.py
Defines the /generate and /health endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ai_core.gemini_generator import GeminiDocumentGenerator

router = APIRouter()

# Lazily instantiated so the app can still start (and /health can respond)
# even if GEMINI_API_KEY hasn't been configured yet.
_generator: GeminiDocumentGenerator | None = None


def get_generator() -> GeminiDocumentGenerator:
    global _generator
    if _generator is None:
        _generator = GeminiDocumentGenerator()
    return _generator


class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=1, description="e.g. NDA, Lease Agreement")
    parties: str = Field(..., min_length=1, description="Names/roles of involved parties")
    terms: str = Field(..., min_length=1, description="Semicolon-separated clauses")
    dates: str = Field(..., min_length=1, description="Effective date")


class DocumentResponse(BaseModel):
    document: str


@router.post("/generate", response_model=DocumentResponse)
def generate_legal_document(request: DocumentRequest):
    try:
        generator = get_generator()
        document_text = generator.generate_document(
            request.document_type,
            request.parties,
            request.terms,
            request.dates,
        )
        return {"document": document_text}
    except ValueError as ve:
        # Configuration error (e.g. missing API key)
        raise HTTPException(status_code=500, detail=str(ve))
    except RuntimeError as re_:
        # Upstream Gemini API error
        raise HTTPException(status_code=502, detail=str(re_))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")


@router.get("/health")
def health_check():
    return {"status": "ok"}
