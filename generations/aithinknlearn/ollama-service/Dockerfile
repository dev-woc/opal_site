FROM ollama/ollama:latest

# Model to pull on first start (override with OLLAMA_MODEL env var)
ENV OLLAMA_MODEL=llama3.2
ENV OLLAMA_KEEP_ALIVE=-1

EXPOSE 11434

COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
