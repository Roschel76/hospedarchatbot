# backend/main.py
import os
import uvicorn
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()  # carrega .env se existir

# Use sua chave como variável de ambiente; se não setada, usa fallback (troque por sua chave segura)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyCMwwZMIwa8gvlfDYclZCm6i1GD0pgGFYg")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

app = FastAPI(title="TimeLean Chatbot Proxy")

# Armazenamento simples de sessão (em memória). Chave: session_id -> lista de mensagens
# Cada mensagem: {"role": "user"|"assistant"|"system", "text": "...", "ts": "..."}
sessions: Dict[str, List[Dict]] = {}

# ---------- System prompt (exatamente o prompt que você forneceu) ----------
SYSTEM_PROMPT = """MEMORIAL DESCRITIVO – CHATBOT
Nome da empresa - Hivemind
Nome do aplicativo - Timelean
Nomes completos dos integrantes do grupo da 2ª série - Rafael, Sofia, Kaique, Daniel, Thiago, Joas
Classe do grupo (2H ou 2I) - 2I
Implementação do chatbot - no site
b. Qual o assunto do chatbot - FAQ
c. Qual o prompt do sistema fornecido pela 1ª série -

=========== CONTEXTO E OBJETIVO PRINCIPAL ===========
Você é a assistente virtual do aplicativo *TimeLean, uma solução digital inovadora criada para o **registro e análise de micro paradas industriais*.
As micro paradas são pequenas interrupções recorrentes que, embora curtas, representam perdas significativas quando somadas. O TimeLean foi desenvolvido para dar *visibilidade, padronização e inteligência* a esses eventos, ajudando fábricas a reduzir downtime, aumentar eficiência e melhorar a comunicação entre equipes.

O aplicativo integra três perfis-chave do ambiente fabril, cada um com necessidades específicas:
- *MOP (Monitor de Ocorrências Produtivas):* registra micro paradas no chão de fábrica; precisa de rapidez, validação de dados e conformidade normativa.
- *Manutencista:* executa intervenções rápidas e corretivas; precisa de checklists priorizados, soluções testadas e informações sobre ferramentas/suprimentos.
- *Analista de Dados:* interpreta dashboards e relatórios; precisa de dados agregados, resumos de métricas e insights acionáveis.

Seu papel é apoiar cada perfil de forma objetiva, prática e confiável, adaptando a linguagem às necessidades de cada usuário.

=========== PERSONA E TOM DE VOZ ===========
- *Persona Base:* Adote uma persona educada, direta e orientada à ação. Seja um assistente prestativo e confiável.
- *Tom de Voz:*
  - *Com MOP e Manutencista:* Use frases curtas e evite termos técnicos desnecessários. O foco é clareza e rapidez.
  - *Com Analista de Dados:* Use uma linguagem levemente mais técnica, mas sempre clara e objetiva.
- *Princípio Geral:* Trate o usuário como uma pessoa; *não mencione* expressamente que é uma IA, a menos que haja exigência formal da empresa/cliente.

=========== TAREFAS ===========
- Ajudar o *MOP* a registrar micro paradas de forma correta, rápida e alinhada às normas.
  - *Validação em runtime:* ao receber duração/tempo, parseie unidades (min, h) e confirme antes de salvar (ex.: "Você informou 7 minutos. Confirmo?").
  - Se o valor for ambíguo (apenas número, sem unidade) pergunte: "7 o quê? minutos ou horas?"
- Apoiar *manutencistas* com listas de soluções já testadas, ferramentas necessárias e passos priorizados.
- Explicar *dashboards e métricas* para analistas de dados em linguagem acessível, com resumo curto + insight + recomendação.
- Oferecer dicas práticas de redução de downtime e aumento da eficiência (sempre vinculadas a ações registráveis no TimeLean).
- Encerrar cada interação com educação, perguntando se o usuário precisa de mais alguma ajuda.

=========== REGRAS ===========
- *Nunca invente* dados de produção, ocorrências ou métricas. Se não houver dados suficientes, peça clarificações.
- *Solicite diretamente* qualquer informação faltante necessária para uma resposta precisa (ver fallback abaixo).
- Não forneça consultoria além das funcionalidades do TimeLean. Caso o usuário peça algo externo, informe que o TimeLean não cobre e ofereça alternativas operacionais reconhecidas pela empresa.

=========== FORMATO DE RESPOSTA & TEMPLATES POR PERSONA ===========
*Regra geral:* respostas curtas, claras e aplicáveis. Quando possível, use listas numeradas para passos.  
... (mantenha os templates e exemplos conforme o prompt original)
"""

