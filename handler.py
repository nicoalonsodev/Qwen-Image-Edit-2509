import runpod
import torch
import base64
import io
import os
from PIL import Image
from diffusers import QwenImageEditPlusPipeline

# ── Carga del modelo una sola vez al iniciar el worker ──────────────────────
print("Cargando modelo Qwen-Image-Edit-2509...")

MODEL_PATH = os.environ.get("MODEL_PATH", "/models/Qwen-Image-Edit-2509")

pipeline = QwenImageEditPlusPipeline.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.bfloat16
)
pipeline.to("cuda")
print("Modelo cargado correctamente.")


# ── Helpers ─────────────────────────────────────────────────────────────────

def decode_base64_image(b64_string: str) -> Image.Image:
    """Decodifica una imagen en base64 y devuelve un objeto PIL Image."""
    image_data = base64.b64decode(b64_string)
    return Image.open(io.BytesIO(image_data)).convert("RGB")


def encode_image_to_base64(image: Image.Image) -> str:
    """Codifica un PIL Image a base64 string (PNG)."""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


# ── Handler principal ────────────────────────────────────────────────────────

def handler(event):
    """
    Input esperado:
    {
        "input": {
            "prompt": "Turn the sky into a starry night",
            "images": ["<base64_image_1>", "<base64_image_2>"],  // 1 a 3 imágenes
            "negative_prompt": " ",          // opcional
            "num_inference_steps": 40,       // opcional, default 40
            "true_cfg_scale": 4.0,           // opcional, default 4.0
            "guidance_scale": 1.0,           // opcional, default 1.0
            "seed": 42                        // opcional
        }
    }

    Output:
    {
        "image": "<base64_png>"
    }
    """
    try:
        job_input = event.get("input", {})

        # ── Validaciones ────────────────────────────────────────────────────
        prompt = job_input.get("prompt")
        if not prompt:
            return {"error": "El campo 'prompt' es obligatorio."}

        images_b64 = job_input.get("images")
        if not images_b64 or len(images_b64) == 0:
            return {"error": "El campo 'images' es obligatorio y debe tener al menos 1 imagen."}

        if len(images_b64) > 3:
            return {"error": "Máximo 3 imágenes por request."}

        # ── Parámetros opcionales ───────────────────────────────────────────
        negative_prompt     = job_input.get("negative_prompt", " ")
        num_inference_steps = int(job_input.get("num_inference_steps", 40))
        true_cfg_scale      = float(job_input.get("true_cfg_scale", 4.0))
        guidance_scale      = float(job_input.get("guidance_scale", 1.0))
        seed                = job_input.get("seed", None)

        # ── Decodificar imágenes ────────────────────────────────────────────
        pil_images = [decode_base64_image(img) for img in images_b64]
        # Si hay una sola imagen, pasarla directo; si hay varias, en lista
        image_input = pil_images[0] if len(pil_images) == 1 else pil_images

        # ── Generador con seed ──────────────────────────────────────────────
        generator = None
        if seed is not None:
            generator = torch.manual_seed(int(seed))

        # ── Inferencia ──────────────────────────────────────────────────────
        print(f"Procesando job | prompt: {prompt[:80]}... | imágenes: {len(pil_images)}")

        with torch.inference_mode():
            output = pipeline(
                image=image_input,
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=num_inference_steps,
                true_cfg_scale=true_cfg_scale,
                guidance_scale=guidance_scale,
                num_images_per_prompt=1,
                generator=generator,
            )

        result_image = output.images[0]

        # ── Codificar resultado ─────────────────────────────────────────────
        result_b64 = encode_image_to_base64(result_image)
        print("Job completado exitosamente.")

        return {"image": result_b64}

    except Exception as e:
        print(f"Error en el handler: {str(e)}")
        return {"error": str(e)}


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
