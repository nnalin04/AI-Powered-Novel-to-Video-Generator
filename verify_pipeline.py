from ai_novel_to_video.processing.pipeline import VideoGenerationPipeline
import os

from unittest.mock import MagicMock

# Initialize pipeline
pipeline = VideoGenerationPipeline()

# Mock ScreenplayGenerator for environment without API keys
mock_screenplay_gen = MagicMock()
mock_screenplay_gen.paragraph_to_screenplay.return_value = {
    "visual_prompt": "A test scene",
    "audio_prompt": "A test narration"
}
pipeline.screenplay_generator = mock_screenplay_gen

# Simulate Text Input
print("Testing Pipeline with Text Input...")
input_data = {'text_input': "This is a test story for the refactored pipeline. It should generate a video."}
result = pipeline.process_request('text', input_data, 'short')
print(f"Result: {result}")

if "Success" in result:
    print("VERIFICATION PASSED: Pipeline processed text input successfully.")
else:
    print("VERIFICATION FAILED: Pipeline failed to process text input.")
