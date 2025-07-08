#!/usr/bin/env python3
# wrapper.py

import os
import sys
import json
import requests
from flask import Flask, request, jsonify
from pydantic import BaseModel, ValidationError, Field
from flask_cors import CORS
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

load_dotenv()  # pip install python-dotenv
API_KEY = os.getenv("OPENAI_API_KEY")

# Se quiser logar melhor, importe logging e configure.

app = Flask(__name__)
CORS(app, origins=["http://localhost:8501"])  

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["10 per minute"])

@app.before_request
def check_api_key():
    if request.endpoint == "integrated" and request.method == "POST":
        if request.headers.get("x-api-key") != API_KEY:
            return jsonify({"error": "API key inválida"}), 401
        
# modelo de entrada: só idCliente e mensagemUsuario
class IntegratedInput(BaseModel):
    idCliente: str = Field(..., max_length=50, pattern=r"^[a-zA-Z0-9\-]+$")
    mensagemUsuario: str = Field(..., min_length=1, max_length=500)
    idiomaPreferido: str = Field("pt-BR", pattern=r"^[a-z]{2}\-[A-Z]{2}$")

@app.route("/integrated", methods=["POST"])
def integrated():
    # valida JSON de entrada
    try:
        data = IntegratedInput(**request.get_json(force=True))
    except (TypeError, ValidationError) as e:
        return jsonify({"error": "Payload inválido", "details": getattr(e, "errors", str(e))}), 400

    # 1) chama IA local de análise de sentimento
    try:
        analyze_resp = requests.post(
            "http://localhost:8000/analyze",
            json={"text": data.mensagemUsuario},
            timeout=5
        )
        analyze_resp.raise_for_status()
        analysis = analyze_resp.json()
        sentimento = analysis["sentimento"]
        confianca = analysis["confianca"]
    except Exception as e:
        return jsonify({"error": "Falha na análise de sentimento", "details": str(e)}), 502

    # 2) chama rota /assistant com o payload completo
    assistant_payload = {
        "idCliente": data.idCliente,
        "mensagemUsuario": data.mensagemUsuario,
        "sentimento": sentimento,
        "confianca": confianca,
        "idiomaPreferido": data.idiomaPreferido
    }

    try:
        assist_resp = requests.post(
            "http://localhost:8080/assistant",
            json=assistant_payload,
            timeout=10
        )
        assist_resp.raise_for_status()
        assistant_data = assist_resp.json()
    except Exception as e:
        return jsonify({"error": "Falha ao chamar /assistant", "details": str(e)}), 502

    # 3) retorna a junção dos dois resultados
    return jsonify({
        "sentimento": sentimento,
        "confianca": confianca,
        "assistant": assistant_data.get("assistant"),
        # em caso de erro interno, repassa detalhes
        **({k: v for k, v in assistant_data.items() if k != "assistant"})
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8090))
    app.run(host="127.0.0.1", port=port)