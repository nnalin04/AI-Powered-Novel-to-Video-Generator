import os
from ai_novel_to_video.services.voice_generator import VoiceGenerator

# Initialize generator (will use mock if no creds)
generator = VoiceGenerator()

output_dir = "ai_novel_to_video/output"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "test_voice.mp3")

print(f"Generating voice to: {output_path}")
result = generator.generate_voice("This is a test narration for the AI video generator.", output_path)

if result and os.path.exists(result):
    print(f"SUCCESS: Audio generated at {result}")
    with open(result, 'rb') as f:
        print(f"File size: {len(f.read())} bytes")
else:
    print("FAILURE: Audio generation failed")
