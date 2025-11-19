import os
from ai_novel_to_video.services.image_generator import ImageGenerator
from ai_novel_to_video.services.voice_generator import VoiceGenerator
from ai_novel_to_video.services.video_assembler import VideoAssembler

# Initialize services
image_gen = ImageGenerator()
voice_gen = VoiceGenerator()
video_assembler = VideoAssembler()

output_dir = "ai_novel_to_video/output"
os.makedirs(output_dir, exist_ok=True)

scenes = []
print("Generating assets for 3 scenes...")

for i in range(3):
    # Generate Image
    img_path = os.path.join(output_dir, f"scene_{i}_img.png")
    image_gen.generate_image(f"Scene {i} visual", img_path)
    
    # Generate Audio
    audio_path = os.path.join(output_dir, f"scene_{i}_audio.mp3")
    voice_gen.generate_voice(f"This is the narration for scene {i}.", audio_path)
    
    scenes.append({'image': img_path, 'audio': audio_path})

print("Assembling video...")
output_video = os.path.join(output_dir, "test_full_video.mp4")
result = video_assembler.assemble_video(scenes, output_video)

if result and os.path.exists(result):
    print(f"SUCCESS: Full video generated at {result}")
    with open(result, 'rb') as f:
        # Check if it's mock content or real binary (if moviepy worked)
        header = f.read(20)
        print(f"File header/content start: {header}")
else:
    print("FAILURE: Video generation failed")
