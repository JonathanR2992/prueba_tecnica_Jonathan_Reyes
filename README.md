# RAG Bank Assistant

Asistente conversacional basado en Retrieval-Augmented Generation (RAG) que permite responder preguntas utilizando información extraída dinámicamente desde el sitio web institucional del banco.

## 1. Objetivo

Este sistema implementa un pipeline completo de RAG que incluye:

1. Scraping web automatizado
2. Limpieza y procesamiento de texto
3. Generación de embeddings
4. Almacenamiento vectorial con ChromaDB
5. Recuperación semántica de información
6. Generación de respuestas usando LLM local (Ollama)

El objetivo es construir un asistente confiable que responda únicamente con información verificada del sitio institucional, evitando alucinaciones del modelo.

## 2. Arquitectura del sistema

[Usuario] 
    ↓ 
[Streamlit UI] 
    ↓ 
[FastAPI Backend] 
    ↓ 
[RAG Service (Facade)] 
    ↓ 
[Retrieval Strategy] 
    ↓ 
[ChromaDB Vector Store] 
    ↓ 
[Ollama LLM] 
    ↓ 
[Respuesta + Fuentes]

## 3. Stack tecnológico

    - Python 3.11
    - FastAPI
    - Streamlit
    - ChromaDB
    - SentenceTransformers
    - Ollama (LLM local)
    - Docker & Docker Compose
    - BeautifulSoup (scraping)

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

## 4. Requisitos previos

- Docker instalado.
- Docker Compose instalado.
- Git instalado.
- Al menos 6 GB de RAM disponibles si se usa Ollama con modelo local.

## 5. Estructura del proyecto

app/ 
├── api/ # Endpoints (FastAPI) 
├── scraping/ # Scraper y limpieza 
├── rag/ # Embeddings, chunking, vector store 
├── patterns/ # Facade, Strategy, Factory 
├── conversation/ # Memoria conversacional 
├── analytics/ # Métricas 
└── config.py # Configuración central 

streamlit_app.py # Frontend 
docker-compose.yml # Orquestación 
.env # Configuración

## 6. Flujo de funcionamiento

  1. Ingesta de datos (ETL)

  El sistema ejecuta automáticamente:

  Scraping → Cleaning → Chunking → Embeddings → Indexación

  Esto se activa desde la UI con:

  "Ejecutar raspado + indexación"

  2. Consulta RAG

  Cuando el usuario realiza una pregunta:

  Se recupera contexto relevante desde ChromaDB
  Se construye un prompt con:
  Contexto
  Historial conversacional
  Se consulta el LLM local (Ollama)
  Se retorna:
  Respuesta generada
  Fuentes utilizadas

## 7. Configuración inicial

Clonar el repositorio:

```bash
git clone https://github.com/JonathanR2992/prueba_tecnica_Jonathan_Reyes.git
cd prueba_tecnica_Jonathan_Reyes
```

Crear el archivo `.env`:

```bash
cp .env .env
```

 -- NOTA --
  El archivo .env debe estar de la siguiente manera:
  # =========================
  # App
  # =========================
  APP_NAME=RAG Bank Assistant
  API_HOST=0.0.0.0
  API_PORT=8000
  ANONYMIZED_TELEMETRY=False
  CHROMA_TELEMETRY=False

  # =========================
  # Scraping
  # =========================
  TARGET_BASE_URL=https://www.bbva.com.co/
  MAX_PAGES=30
  REQUEST_TIMEOUT=10
  USER_AGENT=Mozilla/5.0 (compatible; RAGBankAssistant/1.0)

  # =========================
  # RAG (Optimizado para phi)
  # =========================
  CHUNK_SIZE=500
  CHUNK_OVERLAP=100
  TOP_K=3
  USE_RERANKER=False
  CONVERSATION_WINDOW_N=3

  # =========================
  # Models
  # =========================
  EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
  LLM_PROVIDER=ollama
  OLLAMA_BASE_URL=http://ollama:11434
  OLLAMA_MODEL=phi

  # =========================
  # Storage (CONSISTENTE CON EL CÓDIGO)
  # =========================
  RAW_DATA_PATH=data/raw
  CLEAN_DATA_PATH=data/clean
  CHROMA_PATH=data/chroma
  SQLITE_PATH=data/conversations.db

-- / --

## 8. Levantar el proyecto

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

## 9. Descargar el modelo de Ollama

```bash
docker exec -it rag_bank_ollama ollama pull phi
```

## 10. Uso del sistema

### Usar la UI

