import os
import torch
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
import boto3

def download_model():
    # Stable diffusion
    pipeline = StableDiffusionInpaintPipeline.from_pretrained(
    "runwayml/stable-diffusion-inpainting",
    torch_dtype=torch.float16,
    )

def download_lora_models():
    print("Downloading LORA models...")

    target = "loras/"
    s3_resource = boto3.resource('s3', aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"], aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])
    bucket = s3_resource.Bucket("item-swapper") 

    if not os.path.exists(os.path.dirname(target)):
        os.makedirs(os.path.dirname(target))

    for obj in bucket.objects.filter(Prefix = target):
        if not obj.key.endswith("/"):
            bucket.download_file(obj.key, obj.key)

if __name__ == "__main__":
    download_model()
    download_lora_models()
