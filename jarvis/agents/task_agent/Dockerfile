# Dockerfile para MarketingAgent
FROM python:3.11-slim

LABEL maintainer="Daniel Ribau Fotografia <daniel@ribaufotografia.com>"
LABEL description="MarketingAgent - Agente de marketing do sistema JARVIS"

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instala dependências gerais do sistema
COPY ../../requirements.txt ./system_requirements.txt
RUN pip install --no-cache-dir -r system_requirements.txt

# Copia código do agente
COPY . .

# Cria diretórios necessários
RUN mkdir -p /app/memory /app/logs

# Usuário não-root
RUN useradd -m -u 1000 marketingagent && \
    chown -R marketingagent:marketingagent /app
USER marketingagent

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import agent; print('MarketingAgent OK')" || exit 1

CMD ["python", "agent.py"]