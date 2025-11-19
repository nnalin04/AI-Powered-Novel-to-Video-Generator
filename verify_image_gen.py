import os
from ai_novel_to_video.services.image_generator import ImageGenerator

# Initialize generator (will use mock if no creds)
generator = ImageGenerator()

output_dir = "ai_novel_to_video/output"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "test_gen_image.png")

print(f"Generating image to: {output_path}")
result = generator.generate_image("A futuristic city with flying cars", output_path)

if result and os.path.exists(result):
    print(f"SUCCESS: Image generated at {result}")
else:
    print("FAILURE: Image generation failed")
