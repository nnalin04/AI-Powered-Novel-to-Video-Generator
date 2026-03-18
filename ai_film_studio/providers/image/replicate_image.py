import os
import replicate
import requests
from typing import Optional, List
from ai_film_studio.core.interfaces import ImageGenerationProvider
from ai_film_studio.config.settings import settings

class ReplicateImageProvider(ImageGenerationProvider):
    def __init__(self, model_name: str = "black-forest-labs/flux-2-pro"):
        self.model_name = model_name
        if not settings.REPLICATE_API_TOKEN:
             print("Warning: REPLICATE_API_TOKEN is not set. Generation will fail.", flush=True)

    async def generate_image(self, prompt: str, negative_prompt: str = "", width: int = 1024, height: int = 1024, reference_images: Optional[List[str]] = None) -> str:
        try:
            input_args = {
                "prompt": prompt,
                "width": width,
                "height": height,
                "output_format": "webp"
            }
            
            # Map up to 8 reference images if provided
            if reference_images:
                # Take up to 8 as per flux-2-pro specs
                refs = reference_images[:8]
                for i, ref_url in enumerate(refs):
                    input_args[f"image_prompt_{i+1}"] = ref_url
                    
            print(f"Replicate Image: Requesting model {self.model_name} with prompt: {prompt}", flush=True)
            output = replicate.run(
                self.model_name,
                input=input_args
            )
            
            # Replicate output is usually a FileOutput object or a list of them
            # We extract the URL and download it locally for the pipeline
            if isinstance(output, list) and len(output) > 0:
                image_url = str(output[0])
            else:
                 image_url = str(output)
                 
            if not image_url or not image_url.startswith("http"):
                  print(f"Replicate Image Warning: Invalid URL returned: {image_url}", flush=True)
                  return "assets/placeholders/no_image_generated.png"
                  
            # Save locally
            os.makedirs("assets/generated_images", exist_ok=True)
            output_path = f"assets/generated_images/{hash(prompt)}.webp"
            
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return output_path
            else:
                 print(f"Replicate Image Error: Failed to download image from {image_url}")
                 return "assets/placeholders/no_image_generated.png"

        except Exception as e:
            print(f"Replicate Image Error: {e}", flush=True)
            return "assets/placeholders/no_image_generated.png"
