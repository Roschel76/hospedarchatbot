import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ---------------- CONFIGURAÇÃO ----------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sua_chave_aqui")  # coloque no Render

# ---------------- APP FASTAPI ----------------
app = FastAPI(title="TimeLean Chatbot - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # aceita qualquer origem
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Backend funcionando no Render!"}

@app.get("/chat")
def chat(query: str):
    # Aqui você coloca a lógica do chatbot
    return {"query_received": query, "response": f"Resposta simulada para '{query}'"}

# ---------------- EXECUÇÃO ----------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Render define a porta automaticamente
    uvicorn.run(app, host="0.0.0.0", port=port)
