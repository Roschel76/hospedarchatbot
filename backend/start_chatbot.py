import os
import subprocess
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ---------------- CONFIGURAÇÃO ----------------
PROJECT_ROOT = Path(__file__).parent
BACKEND_MAIN = PROJECT_ROOT / "backend" / "main.py"  # seu código principal
FRONTEND_DIR = PROJECT_ROOT.parent / "frontend"  # ajuste se necessário
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sua_chave_aqui")
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
FRONTEND_PORT = 5173

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

def install_backend_packages():
    if REQUIREMENTS_FILE.exists():
        print("Instalando pacotes do requirements.txt...")
        run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        run_command([sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)])
    else:
        print("requirements.txt não encontrado! Instale pacotes manualmente.")

def run_backend():
    if not BACKEND_MAIN.exists():
        print(f"Arquivo backend/main.py não encontrado em {BACKEND_MAIN}")
        sys.exit(1)

    # Variáveis de ambiente
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = OPENAI_API_KEY

    print("Iniciando backend...")
    subprocess.Popen([sys.executable, str(BACKEND_MAIN)], env=env)

def run_frontend():
    if not (FRONTEND_DIR / "package.json").exists():
        print("Front-end React não encontrado em:", FRONTEND_DIR)
        return
    print("Instalando dependências do front-end (npm install)...")
    run_command(["npm", "install"], cwd=FRONTEND_DIR)
    print("Iniciando front-end React (npm run dev)...")
    subprocess.Popen(["npm", "run", "dev"], cwd=FRONTEND_DIR)
    # abre navegador automaticamente
    import webbrowser
    webbrowser.open(f"http://localhost:{FRONTEND_PORT}")

# ---------------- ROTA DE TESTE ----------------
app = FastAPI(title="TimeLean Chatbot - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Backend funcionando no Render!"}

# ---------------- SCRIPT PRINCIPAL ----------------
def main():
    install_backend_packages()
    run_backend()
    run_frontend()
    # Rodar FastAPI localmente (somente para teste)
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
