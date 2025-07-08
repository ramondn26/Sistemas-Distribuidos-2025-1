#!/usr/bin/env python3
# ml_assistant.py

import os
import sys
import json
from typing import Literal

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

# ─── MODELO DE VALIDAÇÃO DA REQUISIÇÃO ─────────────────────────────────────────
class AssistRequest(BaseModel):
    idCliente: str | None = None
    mensagemUsuario: str
    sentimento: Literal["POSITIVO", "NEGATIVO"]
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
com valor “POSITIVO” ou “NEGATIVO”, e um campo precisao (número entre 0.0 e 1.0)
indicando a confiança na análise de sentimento. Se o sentimento for NEGATIVO,
sua resposta deve começar com empatia, demonstrando preocupação com o cliente e oferecendo
soluções (como reembolso, troca ou suporte). Se o sentimento for POSITIVO, você deve responder
com entusiasmo, agradecer e sugerir produtos relacionados. A precisão deve ser interpretada da seguinte forma:
- Se for ≥ 0.85, aja com segurança.
- Entre 0.60 e 0.84, aja com cautela e peça confirmação (“Entendi corretamente que…?”).
- Se for < 0.60, você deve se recusar a responder e pedir mais contexto ao usuário.
Em todos os casos, sua linguagem deve ser cordial, clara e alinhada com as boas práticas de atendimento
brasileiro, oferecendo sempre opções de contato humano quando necessário, garantindo o direito de
arrependimento em até 7 dias, respeitando a privacidade dos dados e nunca prometendo nada que não possa ser cumprido.
""".strip()

# ─── FUNÇÃO DE CHAMADA AO MODELO ────────────────────────────────────────────────
def get_advice(req: AssistRequest) -> str:
    # monta o conteúdo do usuário como JSON para a IA
    user_payload = json.dumps({
        "idCliente": req.idCliente,
        "mensagemUsuario": req.mensagemUsuario,
        "sentimento": req.sentimento,
        "confianca": req.confianca,
        "idiomaPreferido": req.idiomaPreferido
    }, ensure_ascii=False)

    resp = client.chat.completions.create(
        model="gpt-4o",      # or "gpt-4", "gpt-4-32k", "gpt-4o", etc.
        temperature=0.7,
        max_tokens=250,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_payload},
        ],
    )
    return resp.choices[0].message.content.strip()

# ─── CONFIGURAÇÃO DO FLASK ────────────────────────────────────────────────────
app = Flask(__name__)

@app.route("/assistant", methods=["POST"])
def assistant():
    # valida payload
    try:
        payload = AssistRequest(**request.get_json(force=True))
    except (TypeError, ValidationError) as e:
        return jsonify({"error": "Payload inválido", "details": getattr(e, "errors", str(e))}), 400

    # chama a IA e retorna a resposta (ela mesma decidirá recusar se precisao < 0.60)
    try:
        answer = get_advice(payload)
        return jsonify({"assistant": answer})
    except OpenAIError as e:
        return jsonify({"error": "Erro ao chamar OpenAI", "details": str(e)}), 502

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)