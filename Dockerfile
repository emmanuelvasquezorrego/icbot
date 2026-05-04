# Instalar dependencias
FROM python:3.12-slim AS builder

WORKDIR /app

# Dependencias del sistema necesarias para sentence-transformers y qdrant
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Runtime
FROM python:3.12-slim AS runtime

WORKDIR /app

# Instalar curl para healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Usuario no-root por seguridad
RUN useradd -m -u 1000 botuser

# Copiar paquetes instalados del builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código fuente y archivos auxiliares
COPY --chown=botuser:botuser . .

# Crear directorios de datos (volúmenes)
RUN mkdir -p /app/data /app/documents && \
    chown -R botuser:botuser /app/data /app/documents

USER botuser

# Puerto expuesto
EXPOSE 5000

# Health check (con curl)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Comando de inicio con Gunicorn (workers síncronos, timeout alto)
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--log-level", "info", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:app"]