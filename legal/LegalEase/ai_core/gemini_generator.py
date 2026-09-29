"""
ai_core/gemini_generator.py
Wraps the Google Generative AI (Gemini) SDK to turn structured user input
into a fully drafted legal document.
"""

import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL_NAME


class GeminiDocumentGenerator:
    """Generates legal document text using Google's Gemini model."""

    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not set. Add it to your .env file "
                "(see .env.example)."
            )
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)

    def generate_document(
        self, document_type: str, parties: str, terms: str, dates: str
    ) -> str:
        """Calls Gemini and returns the generated document text."""
        prompt = self._build_prompt(document_type, parties, terms, dates)
        try:
            response = self.model.generate_content(prompt)
        except Exception as exc:  # network / auth / quota errors etc.
            error_text = str(exc)
            lowered_error = error_text.lower()
            if "quota" in lowered_error or "free_tier" in lowered_error:
                raise RuntimeError(
                    f"Gemini quota exceeded for {GEMINI_MODEL_NAME}. The API key's "
                    "Google project has reached this model's free-tier request "
                    "limit. Wait for the quota to reset, enable billing or request "
                    "more quota in Google AI Studio, or set GEMINI_MODEL_NAME in "
                    ".env to a model with available quota. See "
                    "https://ai.google.dev/gemini-api/docs/rate-limits."
                ) from exc
            if "429" in error_text or "resourceexhausted" in lowered_error:
                raise RuntimeError(
                    "Gemini is temporarily rate-limiting requests. Wait briefly "
                    "before trying again, and check the project's quota if this "
                    "continues."
                ) from exc
            raise RuntimeError(f"Gemini API request failed: {exc}") from exc

        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        return text.strip()

    @staticmethod
    def _build_prompt(document_type: str, parties: str, terms: str, dates: str) -> str:
        return (
            "You are an expert legal drafter. Generate a complete, formal, "
            f"and legally structured document titled '{document_type}'.\n\n"
            f"Involved Parties: {parties}\n"
            f"Effective Date: {dates}\n"
            f"Terms and Conditions to incorporate: {terms}\n\n"
            "Formatting rules:\n"
            "- Start with a single '## ' line containing the document title.\n"
            "- Use '### ' for major section headings (e.g., Definitions, Term, "
            "Payment, Confidentiality, Termination, Governing Law, Signatures).\n"
            "- Use '**bold**' only for short emphasis phrases, not headings.\n"
            "- Turn each item in the Terms and Conditions into its own clause.\n"
            "- End with a signature block listing every involved party with a "
            "blank line for their signature.\n"
            "- Output plain text only — no commentary, no disclaimers about "
            "being an AI, and no markdown code fences."
        )
