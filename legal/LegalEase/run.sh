#!/usr/bin/env bash
# Launches the FastAPI backend and the Streamlit frontend together.
# Usage: bash run.sh   (run from the project root, with your venv activated)

set -e

echo "Starting FastAPI backend on port 8000..."
uvicorn legalEaseAPI.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Give the backend a moment to boot before the frontend tries to call it
sleep 2

echo "Starting Streamlit frontend on port 8501..."
streamlit run frontend/app.py

# When Streamlit is closed, also stop the backend
kill $BACKEND_PID
