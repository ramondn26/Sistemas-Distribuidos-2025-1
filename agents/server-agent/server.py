#!/usr/bin/env python3
# server.py

import os
import sys
import json
import pathlib
from typing import Literal, Dict, List

from flask import Flask, request, jsonify
from pydantic import BaseModel, ValidationError, field_validator
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv

# carrega .env automaticamente
load_dotenv()

# ─── CONFIGURAÇÃO DA OPENAI ────────────────────────────────────────────────────
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Erro: defina OPENAI_API_KEY no ambiente.", file=sys.stderr)
    sys.exit(1)
client = OpenAI(api_key=api_key)

# ─── CARREGA FAQ DA LOJA ──────────────────────────────────────────────────────
FAQ_PATH = pathlib.Path(__file__).parent / "faq.json"
try:
    with open(FAQ_PATH, encoding="utf-8") as f:
        faq_data = json.load(f)
except FileNotFoundError:
    print(f"Aviso: {FAQ_PATH} não encontrado. Continuando sem FAQ.", file=sys.stderr)
    faq_data = {}

# monta um texto único com todas as entradas do FAQ
if faq_data:
    faq_text = "Conhecimentos da loja (FAQ):\n" + "\n".join(
        f"- **{pergunta}**: {resposta}" for pergunta, resposta in faq_data.items()
    )
else:
    faq_text = ""

# ─── ARMAZENAMENTO DE HISTÓRICO (em memória) ─────────────────────────────────
# Map cliente ID to a list of chat messages (role/content)
history_store: Dict[str, List[Dict[str, str]]] = {}

# ─── MODELO DE VALIDAÇÃO DA REQUISIÇÃO ─────────────────────────────────────────
class AssistRequest(BaseModel):
    idCliente: str
    mensagemUsuario: str
    sentimento: Literal["POSITIVO", "NEGATIVO", "NEUTRO"]
    confianca: float
    idiomaPreferido: str = "pt-BR"

    @field_validator("confianca")
    @classmethod
    def between_zero_one(cls, v: float):
        if 0.0 <= v <= 1.0:
            return v
        raise ValueError("confianca deve estar entre 0.0 e 1.0")

# ─── PROMPT DO SISTEMA (mantém sua descrição completa) ─────────────────────────
SYSTEM_PROMPT = """
Você é uma assistente virtual de varejo online treinada para atender clientes brasileiros,
seguindo todas as diretrizes do Código de Defesa do Consumidor (Lei 8.078/1990),
do Decreto do E-commerce (7.962/2013), da LGPD (Lei 13.709/2018) e das normas atuais
de atendimento ao consumidor. Sua função é simular o atendimento de uma loja online própria,
oferecendo informações e suporte sobre produtos que devem ser baseados no catálogo público da
Amazon Brasil, incluindo nome, preço, descrição e avaliações, mas sem mencionar a Amazon em nenhum momento.
Os produtos devem ser apresentados como se fossem vendidos diretamente pela sua loja.
Além disso, você receberá dois parâmetros a cada requisição: um campo sentimento,
com valor “POSITIVO”, “NEGATIVO” ou “NEUTRO”, e um campo precisao (número entre 0.0 e 1.0)
indicando a confiança na análise de sentimento. Se o sentimento for NEGATIVO,
sua resposta deve começar com empatia, demonstrando preocupação com o cliente e oferecendo
soluções (como reembolso, troca ou suporte). Se o sentimento for POSITIVO, você deve responder
com entusiasmo, agradecer e sugerir produtos relacionados. Se o sentimento for NEUTRO, responda
de forma equilibrada, oferecendo opções de produtos e perguntando se precisa de mais auxílio.
A precisão deve ser interpretada da seguinte forma:
- Se for ≥ 0.7, aja com segurança.
- Entre 0.30 e 0.69, aja com cautela e peça confirmação (“Entendi corretamente que…?”).
- Se for < 0.30, você deve se recusar a responder e pedir mais contexto ao usuário ou sugerir que fale com um atendente humano.
Em todos os casos, sua linguagem deve ser cordial, clara e alinhada com as boas práticas de atendimento
brasileiro, oferecendo sempre opções de contato humano quando necessário, garantindo o direito de
arrependimento em até 7 dias, respeitando a privacidade dos dados e nunca prometendo nada que não possa ser cumprido.
""".strip()

# ─── FUNÇÃO PARA MONTAR HISTÓRICO DE MENSAGENS ────────────────────────────────
def build_message_history(id_cliente: str, current_payload: Dict) -> List[Dict[str, str]]:
    # inicia o histórico se não existir, incluindo FAQ como segundo contexto
    if id_cliente not in history_store:
        history_store[id_cliente] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        if faq_text:
            history_store[id_cliente].append(
                {"role": "system", "content": faq_text}
            )

    # adiciona a mensagem atual do usuário
    history_store[id_cliente].append(
        {"role": "user", "content": json.dumps(current_payload, ensure_ascii=False)}
    )
    return history_store[id_cliente]

# ─── FUNÇÃO DE CHAMADA AO MODELO ────────────────────────────────────────────────
def get_advice(req: AssistRequest) -> str:
    user_payload = {
        "idCliente": req.idCliente,
        "mensagemUsuario": req.mensagemUsuario,
        "sentimento": req.sentimento,
        "confianca": req.confianca,
        "idiomaPreferido": req.idiomaPreferido
    }

    # monta o histórico completo
    messages = build_message_history(req.idCliente, user_payload)

    # chama a API passando todo o histórico
    resp = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.7,
        max_tokens=500,
        messages=messages,
    )
    assistant_reply = resp.choices[0].message.content.strip()

    # armazena a resposta da assistente
    history_store[req.idCliente].append(
        {"role": "assistant", "content": assistant_reply}
    )
    return assistant_reply

# ─── CONFIGURAÇÃO DO FLASK ────────────────────────────────────────────────────
app = Flask(__name__)

@app.route("/assistant", methods=["POST"])
def assistant():
    try:
        payload = AssistRequest(**request.get_json(force=True))
    except (TypeError, ValidationError) as e:
        return jsonify({"error": "Payload inválido", "details": getattr(e, "errors", str(e))}), 400

    try:
        answer = get_advice(payload)
        return jsonify({"assistant": answer})
    except OpenAIError as e:
        return jsonify({"error": "Erro ao chamar OpenAI", "details": str(e)}), 502

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
