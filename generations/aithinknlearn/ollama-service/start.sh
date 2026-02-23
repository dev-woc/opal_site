#!/bin/bash
set -e

echo "Starting Ollama server..."
ollama serve &
SERVER_PID=$!

# Wait until Ollama is accepting connections
echo "Waiting for Ollama to be ready..."
until curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; do
  sleep 2
done
echo "Ollama is up."

# Pull the model if not already present
MODEL="${OLLAMA_MODEL:-llama3.2}"
if ollama list | grep -q "^${MODEL}"; then
  echo "Model '${MODEL}' already present."
else
  echo "Pulling model '${MODEL}'... (this may take a few minutes on first start)"
  ollama pull "${MODEL}"
  echo "Model '${MODEL}' ready."
fi

echo "Ollama ready. Serving on port 11434."
wait $SERVER_PID
