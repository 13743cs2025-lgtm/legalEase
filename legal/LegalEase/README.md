# LegalEase — AI-Powered Legal Document Generator

Generates employment contracts, NDAs, lease agreements, and other legal
documents from plain-language input, using Google's Gemini model. Export
results as `.txt`, `.docx`, or `.pdf`.

## Project Structure

```
LegalEase/
├── ai_core/
│   └── gemini_generator.py     # Gemini API wrapper (prompt + call)
├── legalEaseAPI/
│   ├── main.py                 # FastAPI app entrypoint
│   └── routes.py               # POST /generate, GET /health
├── frontend/
│   └── app.py                  # Streamlit UI
├── formatting/
│   ├── docx_formatter.py       # .docx export (python-docx)
│   ├── pdf_formatter.py        # .pdf export (fpdf2)
│   └── html_formatter.py       # in-app HTML preview
├── utils/
│   └── sanitize.py             # text cleanup shared by all formatters
├── Image/                      # put an optional logo.png here
├── config.py                   # reads .env into constants
├── requirements.txt
├── .env.example
├── run.sh                      # launches backend + frontend together
└── README.md
```

## 1. Prerequisites

- Python 3.10+
- A Gemini API key — get one free at https://aistudio.google.com/app/apikey

## 2. VS Code Setup

1. Open the `LegalEase` folder in VS Code (`File > Open Folder...`).
2. Install the **Python** extension (Microsoft) if you don't have it.
3. Open a terminal in VS Code: `` Ctrl+` `` (Windows/Linux) or `Cmd+` `` (Mac).

## 3. Installation

```bash
# Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

In VS Code, select this venv as your interpreter: `Ctrl+Shift+P` →
`Python: Select Interpreter` → choose `./venv`.

## 4. Configure your API key

```bash
# Copy the template and edit it
cp .env.example .env        # Windows: copy .env.example .env
```

Open `.env` and paste your key:

```
GEMINI_API_KEY=your_actual_key_here
```

(Optional) If you have a logo image, drop it in `Image/logo.png` and set
`LOGO_PATH=Image/logo.png` in `.env`.

> **Note on the model name:** this project defaults to `gemini-3.8-flash`.
> Google periodically retires/renames models — if you get a "model not
> found" error, check https://ai.google.dev/gemini-api/docs/models for the
> current model name and update `GEMINI_MODEL_NAME` in `.env` (e.g. to a
> newer `gemini-2.x` model).

## 5. Running the app

You need **two terminals** (or use `run.sh` to start both at once), always
from the **project root** so the `config`, `ai_core`, `formatting`, and
`utils` modules resolve correctly.

**Terminal 1 — Backend (FastAPI):**
```bash
uvicorn legalEaseAPI.main:app --reload
```
You should see `Application startup complete.` and the API live at
`http://127.0.0.1:8000`. Visit `http://127.0.0.1:8000/docs` for the
interactive Swagger UI.

**Terminal 2 — Frontend (Streamlit):**
```bash
streamlit run frontend/app.py
```
Streamlit opens automatically at `http://localhost:8501`.

**Or, on macOS/Linux, run both at once:**
```bash
bash run.sh
```

## 6. Testing the app

1. **Health check** — with the backend running, visit
   `http://127.0.0.1:8000/health` → should return `{"status":"ok"}`.
2. **API test via Swagger** — go to `http://127.0.0.1:8000/docs`, expand
   `POST /generate`, click "Try it out", and submit a sample payload:
   ```json
   {
     "document_type": "Freelance Work Contract",
     "parties": "Jane Doe (Service Provider), TechNova Inc. (Client)",
     "terms": "Payment due within 7 days of invoice; Confidentiality must be maintained; Either party may terminate with 15 days notice",
     "dates": "April 15, 2025"
   }
   ```
   You should get back a `document` field containing generated legal text.
3. **End-to-end via Streamlit:**
   - Fill in Document Type, Parties, Terms (semicolon-separated), and
     Effective Date.
   - Click **Generate Document** — a preview appears in a dark card.
   - Click **Click to Edit Document** to tweak the text inline.
   - Use the three download buttons to verify `.txt`, `.docx`, and `.pdf`
     all open correctly and include your terms and (if configured) logo.
4. **Error handling test** — stop the backend, then click "Generate
   Document" in Streamlit; you should see a friendly connection-error
   message instead of a crash.

## 7. Common issues

| Symptom | Fix |
|---|---|
| `ValueError: GEMINI_API_KEY is not set` | Make sure `.env` exists (not just `.env.example`) and contains a real key, and that you're running commands from the project root. |
| `ModuleNotFoundError: No module named 'config'` | You're not running from the project root — `cd` into `LegalEase/` first. |
| Streamlit shows "Could not connect to the backend" | Start the FastAPI server first (Terminal 1) before using the Streamlit app. |
| Gemini returns `429` or says quota exceeded | Google enforces request quotas per API project and model. Wait for the quota reset, enable billing/request more quota in Google AI Studio, or set `GEMINI_MODEL_NAME` in `.env` to a model with available quota. Retrying immediately does not increase a daily limit. |
| PDF/DOCX missing special characters (curly quotes, emoji) | Expected — `utils/sanitize.py` strips non-ASCII characters so text renders safely with the built-in Times New Roman font in both exporters. |
| `model not found` error from Gemini | Update `GEMINI_MODEL_NAME` in `.env` to a currently supported model (see note above). |

## 8. Deployment (optional next step)

- **Backend**: any host that runs a Python web app (Render, Railway, Fly.io,
  a VPS). Set `GEMINI_API_KEY` as an environment variable there, and start
  with `uvicorn legalEaseAPI.main:app --host 0.0.0.0 --port $PORT`.
- **Frontend**: Streamlit Community Cloud, or the same host as the backend.
  Set `BACKEND_URL` to your deployed backend's public URL.
