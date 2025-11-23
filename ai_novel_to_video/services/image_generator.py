import os
import time
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
import logging

# Setup logger for retry attempts
logger = logging.getLogger(__name__)

# Try importing google.genai for image generation
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

class ImageGenerator:
    def __init__(self, project_id: Optional[str] = None, location: str = "us-central1"):
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.location = location or os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.client = None
        self.quota_exceeded = False  # Track quota state
        
        if GENAI_AVAILABLE:
            try:
                # Check if using Vertex AI mode
                use_vertexai = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true"
                
                if use_vertexai:
                    # Vertex AI mode (required for Imagen)
                    if not self.project_id:
                        print("Warning: GOOGLE_GENAI_USE_VERTEXAI is true but GOOGLE_CLOUD_PROJECT not set. Using Mock mode.")
                    else:
                        self.client = genai.Client(vertexai=True, project=self.project_id, location=self.location)
                        self.model_name = 'imagen-3.0-generate-002'
                        print(f"Initialized Imagen with Vertex AI (project: {self.project_id}, location: {self.location})")
                else:
                    # Developer API mode - check if Imagen is available
                    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
                    if api_key:
                        self.client = genai.Client(api_key=api_key)
                        self.model_name = 'imagen-3.0-generate-002'
                        print("Initialized Imagen with Developer API (Note: Imagen may not be available)")
                    else:
                        print("Warning: No API key or Vertex AI config found. Using Mock mode.")
            except Exception as e:
                print(f"Warning: Failed to initialize Google GenAI: {e}")
        else:
            print("Warning: Google GenAI SDK not available. Using Mock mode.")

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
        
        # Generate images using new SDK
        response = self.client.models.generate_images(
            model=self.model_name,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9",
                safety_filter_level="block_medium_and_above",
                person_generation="allow_adult",
                include_rai_reason=False,
                output_mime_type="image/jpeg"
            )
        )
        
        if response.generated_images:
            # Save the generated image
            image = response.generated_images[0].image
            image.save(output_path)
            return output_path
        return None

    def generate_image(self, prompt: str, output_path: str) -> Optional[str]:
        """
        Generates an image from a prompt and saves it to the output path.
        Returns the path to the saved image or None if failed.
        """
        if self.client and not self.quota_exceeded:
            try:
                print(f"Generating image for prompt: {prompt[:50]}...")
                return self._generate_with_retry(prompt, output_path)
            except Exception as e:
                error_str = str(e).lower()
                # Check for quota errors
                if 'quota' in error_str or 'resource exhausted' in error_str:
                    print(f"Quota exceeded for Imagen. Switching to mock mode permanently.")
                    self.quota_exceeded = True
                else:
                    print(f"Error generating image with Imagen: {e}")
                
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
