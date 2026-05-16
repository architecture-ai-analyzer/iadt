# Multi-stage build para otimizar tamanho da imagem
from python:3.11-slim as builder

# Instalar dependências do sistema necessárias para compilar pacotes
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Criar virtual env
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar requirements
COPY project/pyproject.toml /tmp/
WORKDIR /tmp

# Instalar dependências Python
RUN pip install --upgrade pip setuptools wheel && \
    pip install -e .

# Stage final - imagem de produção
from python:3.11-slim

# Sem dependências runtime adicionais necessárias

# Copiar virtual env do builder
COPY --from=builder /opt/venv /opt/venv

# Definir variáveis de ambiente
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Criar user não-root por segurança
RUN groupadd -r iadt && useradd -r -g iadt iadt

# Definir diretório de trabalho
WORKDIR /app

# Copiar código do projeto
COPY project/ .
COPY project/worker.py .

# Alterar permissões
RUN chown -R iadt:iadt /app

# Trocar para user não-root
USER iadt

# Health check simples
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Entrypoint - executar worker
ENTRYPOINT ["python", "-m", "worker"]
