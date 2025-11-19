import os
from ai_novel_to_video.services.image_generator import ImageGenerator
from ai_novel_to_video.services.thumbnail_generator import ThumbnailGenerator

# Initialize services
image_gen = ImageGenerator()
thumbnail_gen = ThumbnailGenerator(image_gen)

output_dir = "ai_novel_to_video/output"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "test_thumbnail.png")

print(f"Generating thumbnail to: {output_path}")
result = thumbnail_gen.generate_thumbnail("The Galactic Adventure", "A futuristic spaceship flying near a nebula", output_path)

if result and os.path.exists(result):
    print(f"SUCCESS: Thumbnail generated at {result}")
else:
    print("FAILURE: Thumbnail generation failed")
