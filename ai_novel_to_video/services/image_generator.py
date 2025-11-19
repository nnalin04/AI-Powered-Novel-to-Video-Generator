import os
import time
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
import logging

# Setup logger for retry attempts
logger = logging.getLogger(__name__)

# Try importing vertexai, but handle the case where it's not installed or credentials fail
try:
    import vertexai
    from vertexai.preview.vision_models import ImageGenerationModel
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False

class ImageGenerator:
    def __init__(self, project_id: Optional[str] = None, location: str = "us-central1"):
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.location = location
        self.model = None
        self.quota_exceeded = False  # Track quota state
        
        if VERTEX_AI_AVAILABLE and self.project_id:
            try:
                vertexai.init(project=self.project_id, location=self.location)
                self.model = ImageGenerationModel.from_pretrained("imagegeneration@006")
            except Exception as e:
                print(f"Warning: Failed to initialize Vertex AI: {e}")
        else:
            print("Warning: Vertex AI not available or Project ID not set. Using Mock mode.")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def _generate_with_retry(self, prompt: str, output_path: str):
        """Internal method with retry logic for API calls."""
        if self.quota_exceeded:
            # Skip retry if quota is exceeded
            raise Exception("Quota exceeded, using mock mode")
        
        images = self.model.generate_images(
            prompt=prompt,
            number_of_images=1,
            language="en",
            aspect_ratio="16:9",  # Default to full video aspect ratio
            safety_filter_level="block_some",
            person_generation="allow_adult",
        )
        if images:
            images[0].save(location=output_path, include_generation_parameters=False)
            return output_path
        return None

    def generate_image(self, prompt: str, output_path: str) -> Optional[str]:
        """
        Generates an image from a prompt and saves it to the output path.
        Returns the path to the saved image or None if failed.
        """
        if self.model and not self.quota_exceeded:
            try:
                print(f"Generating image for prompt: {prompt[:50]}...")
                return self._generate_with_retry(prompt, output_path)
            except Exception as e:
                error_str = str(e).lower()
                # Check for quota errors
                if 'quota' in error_str or 'resource exhausted' in error_str:
                    print(f"Quota exceeded for Vertex AI. Switching to mock mode permanently.")
                    self.quota_exceeded = True
                else:
                    print(f"Error generating image with Vertex AI: {e}")
                
                # Fallback to mock if generation fails
                return self._generate_mock_image(prompt, output_path)
        
        return self._generate_mock_image(prompt, output_path)

    def _generate_mock_image(self, prompt: str, output_path: str) -> str:
        """Generates a placeholder image for testing/dev without API costs."""
        print(f"Mock Generating image for: {prompt[:50]}...")
        # Create a simple colored placeholder using PIL if available, else just a text file
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (1920, 1080), color = (73, 109, 137))
            d = ImageDraw.Draw(img)
            d.text((10,10), "Mock Image", fill=(255,255,0))
            d.text((10,60), prompt[:100], fill=(255,255,255))
            img.save(output_path)
        except ImportError:
            # Fallback if PIL is not installed
            with open(output_path, 'w') as f:
                f.write(f"Mock Image for prompt: {prompt}")
        
        return output_path
