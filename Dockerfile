# ── Base image con CUDA 12.1 + Python 3.11 ──────────────────────────────────
FROM runpod/base:0.6.2-cuda12.1.0

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MODEL_PATH=/models/Qwen-Image-Edit-2509 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# ── Dependencias del sistema ─────────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    git \
    git-lfs \
    wget \
    && git lfs install \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Dependencias de Python ───────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Descarga del modelo desde HuggingFace (sin token, es público) ────────────
RUN mkdir -p /models && \
    git clone https://huggingface.co/Qwen/Qwen-Image-Edit-2509 /models/Qwen-Image-Edit-2509

# ── Copiar el handler ────────────────────────────────────────────────────────
COPY handler.py .

# ── Comando de inicio ────────────────────────────────────────────────────────
CMD ["python3", "-u", "handler.py"]
