import os
import subprocess
import sys
import venv
import webbrowser
from pathlib import Path
from fastapi import FastAPI

# ---------------- CONFIGURAÇÃO ----------------
PROJECT_ROOT = Path(__file__).resolve().parent  # caminho dinâmico e compatível com Render
VENV_PATH = PROJECT_ROOT / ".venv"
BACKEND_MAIN = PROJECT_ROOT / "backend" / "main.py"
FRONTEND_DIR = PROJECT_ROOT / "frontend"  # Altere se sua pasta do React tiver outro nome
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "SUA_CHAVE_AQUI")  # usa variável no Render
DEFAULT_PACKAGES = ["requests", "uvicorn", "python-dotenv"]
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
FRONTEND_PORT = 5173
