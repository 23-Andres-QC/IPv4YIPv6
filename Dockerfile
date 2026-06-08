# ═══════════════════════════════════════════════════════════════
#  IP Manager - Dockerfile
#  Imagen base: Python 3.12 slim (Debian Bookworm)
#  Etapas: build → runtime (imagen mínima)
# ═══════════════════════════════════════════════════════════════

# ─── Etapa 1: build de dependencias ───────────────────────────
FROM python:3.12-slim AS builder

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Copiar solo requirements primero (aprovecha caché de Docker)
COPY requirements.txt .

# Instalar dependencias en directorio local
RUN pip install --target=/build/packages -r requirements.txt

# ─── Etapa 2: imagen final ────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/packages

WORKDIR /app

# Copiar paquetes instalados desde builder
COPY --from=builder /build/packages /app/packages

# Copiar código fuente
COPY app/       ./app/
COPY static/    ./static/
COPY templates/ ./templates/

# Puerto de la aplicación
EXPOSE 8000

# Usuario no-root por seguridad
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Comando de inicio
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
