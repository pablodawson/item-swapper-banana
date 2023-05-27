from PIL import Image
import torch
from torch import autocast
import numpy as np
from diffusers import StableDiffusionInpaintPipeline
from utils import apply_lora, create_mask
import time
import cv2
import base64
from io import BytesIO

def init():
    global model
    global pipeline

    # Stable diffusion
    pipeline = StableDiffusionInpaintPipeline.from_pretrained(
    "runwayml/stable-diffusion-inpainting",
    torch_dtype=torch.float16,
    ).to("cuda")
    #pipeline.enable_xformers_memory_efficient_attention()
    #pipeline.enable_model_cpu_offload()

def inference(model_inputs:dict):
    global model
    global pipeline

    # Inputs
    image_b64 = model_inputs.get("image", None) # Imagen de la pieza
    seg_b64 = model_inputs.get("seg", None) # Imagen de la segmentación
    swap = model_inputs.get("swap", None) # Lista de elementos a cambiar
    inference_steps = model_inputs.get("inference_steps", 12) # Número de pasos de inferencia
    guidance_scale = model_inputs.get("guidance_scale", 20)

    if image_b64 is None:
        return {"error": "Imagen no encontrada"}
    if seg_b64 is None:
        return {"error": "Mapa de segmentación no encontrado"}
    if swap is None:
        return {"error": "Lista de elementos a cambiar no encontrada"}

    # b64 -> RGB PIL Image
    image_bytes = base64.b64decode(image_b64.encode('utf-8'))
    seg_bytes = base64.b64decode(seg_b64.encode('utf-8'))

    image = Image.open(BytesIO(image_bytes))
    seg = Image.open(BytesIO(seg_bytes))

    if (image.format=="PNG"):
        image = image.convert("RGB")
    if (seg.format=="PNG"):
        seg = seg.convert("RGB")

    width = model_inputs.get("width", 768)
    height = int(width * image.height / image.width)
    height = height - (height % 8)

     # ----
    image = image.resize((width, height), Image.BILINEAR)

    for item in swap:
        lora = item.get("lora")
        weight = item.get("weight", 1.35)
        prompt = item.get("prompt", f"A photo of {lora}")
        color = item.get("color")

        mask = create_mask(np.array(seg), color, convex_hull=item.get("convex_hull", False)).resize((width, height))
        apply_lora(pipeline, f"loras/{lora}.safetensors", weight=weight)

        timestart = time.time()

        with autocast("cuda"):
            image = pipeline(prompt, 
                        image, num_inference_steps=inference_steps, guidance_scale=guidance_scale, mask_image=mask, 
                        width=width, height=height).images[0]

        print("Time to add item: ", time.time() - timestart)
    
    buffered = BytesIO()
    image.save(buffered,format="PNG", optimize=True, quality=50)

    output_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return {"output_b64": output_base64}