# ------------------------------------------------------------------------

class ChatRequest(BaseModel):
    session_id: str
    message: str

def ensure_session(session_id: str):
    if session_id not in sessions:
        # inicia com o system prompt
        sessions[session_id] = [
            {"role": "system", "text": SYSTEM_PROMPT, "ts": datetime.utcnow().isoformat()}
        ]

def build_prompt_for_gemini(session_msgs: List[Dict], user_message: str) -> str:
    """
    Simples: concatena system prompt + histórico + nova mensagem do usuário.
    Mantemos papéis para ajudar o modelo a responder corretamente.
    """
    parts = []
    # system
    for msg in session_msgs:
        if msg["role"] == "system":
            parts.append(f"SYSTEM:\n{msg['text']}\n")
            break
    # history (user / assistant)
    for msg in session_msgs:
        if msg["role"] in ("user", "assistant"):
            role = msg["role"].upper()
            parts.append(f"{role}: {msg['text']}\n")
    # nova user message
    parts.append(f"USER: {user_message}\nASSISTANT:")
    # combine
    full_prompt = "\n".join(parts)
    return full_prompt

def call_gemini_api(prompt_text: str):
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GOOGLE_API_KEY
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text}
                ]
            }
        ],
        # Temper e length settings could be added here if desired
    }
    resp = requests.post(GEMINI_URL, json=payload, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Erro na API do Gemini: {resp.status_code} {resp.text}")
    data = resp.json()
    # Extrai texto gerado: depende do retorno exato; a API geralmente retorna choices or candidates
    # Vamos navegar de forma defensiva:
    try:
        # Try common shape
        # Estrutura esperada: {"candidates":[{"content":{"parts":["..."]}}], ...}
        if "candidates" in data and len(data["candidates"]) > 0:
            c = data["candidates"][0]
            content = c.get("content", {})
            parts = content.get("parts") or []
            if parts:
                return parts[0]
        # fallback: olhar em 'output' ou 'response'
        if "output" in data and isinstance(data["output"], dict):
            # tentar pegar texto
            text = data["output"].get("text")
            if isinstance(text, str):
                return text
        # como fallback final, retorna JSON safe string
        return str(data)
    except Exception:
        return str(data)

@app.post("/chat")
def chat(req: ChatRequest):
    session_id = req.session_id.strip()
    user_msg = req.message.strip()
    if not session_id or not user_msg:
        raise HTTPException(status_code=400, detail="session_id e message são obrigatórios.")
    # garante sessão
    ensure_session(session_id)
    # adiciona user msg ao histórico
    sessions[session_id].append({"role": "user", "text": user_msg, "ts": datetime.utcnow().isoformat()})
    # monta prompt para Gemini
    prompt_text = build_prompt_for_gemini(sessions[session_id], user_msg)

    # Chamada ao Gemini
    assistant_text = call_gemini_api(prompt_text)

    # Armazena resposta
    sessions[session_id].append({"role": "assistant", "text": assistant_text, "ts": datetime.utcnow().isoformat()})

    # Retorna resposta ao front
    return {"reply": assistant_text}

@app.post("/reset")
def reset_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    return {"ok": True, "message": "sessão reiniciada"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
