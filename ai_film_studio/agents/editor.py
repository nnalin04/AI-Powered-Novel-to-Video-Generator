import asyncio
import os
from typing import Dict, Any
from ai_film_studio.core.state import EpisodeState

async def editor_node(state: EpisodeState) -> Dict[str, Any]:
    print("--- EDITOR AGENT STARTED ---", flush=True)
    
    os.makedirs("assets/output", exist_ok=True)
    os.makedirs("assets/temp", exist_ok=True)
    
    scene_clips = []
    
    # 1. Process each scene: Overlay audio on video
    for i, scene in enumerate(state.scenes):
        if not scene.video_clip_path or not os.path.exists(scene.video_clip_path):
            print(f"Editor Warning: Missing video for Scene {scene.id}", flush=True)
            continue
            
        scene_output = f"assets/temp/scene_{scene.id}_combined.mp4"
        
        # Command to overlay audio onto video.
        # Normalize to 44100Hz Stereo to ensure consistency for concatenation.
        if scene.audio_track_path and os.path.exists(scene.audio_track_path):
            print(f"Editor: Combining Audio + Video (Normalized) for Scene {scene.id}", flush=True)
            cmd = [
                "ffmpeg", "-y",
                "-i", scene.video_clip_path,
                "-i", scene.audio_track_path,
                "-map", "0:v", "-map", "1:a",
                "-c:v", "copy",
                "-c:a", "aac",
                "-ar", "44100",
                "-ac", "2",
                "-shortest",
                scene_output
            ]
        else:
            print(f"Editor: Adding silent normalized audio track to Scene {scene.id}", flush=True)
            cmd = [
                "ffmpeg", "-y", 
                "-i", scene.video_clip_path,
                "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                scene_output
            ]
            
        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await process.communicate()
        
        if process.returncode == 0:
            scene_clips.append(scene_output)

    # 2. Concatenate all scene clips
    output_path = f"assets/output/episode_{state.episode_number}_final.mp4"
    if not scene_clips:
        print("Editor Error: No scene clips to concatenate.", flush=True)
        return {"errors": ["No scene clips generated"]}

    # Create a concat list file for ffmpeg
    list_path = "assets/temp/concat_list.txt"
    with open(list_path, "w") as f:
        for clip in scene_clips:
            # ffmpeg concat demuxer requires absolute paths or paths relative to the list file
            f.write(f"file '{os.path.abspath(clip)}'\n")
            
    print(f"Editor: Concatenating {len(scene_clips)} clips...", flush=True)
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_path,
        "-c", "copy",
        output_path
    ]
    
    process = await asyncio.create_subprocess_exec(*concat_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        print(f"Editor FFmpeg Concat Error: {stderr.decode()}", flush=True)
        return {"errors": [stderr.decode()]}
        
    print(f"Editor: Final video created at {output_path}", flush=True)
    return {"final_video_path": output_path}
