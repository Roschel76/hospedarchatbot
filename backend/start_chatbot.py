import os
import subprocess
import sys
import platform
from pathlib import Path

# ---------------- CONFIGURAÇÃO ----------------
# Define o diretório raiz do projeto automaticamente (sem caminhos fixos)
PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_MAIN = PROJECT_ROOT / "main.py"
FRONTEND_DIR = PROJECT_ROOT.parent / "frontend"  # volta 1 nível, pois backend/ está dentro do projeto
REQUIREMENTS_FILE = PROJECT_ROOT.parent / "requirements.txt"

DEFAULT_PACKAGES = ["requests", "uvicorn", "python-dotenv"]
FRONTEND_PORT = 5173

# Adicione sua chave da API via variável de ambiente (não no código)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "SUA_CHAVE_AQUI")  

# ---------------- FUNÇÕES ----------------
def run_command(cmd_list, cwd=None, env=None):
    """Executa comandos no terminal e mostra saída em tempo real."""
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
    """Instala as dependências do backend."""
    if REQUIREMENTS_FILE.exists():
        print("Instalando pacotes do requirements.txt...")
        run_command([sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)])
    else:
        print("requirements.txt não encontrado, instalando pacotes padrão...")
        for pkg in DEFAULT_PACKAGES:
            run_command([sys.executable, "-m", "pip", "install", pkg])

def run_backend(env):
    """Inicia o backend (FastAPI)."""
    print("Iniciando backend...")
    return subprocess.Popen([sys.executable, str(BACKEND_MAIN)], env=env)

def run_frontend():
    """Inicia o frontend (React, se existir)."""
    if not (FRONTEND_DIR / "package.json").exists():
        print("Front-end React não encontrado em:", FRONTEND_DIR)
        return None

    print("Instalando dependências do front-end...")
    run_command(["npm", "install"], cwd=FRONTEND_DIR)

    print("Iniciando front-end React...")
    return subprocess.Popen(["npm", "run", "dev"], cwd=FRONTEND_DIR)

# ---------------- SCRIPT PRINCIPAL ----------------
def main():
    print("Preparando ambiente...")

    # Instala pacotes
    install_backend_packages()

    # Define variáveis de ambiente
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = OPENAI_API_KEY

    # Executa backend
    backend_proc = run_backend(env)

    # Executa frontend (apenas se estiver rodando localmente)
    if platform.system() == "Windows":
        frontend_proc = run_frontend()
    else:
        frontend_proc = None

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
