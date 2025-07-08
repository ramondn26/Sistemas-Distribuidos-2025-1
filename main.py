import streamlit as st
import requests

# Endereços dos agentes (garanta que batem com o que está rodando)
URL_IA_LOCAL = "http://localhost:8001/analyze"    # FastAPI (sentimento)
URL_IA_REMOTA = "http://localhost:8000/assistant" # Flask (assistente)

st.set_page_config(page_title="Atendimento Online", page_icon="💬")

st.title("💬 Atendimento Virtual")

# Escolha do tipo de usuário
tipo_usuario = st.radio("Tipo de usuário:", ["Comum", "Premium"])
id_cliente = st.text_input("Seu nome ou ID (opcional):", key="idcliente")
idioma = st.selectbox("Idioma preferido:", ["pt-BR", "en-US"])
mensagem = st.text_area("Digite sua dúvida ou mensagem:")

if st.button("Enviar"):
    if not mensagem.strip():
        st.warning("Digite uma mensagem para continuar.")
    else:
        # Análise de sentimento (IA local)
        with st.spinner("Analisando sentimento..."):
            try:
                r = requests.post(URL_IA_LOCAL, json={"text": mensagem})
                r.raise_for_status()
                sent_data = r.json()
                sentimento = sent_data.get("sentimento")
                confianca = sent_data.get("confianca")
            except Exception as e:
                st.error(f"Erro na análise de sentimento: {e}")
                sentimento = "NEUTRO"
                confianca = 0.5

        st.write(f"Sentimento detectado: **{sentimento}** | Confiança: **{confianca}**")

        # Consulta à IA remota (Flask)
        payload = {
            "idCliente": id_cliente or None,
            "mensagemUsuario": mensagem,
            "sentimento": sentimento,
            "confianca": confianca,
            "idiomaPreferido": idioma
        }
        with st.spinner("Aguardando resposta da assistente..."):
            try:
                r2 = requests.post(URL_IA_REMOTA, json=payload)
                r2.raise_for_status()
                resposta = r2.json().get("assistant")
            except Exception as e:
                resposta = f"Erro ao consultar assistente: {e}"

        st.markdown("---")
        st.markdown("### Resposta da Assistente")
        st.write(resposta)

        # Promoção apenas para premium
        if tipo_usuario == "Premium":
            st.success("🎁 Promoção exclusiva para você! Ganhe 10% OFF em sua próxima compra com o cupom PREMIUM10.")

        st.markdown("---")
        st.info("Preencha novamente para uma nova consulta.")

