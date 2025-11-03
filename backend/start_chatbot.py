import os
import subprocess
import sys
import venv
from pathlib import Path

# ---------------- CONFIGURAÇÃO ----------------
PROJECT_ROOT = Path(__file__).resolve().parent
VENV_PATH = PROJECT_ROOT / ".venv"
BACKEND_MAIN = PROJECT_ROOT / "backend" / "main.py"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "SUA_CHAVE_AQUI")
DEFAULT_PACKAGES = ["requests", "uvicorn", "python-dotenv"]
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"

# ---------------- FUNÇÕES ----------------
def run_command(cmd_list, cwd=None, env=None):
    process = subprocess.Popen(
        cmd_list, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env
    )
    for line in process.stdout:
        print(line, end="")
    process.wait()

def create_venv(path):
    if not path.exists():
        print("Criando venv...")
        venv.create(path, with_pip=True)
    else:
        print("Venv já existe.")

def install_backend_packages(python_exe):
    run_command([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"])
    if REQUIREMENTS_FILE.exists():
        print("Instalando pacotes do requirements.txt...")
        run_command([str(python_exe), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)])
    else:
        print("requirements.txt não encontrado, instalando pacotes padrão...")
        for pkg in DEFAULT_PACKAGES:
            run_command([str(python_exe), "-m", "pip", "install", pkg])

def run_backend(python_exe, env):
    print("Iniciando backend...")
    subprocess.Popen([str(python_exe), str(BACKEND_MAIN)], env=env).wait()

# ---------------- SCRIPT PRINCIPAL ----------------
def main():
    create_venv(VENV_PATH)
    python_exe = VENV_PATH / "bin" / "python"

    if not python_exe.exists():
        print(f"Python não encontrado no venv: {python_exe}")
        sys.exit(1)

    install_backend_packages(python_exe)

    env = os.environ.copy()
    env["OPENAI_API_KEY"] = OPENAI_API_KEY

    run_backend(python_exe, env)

if __name__ == "__main__":
    main()
