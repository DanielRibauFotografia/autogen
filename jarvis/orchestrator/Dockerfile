# Dockerfile para Orchestrator
FROM python:3.11-slim

LABEL maintainer="Daniel Ribau Fotografia <daniel@ribaufotografia.com>"
LABEL description="Orchestrator - Orquestrador principal do sistema JARVIS"

WORKDIR /app

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instala dependências gerais do sistema
COPY ../requirements.txt ./system_requirements.txt
RUN pip install --no-cache-dir -r system_requirements.txt

# Copia código do orquestrador
COPY . .

# Cria diretórios necessários
RUN mkdir -p /app/memory /app/logs

# Usuário não-root
RUN useradd -m -u 1000 orchestrator && \
    chown -R orchestrator:orchestrator /app
USER orchestrator

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import orchestrator; print('Orchestrator OK')" || exit 1

CMD ["python", "orchestrator.py"]