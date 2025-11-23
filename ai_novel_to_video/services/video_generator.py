import os
import time
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
import logging

# Setup logger for retry attempts
logger = logging.getLogger(__name__)

# Try importing google.genai for video generation
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

class VideoGenerator:
    def __init__(self, project_id: Optional[str] = None, location: str = "us-central1"):
        """
        Initialize Video Generator with Veo model.
        Note: Veo is only available through Vertex AI.
        """
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.location = location or os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.client = None
        self.quota_exceeded = False  # Track quota state
        
        if GENAI_AVAILABLE and self.project_id:
            try:
                # Veo requires Vertex AI
                self.client = genai.Client(vertexai=True, project=self.project_id, location=self.location)
                self.model_name = 'veo-2.0-generate-001'
                print(f"Initialized Veo with Vertex AI (project: {self.project_id}, location: {self.location})")
            except Exception as e:
                print(f"Warning: Failed to initialize Veo: {e}")
                print("Falling back to mock mode.")
        else:
            if not GENAI_AVAILABLE:
                print("Warning: Google GenAI SDK not available. Using Mock mode.")
            else:
                print("Warning: Project ID not set. Veo requires Vertex AI. Using Mock mode.")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=20),
        retry=retry_if_exception_type((Exception,)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def _generate_with_retry(self, prompt: str, output_path: str, duration_seconds: int = 5, 
                            image_path: Optional[str] = None):
        """Internal method with retry logic for API calls."""
        if self.quota_exceeded:
            raise Exception("Quota exceeded, using mock mode")
        
        # Prepare generation config
        config = types.GenerateVideosConfig(
            number_of_videos=1,
            duration_seconds=duration_seconds,
            enhance_prompt=True,
        )
        
        # Generate video
        if image_path:
            # Image-to-video generation
            image = types.Image.from_file(location=image_path)
            operation = self.client.models.generate_videos(
                model=self.model_name,
                prompt=prompt,
                image=image,
                config=config
            )
        else:
            # Text-to-video generation
            operation = self.client.models.generate_videos(
                model=self.model_name,
                prompt=prompt,
                config=config
            )
        
        # Poll operation until complete
        print(f"Video generation started. Polling for completion...")
        max_wait_time = 300  # 5 minutes max
        start_time = time.time()
        
        while not operation.done:
            if time.time() - start_time > max_wait_time:
                raise Exception("Video generation timed out after 5 minutes")
            
            time.sleep(20)  # Wait 20 seconds between polls
            operation = self.client.operations.get(operation)
            print(f"Still generating... ({int(time.time() - start_time)}s elapsed)")
        
        # Get the generated video
        if operation.response and operation.response.generated_videos:
            video = operation.response.generated_videos[0].video
            # Save video to output path
            try:
                # Try using save method if available
                video.save(output_path)
            except AttributeError:
                # Fallback: try to access video data directly
                try:
                    with open(output_path, 'wb') as f:
                        # The video object might have different attributes
                        if hasattr(video, 'data'):
                            f.write(video.data)
                        elif hasattr(video, 'content'):
                            f.write(video.content)
                        else:
                            raise AttributeError(f"Video object has no known data attribute. Available: {dir(video)}")
                except Exception as e:
                    print(f"Error saving video: {e}")
                    return None
            
            print(f"Video saved to {output_path}")
            return output_path
        
        return None

    def generate_video(self, prompt: str, output_path: str, duration_seconds: int = 5) -> Optional[str]:
        """
        Generates a video from a text prompt using Veo.
        
        Args:
            prompt: Text description of the video to generate
            output_path: Path to save the generated video (MP4)
            duration_seconds: Duration of video (5-10 seconds supported)
        
        Returns:
            Path to the saved video or None if failed
        """
        if self.client and not self.quota_exceeded:
            try:
                print(f"Generating video for prompt: {prompt[:50]}...")
                return self._generate_with_retry(prompt, output_path, duration_seconds)
            except Exception as e:
                error_str = str(e).lower()
                # Check for quota errors
                if 'quota' in error_str or 'resource exhausted' in error_str:
                    print(f"Quota exceeded for Veo. Switching to mock mode permanently.")
                    self.quota_exceeded = True
                else:
                    print(f"Error generating video with Veo: {e}")
                
                # Fallback to mock if generation fails
                return self._generate_mock_video(prompt, output_path, duration_seconds)
        
        return self._generate_mock_video(prompt, output_path, duration_seconds)

    def generate_video_from_image(self, prompt: str, image_path: str, output_path: str, 
                                  duration_seconds: int = 5) -> Optional[str]:
        """
        Generates a video from an image using Veo (image-to-video).
        
        Args:
            prompt: Text description to guide the animation
            image_path: Path to the input image
            output_path: Path to save the generated video (MP4)
            duration_seconds: Duration of video (5-10 seconds supported)
        
        Returns:
            Path to the saved video or None if failed
        """
        if self.client and not self.quota_exceeded:
            try:
                print(f"Generating video from image: {image_path}")
                return self._generate_with_retry(prompt, output_path, duration_seconds, image_path)
            except Exception as e:
                error_str = str(e).lower()
                # Check for quota errors
                if 'quota' in error_str or 'resource exhausted' in error_str:
                    print(f"Quota exceeded for Veo. Switching to mock mode permanently.")
                    self.quota_exceeded = True
                else:
                    print(f"Error generating video from image with Veo: {e}")
                
                # Fallback to mock if generation fails
                return self._generate_mock_video(prompt, output_path, duration_seconds)
        
        return self._generate_mock_video(prompt, output_path, duration_seconds)

    def _generate_mock_video(self, prompt: str, output_path: str, duration_seconds: int = 5) -> str:
        """Generates a placeholder video for testing/dev without API costs."""
        print(f"Mock Generating video for: {prompt[:50]}...")
        
        try:
            from moviepy import ColorClip, TextClip, CompositeVideoClip
            
            # Create a simple colored background
            bg_clip = ColorClip(size=(1920, 1080), color=(73, 109, 137), duration=duration_seconds)
            
            # Add text overlay
            try:
                txt_clip = TextClip(
                    text=f"Mock Video\n{prompt[:100]}",
                    font_size=50,
                    color='white',
                    size=(1800, 900),
                    method='caption'
                ).with_duration(duration_seconds).with_position('center')
                
                video = CompositeVideoClip([bg_clip, txt_clip])
            except Exception as text_error:
                # If TextClip fails, just use the color clip
                print(f"Warning: Could not add text to mock video: {text_error}")
                video = bg_clip
            
            # Write video file
            video.write_videofile(output_path, fps=24, codec='libx264', audio=False, logger=None)
            
        except Exception as e:
            print(f"Error generating mock video with MoviePy: {e}")
            # Create a minimal placeholder file
            with open(output_path, 'w') as f:
                f.write(f"Mock Video for prompt: {prompt}")
        
        return output_path
