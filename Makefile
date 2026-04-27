up:
	docker compose up --build

pull-model:
	./scripts/pull_ollama_model.sh

ingest:
	curl -X POST http://localhost:8000/ingest

health:
	curl http://localhost:8000/health
