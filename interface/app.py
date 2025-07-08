# app.py

import streamlit as st
import requests

# 1) Configurações da página
st.set_page_config(
    page_title="Atendimento Automatizado",
    layout="centered",
)

# 2) Injeção do CSS personalizado
with open("style.css") as f:
    css = f"<style>{f.read()}</style>"
st.markdown(css, unsafe_allow_html=True)

# 3) Cabeçalho
st.markdown("<h1 class='titulo-principal'>Atendimento Automatizado</h1>", unsafe_allow_html=True)

# 4) Formulário
id_cliente = st.text_input("ID do Cliente", placeholder="Digite seu ID...", key="id")
mensagem = st.text_area("Mensagem do Usuário", placeholder="Escreva sua mensagem...", key="msg")

# 5) Botão de Enviar
if st.button("Enviar", key="send"):
    if not id_cliente or not mensagem:
        st.warning("Por favor, preencha ambos os campos.")
    else:
        payload = {
            "idCliente": id_cliente,
            "mensagemUsuario": mensagem,
            "idiomaPreferido": "pt-BR",
        }
        # Spinner de carregamento
        with st.spinner("Enviando e aguardando resposta..."):
            try:
                resp = requests.post("http://localhost:8090/integrated", json=payload, timeout=60)
                resp.raise_for_status()
                data = resp.json()
                assistant_text = data.get("assistant", "")
                st.success(assistant_text)
            except requests.exceptions.RequestException as e:
                st.error(f"Erro na requisição: {e}")
