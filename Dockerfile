# ── Base image PyTorch oficial de RunPod con CUDA 12.4 ──────────────────────
FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

# El modelo vive en el Network Volume
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MODEL_PATH=/runpod-volume/Qwen-Image-Edit-2509 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# ── Dependencias de Python ───────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copiar el handler (el modelo viene del Network Volume en /runpod-volume) ─
COPY handler.py .

# ── Comando de inicio ────────────────────────────────────────────────────────
CMD ["python3", "-u", "handler.py"]
