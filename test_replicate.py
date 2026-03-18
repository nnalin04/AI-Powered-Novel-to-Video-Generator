import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from ai_film_studio.providers.factory import ProviderFactory
from ai_film_studio.config.settings import settings

async def main():
    print("--- Replicate Integration Test ---")
    if not settings.REPLICATE_API_TOKEN:
        print("❌ Error: REPLICATE_API_TOKEN not found in environment.")
        print("Please add 'REPLICATE_API_TOKEN=your_token_here' to the .env file.")
        return

    print("✅ REPLICATE_API_TOKEN found.")
    
    # 1. Test Image Gen
    print("\n--- 1. Testing Image Generation (FLUX.2 Pro) ---")
    image_gen = ProviderFactory.get_image_gen()
    test_image_prompt = "A futuristic cinematic still of a robot drinking coffee, cyberpunk aesthetic, high quality"
    
    print(f"Generating image with prompt: {test_image_prompt}")
    image_path = await image_gen.generate_image(test_image_prompt)
    if os.path.exists(image_path) and "placeholders" not in image_path:
        print(f"✅ Image generated and saved to: {image_path}")
    else:
        print(f"❌ Image generation failed or returned placeholder: {image_path}")
        return # Stop if image fails
        
    # 2. Test Video Gen
    print("\n--- 2. Testing Video Generation (MiniMax Hailuo-02) ---")
    video_gen = ProviderFactory.get_video_gen()
    test_video_prompt = "The robot slowly raises the coffee cup to its face, cinematic lighting, 4k"
    
    print(f"Generating video with prompt: {test_video_prompt} and starting image: {image_path}")
    video_path = await video_gen.generate_clip(test_video_prompt, image_url=image_path)
    
    if os.path.exists(video_path) and "placeholders" not in video_path:
        print(f"✅ Video generated and saved to: {video_path}")
    else:
        print(f"❌ Video generation failed or returned placeholder: {video_path}")

if __name__ == "__main__":
    asyncio.run(main())
