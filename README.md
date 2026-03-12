# 🖼️ RunPod Worker — Qwen-Image-Edit-2509

Worker serverless para RunPod que usa el modelo **Qwen-Image-Edit-2509** de Alibaba para editar imágenes con instrucciones en texto natural.

---

## 📁 Estructura del proyecto

```
qwen-image-edit-worker/
├── Dockerfile
├── handler.py
├── requirements.txt
├── test_input.json
└── README.md
```

---

## 🚀 Paso a paso para deployar

### PASO 1 — Crear el repositorio en GitHub

1. Andá a [github.com](https://github.com) y creá un repositorio nuevo
   - Nombre sugerido: `qwen-image-edit-worker`
   - Visibilidad: **Public** (RunPod lo necesita así para el build automático)
2. Subí todos los archivos de esta carpeta al repo

```bash
git init
git add .
git commit -m "Initial worker setup"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/qwen-image-edit-worker.git
git push -u origin main
```

---

### PASO 2 — Conectar GitHub con RunPod

1. Entrá a [runpod.io](https://runpod.io) → **Settings**
2. Buscá la sección **Connections** → **GitHub**
3. Hacé click en **Connect** y autorizá tu cuenta de GitHub
4. Seleccioná el repositorio `qwen-image-edit-worker`

---

### PASO 3 — Crear el Endpoint Serverless

1. Andá a **Serverless** → **New Endpoint**
2. En **Custom Source** seleccioná → **GitHub Repository**
3. Elegí tu repo `qwen-image-edit-worker` y la rama `main`
4. En **Worker Configuration** elegí la GPU:
   - ✅ **Recomendado: A40 (48GB VRAM)** — corre sin problemas
   - ✅ **Alternativa: A100 80GB** — más rápido pero más caro
   - ⚠️ **Mínimo: RTX 4090 (24GB)** — puede quedar justo
5. Hacé click en **Create Endpoint**
6. RunPod va a buildear la imagen automáticamente (tarda ~10-15 min la primera vez)

---

### PASO 4 — Hacer un request de prueba

Una vez que el endpoint esté activo, podés probarlo desde el panel de RunPod o con curl:

```bash
curl -X POST https://api.runpod.ai/v2/TU_ENDPOINT_ID/runsync \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_API_KEY" \
  -d '{
    "input": {
      "prompt": "Change the background to a beautiful sunset beach",
      "images": ["<BASE64_DE_TU_IMAGEN>"],
      "num_inference_steps": 40,
      "seed": 42
    }
  }'
```

La respuesta va a tener el campo `"image"` con la imagen editada en base64.

---

## 📥 Parámetros del endpoint

| Campo | Tipo | Requerido | Default | Descripción |
|-------|------|-----------|---------|-------------|
| `prompt` | string | ✅ Sí | — | Instrucción de edición |
| `images` | array | ✅ Sí | — | 1 a 3 imágenes en base64 |
| `negative_prompt` | string | No | `" "` | Qué evitar en la imagen |
| `num_inference_steps` | int | No | `40` | Pasos de inferencia |
| `true_cfg_scale` | float | No | `4.0` | Escala CFG |
| `guidance_scale` | float | No | `1.0` | Escala de guiado |
| `seed` | int | No | `null` | Semilla para reproducibilidad |

---

## 💡 Ejemplos de prompts

```
"Turn the background into a snowy mountain landscape"
"Make the person wear a red jacket"
"Add a rainbow in the sky"
"Convert the image to anime style"
"Remove the person from the background"
"Change the text on the sign to 'Hello World'"
```

---

## ⚠️ Notas importantes

- El **primer arranque** del worker es lento (~2-3 min) porque carga el modelo en VRAM
- Los arranques siguientes son mucho más rápidos
- El modelo pesa ~35GB, el build de Docker tarda la primera vez
- Para uso frecuente, considerá usar un **Network Volume** en lugar de clonar el modelo en cada build

---

## 🔧 Convertir imagen a base64 en Python

```python
import base64

with open("mi_imagen.jpg", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")
print(b64)
```

---

## 📦 Decodificar la imagen de respuesta en Python

```python
import base64
from PIL import Image
import io

b64_result = response_json["output"]["image"]
image_data = base64.b64decode(b64_result)
image = Image.open(io.BytesIO(image_data))
image.save("resultado.png")
```
