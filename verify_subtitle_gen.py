import os
from ai_novel_to_video.services.subtitle_generator import SubtitleGenerator

# Initialize generator
generator = SubtitleGenerator()

output_dir = "ai_novel_to_video/output"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "test_subtitles.srt")

# Create dummy audio file for duration check (if moviepy available)
dummy_audio = os.path.join(output_dir, "dummy_audio.mp3")
with open(dummy_audio, 'w') as f:
    f.write("dummy content")

scenes = [
    {'text': "This is the first scene text.", 'audio': dummy_audio},
    {'text': "Here is the second scene.", 'audio': dummy_audio},
    {'text': "And finally, the conclusion.", 'audio': dummy_audio}
]

print(f"Generating subtitles to: {output_path}")
result = generator.generate_srt(scenes, output_path)

if result and os.path.exists(result):
    print(f"SUCCESS: Subtitles generated at {result}")
    with open(result, 'r') as f:
        print("--- File Content ---")
        print(f.read())
        print("--------------------")
else:
    print("FAILURE: Subtitle generation failed")
