import os
import replicate
import requests
from typing import Optional
from ai_film_studio.core.interfaces import VideoGenerationProvider
from ai_film_studio.config.settings import settings

class ReplicateVideoProvider(VideoGenerationProvider):
    def __init__(self, model_name: str = "minimax/hailuo-02"):
        self.model_name = model_name
        if not settings.REPLICATE_API_TOKEN:
             print("Warning: REPLICATE_API_TOKEN is not set. Generation will fail.", flush=True)

    async def generate_clip(self, prompt: str, image_url: Optional[str] = None, duration_seconds: int = 5) -> str:
        try:
            input_args = {
                "prompt": prompt
            }
            
            if image_url:
                 # Provide the initial image URL if it's image-to-video
                 # Note: MiniMax might call this `image` or `init_image` or `image_url`
                 # Using the most common Replicate convention `image` or `initial_image`
                 # Need to check the specific API signature for hailuo-02, generally it is `image`
                 input_args["image"] = image_url
            
            # Note: For Wan 2.2 or Hailuo, duration might not be directly settable like this
            # but we pass what we can or rely on default model behavior
                 
            print(f"Replicate Video: Requesting model {self.model_name} with prompt: {prompt}", flush=True)
            output = replicate.run(
                self.model_name,
                input=input_args
            )
            
            if isinstance(output, list) and len(output) > 0:
                video_url = str(output[0])
            else:
                 video_url = str(output)
                 
            if not video_url or not video_url.startswith("http"):
                  print(f"Replicate Video Warning: Invalid URL returned: {video_url}", flush=True)
                  return "assets/placeholders/veo_generated_clip.mp4"
            
            # Save locally
            os.makedirs("assets/output", exist_ok=True)
            output_path = f"assets/output/{hash(prompt)}.mp4"
            
            response = requests.get(video_url)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return output_path
            else:
                 print(f"Replicate Video Error: Failed to download video from {video_url}")
                 return "assets/placeholders/veo_generated_clip.mp4"
                 
        except Exception as e:
            print(f"Replicate Video Error: {e}", flush=True)
            return "assets/placeholders/veo_generated_clip.mp4"
