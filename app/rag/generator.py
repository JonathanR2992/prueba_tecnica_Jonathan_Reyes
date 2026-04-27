import httpx

from app.config import settings


class OllamaGenerator:
    def __init__(self):
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model

    def generate(self, question: str, context: str, history: list[dict]) -> str:
        history_text = "\n".join([f"Usuario: {h['user_message']}\nAsistente: {h['assistant_message']}" for h in history])
        prompt = f"""
Eres un asistente interno que responde únicamente con base en el contexto recuperado del sitio web.
Si la respuesta no está en el contexto, dilo claramente y sugiere consultar la fuente oficial.

Historial reciente:
{history_text}

Contexto recuperado:
{context}

Pregunta del usuario:
{question}

Respuesta clara, breve y sustentada:
""".strip()

        try:
            response = httpx.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=120,
            )
            response.raise_for_status()
            return response.json().get("response", "No se recibió respuesta del modelo.")
        except Exception as exc:
            return (
                "No fue posible consultar el LLM local. "
                "Verifica que Ollama esté corriendo y que el modelo esté descargado. "
                f"Detalle técnico: {exc}"
            )
