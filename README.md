# RAG Bank Assistant

Sistema RAG con web scraping para consultar información publicada en un sitio web bancario institucional.

## 1. Objetivo

El proyecto implementa un asistente conversacional que:

1. Extrae contenido del sitio web configurado.
2. Guarda datos crudos y limpios en local.
3. Divide, vectoriza e indexa el contenido en ChromaDB.
4. Expone una API conversacional con FastAPI.
5. Expone una UI minimalista con Streamlit.
6. Mantiene historial conversacional persistente por `conversation_id`.
7. Usa los últimos `N` mensajes como memoria conversacional configurable.
8. Incluye métricas básicas sobre el histórico de conversaciones.
9. Implementa tres patrones de diseño: Factory Method, Strategy y Facade.

## 2. Stack tecnológico

| Componente | Tecnología | Justificación |
|---|---|---|
| Lenguaje | Python | Requisito obligatorio y ecosistema robusto para ML/IA. |
| API | FastAPI | Ligero, rápido y adecuado para servicios ML. |
| UI | Streamlit | Permite una interfaz conversacional limpia con poco código. |
| Scraping | Requests + BeautifulSoup | Stack simple, estable y suficiente para páginas HTML. |
| Vector DB | ChromaDB | Base vectorial local, gratuita y persistente. |
| Embeddings | Sentence Transformers | Embeddings open source sin costo por API. |
| LLM | Ollama | Ejecución local de modelos open source. |
| Historial | SQLite | Persistencia local simple, portable y suficiente para la prueba. |
| Docker | Docker + Compose | Permite levantar API, UI y Ollama con un solo comando. |

## 3. Requisitos previos

- Docker instalado.
- Docker Compose instalado.
- Git instalado.
- Al menos 6 GB de RAM disponibles si se usa Ollama con modelo local.

## 4. Configuración inicial

Clonar el repositorio:

```bash
git clone https://github.com/JonathanR2992/prueba_tecnica_Jonathan_Reyes.git
cd rag-bbva-assistant
```

Crear el archivo `.env`:

```bash
cp .env.example .env
```

Variables principales:

```env
TARGET_BASE_URL=https://www.bbva.com.co/
MAX_PAGES=30
CHUNK_SIZE=900
CHUNK_OVERLAP=150
TOP_K=5
USE_RERANKER=true
CONVERSATION_WINDOW_N=6
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:3b
```

## 5. Levantar el proyecto

```bash
docker compose up --build
```

La API quedará disponible en:

```text
http://localhost:8000
```

La interfaz Streamlit quedará disponible en:

```text
http://localhost:8501
```

## 6. Descargar el modelo de Ollama

En otra terminal, después de levantar los servicios:

```bash
chmod +x scripts/pull_ollama_model.sh
./scripts/pull_ollama_model.sh
```

También puede ejecutarse manualmente:

```bash
docker exec -it rag_bank_ollama ollama pull llama3.2:3b
```

## 7. Uso del sistema

### Opción 1: usar la UI

1. Abrir `http://localhost:8501`.
2. Presionar `Ejecutar scraping + indexación`.
3. Esperar a que termine la ingesta.
4. Escribir una pregunta en el chat.
5. Revisar la respuesta y las fuentes recuperadas.

### Opción 2: usar la API

Health check:

```bash
curl http://localhost:8000/health
```

Ejecutar scraping e indexación:

```bash
curl -X POST http://localhost:8000/ingest
```

Preguntar al sistema:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "session_001",
    "question": "¿Qué productos de ahorro ofrece el banco?"
  }'
```

Consultar métricas:

```bash
curl http://localhost:8000/analytics
```

## 8. Patrones de diseño implementados

### 8.1 Factory Method

Archivo: `app/patterns/factory.py`

Se usa para centralizar la creación de componentes como:

- Vector store.
- Generador LLM.

Justificación: permite cambiar implementaciones futuras, por ejemplo pasar de ChromaDB a Qdrant o de Ollama a una API externa, sin modificar todo el sistema.

### 8.2 Strategy

Archivo: `app/patterns/strategy.py`

Se usa para intercambiar estrategias de recuperación:

- `BasicRetrievalStrategy`: búsqueda vectorial directa.
- `RerankedRetrievalStrategy`: búsqueda vectorial + reranking TF-IDF.

Justificación: permite activar o desactivar el reranker desde configuración sin cambiar la lógica principal del RAG.

### 8.3 Facade

Archivo: `app/patterns/facade.py`

Clase principal: `RAGService`.

Encapsula:

- Carga de historial.
- Recuperación de documentos.
- Reranking.
- Construcción de contexto.
- Generación de respuesta.
- Persistencia de conversación.

Justificación: expone una interfaz simple `ask()` para que la API no conozca los detalles internos del pipeline RAG.

## 9. Historial de conversación

El sistema guarda cada interacción en SQLite con:

- `conversation_id`
- `user_message`
- `assistant_message`
- `created_at`

La memoria conversacional toma los últimos `N` mensajes según:

```env
CONVERSATION_WINDOW_N=6
```

Esto permite que una misma sesión conserve contexto sin mezclar conversaciones distintas.

## 10. Análisis de datos

Endpoint:

```text
GET /analytics
```

Métricas incluidas:

- Total de mensajes.
- Total de conversaciones únicas.
- Longitud promedio de preguntas.
- Términos frecuentes en preguntas de usuarios.

Estas métricas permiten estimar uso, temas consultados e impacto potencial del asistente.

## 11. Manejo de errores

El sistema incluye manejo básico de errores en:

- Scraping de páginas con `try/except`.
- Endpoint `/ingest` con respuesta HTTP 500 controlada.
- Validación de pregunta vacía.
- Fallback cuando Ollama no está disponible.

## 12. Limitaciones conocidas

- El scraping está diseñado para HTML estático. Si el sitio carga contenido con JavaScript, se podría requerir Playwright o Selenium.
- El reranker implementado usa TF-IDF por simplicidad y costo cero. Una mejora sería usar CrossEncoder de SentenceTransformers.
- La respuesta depende de tener descargado el modelo de Ollama.
- No se implementó autenticación porque no fue solicitada para la prueba técnica.
- El scraping debe respetar las políticas del sitio objetivo y su `robots.txt`.

## 13. Futuras mejoras

- Agregar Playwright para sitios con renderizado dinámico.
- Implementar CrossEncoder reranker.
- Añadir evaluación automática de RAG: faithfulness, answer relevance y context precision.
- Implementar autenticación para usuarios internos.
- Agregar panel de analítica en Streamlit con gráficas.
- Programar ingestas periódicas.
- Agregar tests unitarios y de integración.
- Agregar CI/CD con GitHub Actions.

## 14. Decisiones de diseño

Ante ambigüedades del enunciado, se asumió lo siguiente:

- El banco objetivo puede configurarse mediante `TARGET_BASE_URL`.
- La persistencia local es válida usando SQLite y ChromaDB persistente.
- El LLM puede ejecutarse localmente con Ollama para evitar costos.
- La UI no busca ser visualmente sofisticada, sino funcional, limpia y evaluable.
