import asyncio
import os
import subprocess
from typing import Dict, Any
from ai_film_studio.core.state import EpisodeState
from ai_film_studio.providers.factory import ProviderFactory

async def generate_ken_burns_video(image_path: str, output_path: str, duration: float = 4.0):
    """Creates a video from a static image with a zoom-in effect using ffmpeg."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # ffmpeg command for a simple zoom-in effect
    # scale=8000:-1: zooming onto a high-res virtual canvas
    # zoompan: the actual effect. d=duration*fps
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", image_path,
        "-vf", f"zoompan=z='min(zoom+0.0015,1.5)':d={int(duration * 25)}:s=1280x720:fps=25",
        "-t", str(duration),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_path
    ]
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        print(f"FFmpeg Error: {stderr.decode()}")
        return None
    return output_path

async def animator_node(state: EpisodeState) -> Dict[str, Any]:
    print("--- ANIMATION AGENT STARTED ---", flush=True)
    
    video_gen = ProviderFactory.get_video_gen()
    
    tasks = []
    for scene in state.scenes:
        # Extract storyboard path from visual_description [Ref: path]
        storyboard_path = None
        if "[Ref: " in scene.visual_description:
            try:
                storyboard_path = scene.visual_description.split("[Ref: ")[1].split("]")[0]
            except:
                pass
        
        async def animate_scene(s=scene, img=storyboard_path):
            prompt = f"Animate this scene: {s.visual_description}"
            # Attempt real video generation if possible (placeholder for now)
            video_path = await video_gen.generate_clip(prompt=prompt, image_url=img)
            
            # Check if we got a mock placeholder or if it doesn't exist
            if "placeholders" in video_path or not os.path.exists(video_path):
                if img and os.path.exists(img):
                    print(f"Animator: Falling back to ffmpeg for Scene {s.id}", flush=True)
                    gen_path = f"assets/generated_videos/scene_{s.id}.mp4"
                    success_path = await generate_ken_burns_video(img, gen_path, duration=s.estimated_duration)
                    if success_path:
                        video_path = success_path
                else:
                    print(f"Animator Warning: No storyboard image for Scene {s.id}, using mock path", flush=True)
            
            s.video_clip_path = video_path
            s.status = "done"
            return s
        
        tasks.append(animate_scene())
    
    updated_scenes = await asyncio.gather(*tasks)
    
    return {
        "scenes": updated_scenes
    }
