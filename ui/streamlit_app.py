import os
import uuid

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://api:8000")

st.set_page_config(page_title="RAG Bank Assistant", page_icon="🏦")
st.title("🏦 RAG Bank Assistant")
st.caption("Asistente conversacional basado en información scrapeada del sitio institucional.")

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = f"session_{uuid.uuid4().hex[:8]}"

conversation_id = st.text_input("ID de conversación", value=st.session_state.conversation_id)
st.session_state.conversation_id = conversation_id

with st.sidebar:
    st.header("Administración")
    if st.button("Ejecutar scraping + indexación"):
        with st.spinner("Procesando sitio web e indexando contenido..."):
            response = requests.post(f"{API_URL}/ingest", timeout=300)
            if response.ok:
                st.success("Ingesta completada")
                st.json(response.json())
            else:
                st.error(response.text)

    if st.button("Ver métricas"):
        response = requests.get(f"{API_URL}/analytics", timeout=30)
        if response.ok:
            st.json(response.json())
        else:
            st.error(response.text)

question = st.chat_input("Escribe tu pregunta sobre el sitio web...")

if question:
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Consultando RAG..."):
            response = requests.post(
                f"{API_URL}/ask",
                json={"conversation_id": conversation_id, "question": question},
                timeout=180,
            )
            if response.ok:
                data = response.json()
                st.write(data["answer"])
                with st.expander("Fuentes recuperadas"):
                    st.json(data.get("sources", []))
            else:
                st.error(response.text)