1. Abrir `http://localhost:8501`.
2. Presionar `Ejecutar raspado + indexación`.
3. Esperar a que termine la ingesta.
4. Escribir una pregunta en el chat.
    Ejemplos:
      ¿Qué puedo hacer con la App BBVA?
      ¿Cómo abrir una cuenta de ahorros?
5. Revisar la respuesta y las fuentes recuperadas.


## 11. Patrones de diseño implementados

### 11.1 Uso de RAG

Se evita que el modelo genere respuestas incorrectas utilizando únicamente contexto recuperado.

### 11.2 Modelo LLM (phi)

Se seleccionó un modelo liviano para:

Reducir latencia
Permitir ejecución en CPU
Evitar timeouts en Docker

### 11.3 ChromaDB

Elegido por:

Persistencia local
Simplicidad de integración
Buen rendimiento en pruebas técnicas

### 11.4 Arquitectura con patrones

Se implementaron:

Factory → desacopla la creación de componentes
Strategy → permite cambiar la estrategia de recuperación
Facade → simplifica el uso del sistema RAG

#### 11.4.1 Factory Method

Archivo: `app/patterns/factory.py`

Se usa para centralizar la creación de componentes como:

- Vector store.
- Generador LLM.

Justificación: permite cambiar implementaciones futuras, por ejemplo pasar de ChromaDB a Qdrant o de Ollama a una API externa, sin modificar todo el sistema.

#### 11.4.2 Strategy

Archivo: `app/patterns/strategy.py`

Se usa para intercambiar estrategias de recuperación:

- `BasicRetrievalStrategy`: búsqueda vectorial directa.
- `RerankedRetrievalStrategy`: búsqueda vectorial + reranking TF-IDF.

Justificación: permite activar o desactivar el reranker desde configuración sin cambiar la lógica principal del RAG.

#### 11.4.3 Facade

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

## 12. Historial de conversación

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

## 13. Análisis de datos

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

## 14. Manejo de errores

El sistema incluye manejo básico de errores en:

- Scraping de páginas con `try/except`.
- Endpoint `/ingest` con respuesta HTTP 500 controlada.
- Validación de pregunta vacía.
- Fallback cuando Ollama no está disponible.

## 15. Limitaciones conocidas

- El scraping está diseñado para HTML estático. Si el sitio carga contenido con JavaScript, se podría requerir Playwright o Selenium.
- El reranker implementado usa TF-IDF por simplicidad y costo cero. Una mejora sería usar CrossEncoder de SentenceTransformers.
- La respuesta depende de tener descargado el modelo de Ollama.
- No se implementó autenticación porque no fue solicitada para la prueba técnica.
- El scraping debe respetar las políticas del sitio objetivo y su `robots.txt`.

## 16. Futuras mejoras

- Agregar Playwright para sitios con renderizado dinámico.
- Implementar CrossEncoder reranker.
- Añadir evaluación automática de RAG: faithfulness, answer relevance y context precision.
- Implementar autenticación para usuarios internos.
- Agregar panel de analítica en Streamlit con gráficas.
- Programar ingestas periódicas.
- Agregar tests unitarios y de integración.
- Agregar CI/CD con GitHub Actions.

## 17. Decisiones de diseño

Ante ambigüedades del enunciado, se asumió lo siguiente:

- El banco objetivo puede configurarse mediante `TARGET_BASE_URL`.
- La persistencia local es válida usando SQLite y ChromaDB persistente.
- El LLM puede ejecutarse localmente con Ollama para evitar costos.
- La UI no busca ser visualmente sofisticada, sino funcional, limpia y evaluable.

## 18. Uso de Inteligencia Artificial durante el desarrollo

El desarrollo de esta prueba técnica contó con el apoyo de herramientas de Inteligencia Artificial generativa (como asistentes de código) para:

- Acelerar la estructuración del proyecto.
- Validar enfoques de arquitectura.
- Generar ejemplos base de código.
- Depurar errores durante la implementación.

Sin embargo:

- La arquitectura, integración de componentes y decisiones técnicas fueron definidas, ajustadas y validadas manualmente.
- Se realizaron múltiples iteraciones de debugging, integración y pruebas para asegurar el correcto funcionamiento del sistema.
- El resultado final refleja comprensión completa del pipeline RAG, su implementación y sus trade-offs.

Este enfoque es consistente con prácticas modernas de desarrollo, donde la IA actúa como herramienta de apoyo, pero la responsabilidad técnica recae en el ingeniero.

## Autor

Jonathan Reyes
Ingeniero Electrónico | Data Science & Machine Learning