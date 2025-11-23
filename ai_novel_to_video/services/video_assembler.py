import os
from typing import List, Dict, Optional
from ai_novel_to_video.services.animation_service import AnimationService

try:
    # Try moviepy 2.0+ imports
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, VideoFileClip
    from moviepy.video.fx import Loop
    MOVIEPY_AVAILABLE = True
    MOVIEPY_V2 = True
except ImportError:
    try:
        # Fallback for older versions
        from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, VideoFileClip
        MOVIEPY_AVAILABLE = True
        MOVIEPY_V2 = False
    except ImportError:
        MOVIEPY_AVAILABLE = False
        MOVIEPY_V2 = False

class VideoAssembler:
    def __init__(self):
        self.animation_service = AnimationService()
        if not MOVIEPY_AVAILABLE:
            print("Warning: MoviePy not installed. Video assembly will be mocked.")

    def assemble_video(self, scenes: List[Dict[str, str]], output_path: str, fps: int = 24) -> Optional[str]:
        """
        Assembles a video from a list of scenes.
        Each scene is a dict: {'image': path_to_image, 'video_clip': path_to_veo_video (optional), 'audio': path_to_audio}
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
                    video_clip_path = scene.get('video_clip')  # NEW: Veo-generated video
                    audio_path = scene.get('audio')
                    
                    if not audio_path or not os.path.exists(audio_path):
                        print(f"Warning: Missing audio for scene {i}. Skipping.")
                        continue

                    # Create Audio Clip
                    audio_clip = AudioFileClip(audio_path)
                    duration = audio_clip.duration
                    
                    # Create Video Clip
                    video_clip = None
                    
                    # Option 1: Use Veo-generated video if available
                    if video_clip_path and os.path.exists(video_clip_path):
                        try:
                            print(f"Using Veo video for scene {i+1}")
                            video_clip = VideoFileClip(video_clip_path)
                            # Adjust duration to match audio
                            if video_clip.duration < duration:
                                # Loop the video if it's shorter than audio
                                if MOVIEPY_V2:
                                    video_clip = video_clip.with_effects([Loop(duration=duration)])
                                else:
                                    video_clip = video_clip.loop(duration=duration)
                            else:
                                # Trim if longer
                                video_clip = video_clip.subclip(0, duration)
                        except Exception as e:
                            print(f"Warning: Failed to load Veo video for scene {i}: {e}")
                            video_clip = None
                    
                    # Option 2: Use animated image with Ken Burns effect
                    if not video_clip:
                        if not image_path or not os.path.exists(image_path):
                            print(f"Warning: Missing image for scene {i}. Skipping.")
                            continue
                        
                        print(f"Using animated image for scene {i+1}")
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
