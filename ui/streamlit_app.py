import os
import uuid

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://api:8000")

st.set_page_config(
    page_title="RAG Bank Assistant",
    page_icon="🏦",
    layout="wide",
)

st.title("🏦 RAG Bank Assistant")
st.caption("Asistente conversacional basado en información scrapeada del sitio institucional.")

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = f"session_{uuid.uuid4().hex[:8]}"

if "messages" not in st.session_state:
    st.session_state.messages = []

conversation_id = st.text_input(
    "ID de conversación",
    value=st.session_state.conversation_id,
)
st.session_state.conversation_id = conversation_id

with st.sidebar:
    st.header("Administración")

    if st.button("Ejecutar scraping + indexación"):
        with st.spinner("Procesando sitio web e indexando contenido..."):
            try:
                response = requests.post(f"{API_URL}/ingest", timeout=300)
                if response.ok:
                    st.success("Ingesta completada")
                    st.json(response.json())
                else:
                    st.error(response.text)
            except requests.RequestException as error:
                st.error(f"No fue posible ejecutar la ingesta: {error}")

    if st.button("Ver métricas"):
        try:
            response = requests.get(f"{API_URL}/analytics", timeout=30)
            if response.ok:
                st.json(response.json())
            else:
                st.error(response.text)
        except requests.RequestException as error:
            st.error(f"No fue posible consultar métricas: {error}")

    if st.button("Nueva conversación"):
        st.session_state.conversation_id = f"session_{uuid.uuid4().hex[:8]}"
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input("Escribe tu pregunta sobre el sitio web...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Consultando RAG..."):
            try:
                response = requests.post(
                    f"{API_URL}/ask",
                    json={
                        "conversation_id": conversation_id,
                        "question": question,
                    },
                    timeout=180,
                )

                if response.ok:
                    data = response.json()
                    answer = data.get("answer", "No se recibió respuesta del sistema.")
                    sources = data.get("sources", [])
                    
                    if data.get("error"):
                        st.error(data["error"])

                    st.write(answer)

                    if sources:
                        with st.expander("Fuentes recuperadas"):
                            for idx, source in enumerate(sources, start=1):
                                st.markdown(f"### Fuente {idx}")

                                if isinstance(source, dict):
                                    source_name = (
                                        source.get("source")
                                        or source.get("url")
                                        or source.get("metadata", {}).get("source")
                                        or "Fuente sin identificar"
                                    )

                                    text = (
                                        source.get("text")
                                        or source.get("content")
                                        or source.get("document")
                                        or str(source)
                                    )

                                    st.markdown(f"**Origen:** {source_name}")
                                    st.write(text[:800])
                                else:
                                    st.write(str(source)[:800])

                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )

                else:
                    st.error(response.text)

            except requests.RequestException as error:
                st.error(f"No fue posible consultar la API: {error}")