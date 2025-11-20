import os
from typing import List, Dict, Optional
from ai_novel_to_video.services.animation_service import AnimationService

try:
    # Try moviepy 2.0+ imports
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
    MOVIEPY_AVAILABLE = True
except ImportError:
    try:
        # Fallback for older versions
        from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
        MOVIEPY_AVAILABLE = True
    except ImportError:
        MOVIEPY_AVAILABLE = False

class VideoAssembler:
    def __init__(self):
        self.animation_service = AnimationService()
        if not MOVIEPY_AVAILABLE:
            print("Warning: MoviePy not installed. Video assembly will be mocked.")

    def assemble_video(self, scenes: List[Dict[str, str]], output_path: str, fps: int = 24) -> Optional[str]:
        """
        Assembles a video from a list of scenes.
        Each scene is a dict: {'image': path_to_image, 'audio': path_to_audio}
        """
        if not scenes:
            print("Error: No scenes provided for video assembly.")
            return None

        if MOVIEPY_AVAILABLE:
            try:
                clips = []
                print(f"Assembling video from {len(scenes)} scenes...")
                
                for i, scene in enumerate(scenes):
                    image_path = scene.get('image')
                    audio_path = scene.get('audio')
                    
                    if not image_path or not os.path.exists(image_path):
                        print(f"Warning: Missing image for scene {i}. Skipping.")
                        continue
                    if not audio_path or not os.path.exists(audio_path):
                        print(f"Warning: Missing audio for scene {i}. Skipping.")
                        continue

                    # Create Audio Clip
                    audio_clip = AudioFileClip(audio_path)
                    duration = audio_clip.duration
                    
                    # Create Video Clip (with Animation)
                    # Try to apply Ken Burns effect
                    video_clip = self.animation_service.apply_ken_burns(image_path, duration)
                    
                    if not video_clip:
                        # Fallback to static image if animation fails or returns None
                        video_clip = ImageClip(image_path).with_duration(duration)
                    
                    # Set audio
                    video_clip = video_clip.with_audio(audio_clip)
                    
                    clips.append(video_clip)

                if not clips:
                    print("Error: No valid clips created.")
                    return None

                # Concatenate all clips
                final_video = concatenate_videoclips(clips, method="compose")
                
                # Write output file
                print(f"Writing video to {output_path}...")
                final_video.write_videofile(output_path, fps=fps, codec='libx264', audio_codec='aac')
                
                # Close clips to release resources
                for clip in clips:
                    clip.close()
                final_video.close()
                
                return output_path

            except Exception as e:
                print(f"Error assembling video with MoviePy: {e}")
                import traceback
                traceback.print_exc()
                return self._mock_assemble_video(scenes, output_path)
        
        return self._mock_assemble_video(scenes, output_path)

    def _mock_assemble_video(self, scenes: List[Dict[str, str]], output_path: str) -> str:
        """Creates a dummy video file for testing."""
        print(f"Mock assembling video with {len(scenes)} scenes...")
        with open(output_path, 'w') as f:
            f.write(f"Mock Video File. Contains {len(scenes)} scenes.\n")
            for i, scene in enumerate(scenes):
                f.write(f"Scene {i}: Image={scene.get('image')}, Audio={scene.get('audio')}\n")
        return output_path
