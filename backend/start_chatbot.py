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


# ---------------- API PRINCIPAL ----------------
app = FastAPI(title="TimeLean Chatbot - Backend (POC)")

@app.get("/")
def home():
    return {"message": "Chatbot está online 🚀"}

# ---------------- FUNÇÕES ----------------
def run_command(cmd_list, cwd=None, env=None):
    process = subprocess.Popen(cmd_list, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
    try:
        for line in process.stdout:
            print(line, end="")
        process.wait()
    except KeyboardInterrupt:
        print("\nEncerrando processos...")
        process.terminate()
        sys.exit(0)

def create_venv(path):
    if not path.exists():
        print("Criando venv...")
        venv.create(path, with_pip=True)
    else:
        print("Venv já existe.")

def install_backend_packages(python_exe):
    run_command([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
    if REQUIREMENTS_FILE.exists():
        print("Instalando pacotes do requirements.txt...")
        run_command([python_exe, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)])
    else:
        print("requirements.txt não encontrado, instalando pacotes padrão...")
        for pkg in DEFAULT_PACKAGES:
            run_command([python_exe, "-m", "pip", "install", pkg])

def run_backend(python_exe, env):
    print("Iniciando backend...")
    return subprocess.Popen([python_exe, str(BACKEND_MAIN)], env=env)

def run_frontend():
    if not (FRONTEND_DIR / "package.json").exists():
        print("Front-end React não encontrado na pasta:", FRONTEND_DIR)
        return None

    print("Instalando dependências do front-end (se necessário)...")
    run_command(["npm", "install"], cwd=FRONTEND_DIR)

    print("Iniciando front-end React...")
    proc = subprocess.Popen(["npm", "run", "dev"], cwd=FRONTEND_DIR)
    # abre navegador automaticamente
    webbrowser.open(f"http://localhost:{FRONTEND_PORT}")
    return proc

# ---------------- SCRIPT PRINCIPAL ----------------
def main():
    create_venv(VENV_PATH)
    python_exe = VENV_PATH / "Scripts" / "python.exe"
    if not python_exe.exists():
        print(f"Python não encontrado no venv: {python_exe}")
        sys.exit(1)

    install_backend_packages(str(python_exe))

    # preparar variáveis de ambiente
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = OPENAI_API_KEY

    # rodar backend
    backend_proc = run_backend(str(python_exe), env)

    # rodar front-end
    frontend_proc = run_frontend()

    try:
        backend_proc.wait()
        if frontend_proc:
            frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nEncerrando tudo...")
        backend_proc.terminate()
        if frontend_proc:
            frontend_proc.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()
