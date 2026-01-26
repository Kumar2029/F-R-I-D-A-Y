import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep
import base64
import json

# Set API URL and headers
API_URL = "https://api-inference.huggingface.co/models/prompthero/openjourney"
api_key = get_key('.env', 'HuggingFaceAPIKey')
if not api_key:
    print("DEBUG: HuggingFaceAPIKey is MISSING in .env")
else:
    print(f"DEBUG: HuggingFaceAPIKey loaded (Length: {len(api_key)})")
    
headers = {"Authorization": f"Bearer {api_key}"}

# Ensure the Data folder exists
if not os.path.exists("Data"):
    os.makedirs("Data")

def open_images(prompt):
    folder_path = r"Data"
    prompt = prompt.replace(" ", "_")
    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)

        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)

        except IOError:
            print(f"Unable to open {image_path}. Ensure the image file exists and is valid.")

async def query(payload):
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for HTTP failures
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error querying API: {e}")
        return None

# PART 4: IMAGE MODEL ROTATION
IMAGE_MODELS = [
    "runwayml/stable-diffusion-v1-5",
    "stabilityai/stable-diffusion-2-1",
    "prompthero/openjourney",
    "stabilityai/stable-diffusion-xl-base-1.0",
    "black-forest-labs/FLUX.1-schnell"
]

def get_api_url(model_path):
    # Support both direct inference and router endpoints just in case, but standardizing on inference
    # for simplicity unless specific models need router.
    # The user testing showed "router" URL failed too.
    # We will try standard inference first.
    return f"https://api-inference.huggingface.co/models/{model_path}"

async def generate_images_with_rotation(prompt: str):
    # Try each model in order
    for model in IMAGE_MODELS:
        print(f"[ImageGen] Attempting model: {model}")
        
        global API_URL
        API_URL = get_api_url(model)
        
        # Reset tasks for this attempt
        tasks = []
        for i in range(4):
            seed = randint(0, 1000000)
            payload = {
                "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High details, high resolution, seed={seed}"
            }
            task = asyncio.create_task(query(payload))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        
        # Check if ANY response is valid (not None)
        valid_responses = [r for r in responses if r is not None]
        
        if not valid_responses:
             print(f"[ImageGen] Model {model} returned no data. Rotating...")
             # Improve Strategy Health for model? The user requirement is 'record failure per model'
             # but StrategyHealth is at 'Strategy' level (all models = 1 strategy).
             # We can just log it here as requested.
             continue
             
        # Check if actual error in content (JSON error)
        # We need at least one success to claim this model worked.
        model_success = False
        
        for i, response_content in enumerate(responses):
            if response_content:
                try:
                    response_json = json.loads(response_content)
                    if "images" in response_json:
                        # Success!
                        image_base64 = response_json["images"][0]
                        image_bytes = base64.b64decode(image_base64)
                        with open(fr"Data\{prompt.replace(' ', '_')}{i + 1}.jpg", "wb") as f:
                            f.write(image_bytes)
                        model_success = True
                    elif "error" in response_json:
                         print(f"[ImageGen] Model {model} Error: {response_json['error']}")
                except Exception as e:
                    print(f"[ImageGen] Save Error: {e}")
        
        if model_success:
            print(f"[ImageGen] Success with model: {model}")
            return # Exit loop, we are done
            
        print(f"[ImageGen] Model {model} failed to produce images. Rotating...")

    raise Exception("All image models failed")

async def generate_images(prompt: str):
    # Wrapper to maintain async signature called by GenerateImages
    await generate_images_with_rotation(prompt)

def GenerateImages(prompt: str):
    print(f"DEBUG: CWD is {os.getcwd()}")
    asyncio.run(generate_images(prompt))
    
    # Check if images exist before opening
    folder_path = r"Data"
    prompt_safe = prompt.replace(" ", "_")
    files = [f"{prompt_safe}{i}.jpg" for i in range(1, 5)]
    found = False
    for f in files:
        full_path = os.path.abspath(os.path.join(folder_path, f))
        print(f"DEBUG: Checking {full_path}")
        if os.path.exists(full_path):
            print(f"DEBUG: Found {full_path}")
            found = True
            break
            
    if not found:
        raise Exception("Image Generation Failed: No images were saved (Check API Key or Model Status)")
        
    open_images(prompt)

if __name__ == "__main__":
    # Main execution loop
    while True:
        try:
            with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
                data = str(f.read())

            prompt, status = data.split(",")
            status = status.strip()

            if status.lower() == "true":
                print("Generating Images...")
                GenerateImages(prompt=prompt)

                with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                    f.write("False, False")
                break
            else:
                sleep(1)

        except :
            pass