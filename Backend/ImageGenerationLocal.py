import requests
import base64
import os
import time

SD_API = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUTPUT_DIR = "Data"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_image_local(prompt: str, steps=25, width=512, height=512):
    payload = {
        "prompt": prompt,
        "steps": steps,
        "width": width,
        "height": height,
        "sampler_name": "Euler a"
    }

    # Added timeout for safety
    response = requests.post(SD_API, json=payload, timeout=120)
    response.raise_for_status()

    images = response.json()["images"]
    if not images:
        raise RuntimeError("No image generated")

    img_data = base64.b64decode(images[0])
    filename = f"{prompt.replace(' ', '_')}_{int(time.time())}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(img_data)

    return filepath
