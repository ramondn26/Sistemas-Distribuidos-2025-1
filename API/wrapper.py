#!/usr/bin/env python3
# wrapper.py

import os
import sys
import json
import requests
from flask import Flask, request, jsonify
from pydantic import BaseModel, ValidationError
from flask_cors import CORS

# Se quiser logar melhor, importe logging e configure.

app = Flask(__name__)
CORS(app)   

# modelo de entrada: só idCliente e mensagemUsuario
class IntegratedInput(BaseModel):
    idCliente: str
    mensagemUsuario: str
    idiomaPreferido: str = "pt-BR"

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