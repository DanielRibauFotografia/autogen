# Dockerfile para PhotoAgent
# Baseado em Python 3.11 slim para eficiência

FROM python:3.11-slim

# Metadados do container
LABEL maintainer="Daniel Ribau Fotografia <daniel@ribaufotografia.com>"
LABEL description="PhotoAgent - Agente especializado em gerenciamento de fotos do sistema JARVIS"
LABEL version="1.0.0"

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema para processamento de imagens
RUN apt-get update && apt-get install -y \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libtiff5-dev \
    libopenjp2-7-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instala dependências gerais do sistema JARVIS
COPY ../../requirements.txt ./system_requirements.txt
RUN pip install --no-cache-dir -r system_requirements.txt

# Copia código do agente
COPY . .

# Cria diretórios necessários
RUN mkdir -p /app/photos /app/photos/processed /app/photos/backup /app/memory /app/logs

# Usuário não-root para segurança
RUN useradd -m -u 1000 photoagent && \
    chown -R photoagent:photoagent /app
USER photoagent

# Health check para verificar se o agente está funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import agent; print('PhotoAgent OK')" || exit 1

# Comando padrão para executar o agente
CMD ["python", "agent.py"]