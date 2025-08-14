FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Dependências de sistema mínimas (psycopg2 etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /djangoapp

# 1) Copia só o requirements (agora em djangoapp/)
COPY djangoapp/requirements.txt /tmp/requirements.txt

# 2) Cria venv e instala as libs
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r /tmp/requirements.txt

# 3) Copia o app e os scripts
COPY djangoapp /djangoapp
COPY scripts /scripts

# Normaliza EOL e garante execução dos .sh
RUN sed -i 's/\r$//' /scripts/*.sh && chmod +x /scripts/*.sh

# Usuário não-root (opcional, mas recomendado)
RUN useradd -m -u 1000 duser && chown -R duser:duser /venv /djangoapp /scripts
USER duser

# PATH inclui venv e scripts
ENV PATH="/scripts:/venv/bin:$PATH"

EXPOSE 8000
CMD ["/scripts/start_app.sh"]
