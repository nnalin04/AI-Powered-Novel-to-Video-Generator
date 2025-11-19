import os
import datetime
from typing import List, Dict, Optional

try:
    # Try moviepy 2.0+ imports
    from moviepy import AudioFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    try:
        # Fallback for older versions
        from moviepy.editor import AudioFileClip
        MOVIEPY_AVAILABLE = True
    except ImportError:
        MOVIEPY_AVAILABLE = False

class SubtitleGenerator:
    def __init__(self):
        if not MOVIEPY_AVAILABLE:
            print("Warning: MoviePy not installed. Subtitle timing will be estimated.")

    def generate_srt(self, scenes: List[Dict[str, str]], output_path: str) -> Optional[str]:
        """
        Generates an SRT subtitle file from a list of scenes.
        Each scene is a dict: {'text': str, 'audio': path_to_audio}
        """
        if not scenes:
            print("Error: No scenes provided for subtitle generation.")
            return None

        print(f"Generating subtitles for {len(scenes)} scenes...")
        
        srt_content = ""
        current_time = 0.0

        for i, scene in enumerate(scenes):
            text = scene.get('text', '').strip()
            audio_path = scene.get('audio')
            
            duration = 5.0 # Default duration if audio missing or moviepy fails
            
            if audio_path and os.path.exists(audio_path) and MOVIEPY_AVAILABLE:
                try:
                    with AudioFileClip(audio_path) as audio_clip:
                        duration = audio_clip.duration
                except Exception as e:
                    print(f"Warning: Could not get duration for {audio_path}: {e}")
            
            start_time = current_time
            end_time = current_time + duration
            current_time = end_time
            
            # Format timestamps: HH:MM:SS,mmm
            start_str = self._format_time(start_time)
            end_str = self._format_time(end_time)
            
            # SRT Entry
            srt_content += f"{i+1}\n"
            srt_content += f"{start_str} --> {end_str}\n"
            srt_content += f"{text}\n\n"

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            print(f"Subtitles saved to {output_path}")
            return output_path
        except Exception as e:
            print(f"Error saving subtitle file: {e}")
            return None

    def _format_time(self, seconds: float) -> str:
        """Formats seconds into SRT timestamp format: HH:MM:SS,mmm"""
        td = datetime.timedelta(seconds=seconds)
        # Total seconds to hours, minutes, seconds, milliseconds
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        millis = int(td.microseconds / 1000)
        
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"
