import os
from ai_novel_to_video.services.youtube_uploader import YouTubeUploader

# Initialize uploader (will default to mock if no secrets)
uploader = YouTubeUploader()

output_dir = "ai_novel_to_video/output"
os.makedirs(output_dir, exist_ok=True)

# Create dummy assets
video_path = os.path.join(output_dir, "test_video.mp4")
with open(video_path, 'w') as f: f.write("dummy video")

thumb_path = os.path.join(output_dir, "test_thumb.png")
with open(thumb_path, 'w') as f: f.write("dummy thumb")

print(f"Attempting upload of {video_path}...")
video_id = uploader.upload_video(
    video_path, 
    "Test Video Title", 
    "Test Description", 
    ["test", "ai"], 
    thumb_path
)

if video_id:
    print(f"SUCCESS: Upload completed. Video ID: {video_id}")
else:
    print("FAILURE: Upload failed")
