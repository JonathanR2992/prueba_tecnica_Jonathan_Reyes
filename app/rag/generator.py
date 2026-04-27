import httpx

from app.config import settings


class OllamaGenerator:
    def __init__(self):
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model

    def _format_history(self, history: list[dict]) -> str:
        if not history:
            return "Sin historial previo."

        return "\n".join(
            [
                f"Usuario: {item.get('user_message', '')}\n"
                f"Asistente: {item.get('assistant_message', '')}"
                for item in history
            ]
        )

    def _format_context(self, context) -> str:
        if not context:
            return "No se recuperó contexto relevante."

        if isinstance(context, str):
            return context

        formatted_chunks = []

        for idx, item in enumerate(context, start=1):
            if isinstance(item, dict):
                text = (
                    item.get("text")
                    or item.get("content")
                    or item.get("document")
                    or str(item)
                )

                source = (
                    item.get("source")
                    or item.get("url")
                    or item.get("metadata", {}).get("source")
                    or "Fuente no identificada"
                )

                formatted_chunks.append(
                    f"[Fuente {idx}]\nOrigen: {source}\nContenido:\n{text}"
                )
            else:
                formatted_chunks.append(f"[Fuente {idx}]\n{str(item)}")

        return "\n\n".join(formatted_chunks)

    def generate(self, question: str, context, history: list[dict]) -> str:
        history_text = self._format_history(history)
        context_text = self._format_context(context)

        prompt = f"""
Eres un asistente conversacional para usuarios internos.

Tu tarea es responder preguntas usando únicamente el contexto recuperado desde el sitio web institucional del banco.

Reglas:
1. Responde solo con base en el contexto entregado.
2. Si el contexto no contiene suficiente información, responde:
   "No encontré información suficiente en las fuentes recuperadas para responder con precisión."
3. No inventes productos, requisitos, tasas, beneficios, condiciones ni datos legales.
4. Responde en español, de forma clara y estructurada.
5. Si aplica, usa viñetas.
6. No menciones información que no aparezca en el contexto recuperado.

Historial de conversación:
{history_text}

Contexto recuperado:
{context_text}

Pregunta del usuario:
{question}

Respuesta:
""".strip()

        try:
            response = httpx.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "top_p": 0.9,
                        "num_ctx": 2048,
                        "num_predict": 250,
                    },
                },
                timeout=300,
            )
            response.raise_for_status()
            return response.json().get("response", "No se recibió respuesta del modelo.")

        except Exception as exc:
            return (
                "No fue posible consultar el LLM local. "
                "Verifica que Ollama esté corriendo y que el modelo esté descargado. "
                f"Detalle técnico: {exc}"
            )