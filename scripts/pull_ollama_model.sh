#!/usr/bin/env bash
set -e
MODEL=${OLLAMA_MODEL:-llama3.2:3b}
docker exec -it rag_bank_ollama ollama pull "$MODEL"
