import os
from ai_novel_to_video.services.input_processor import InputProcessor
from ai_novel_to_video.services.screenplay_generator import ScreenplayGenerator
from ai_novel_to_video.services.image_generator import ImageGenerator
from ai_novel_to_video.services.voice_generator import VoiceGenerator
from ai_novel_to_video.services.video_generator import VideoGenerator
from ai_novel_to_video.services.video_assembler import VideoAssembler
from ai_novel_to_video.services.subtitle_generator import SubtitleGenerator
from ai_novel_to_video.services.thumbnail_generator import ThumbnailGenerator
from ai_novel_to_video.services.youtube_uploader import YouTubeUploader
from ai_novel_to_video.utils.logger import setup_logger

logger = setup_logger('pipeline', 'ai_novel_to_video/logs/pipeline.log')

class VideoGenerationPipeline:
    def __init__(self):
        logger.info("Initializing VideoGenerationPipeline services...")
        self.input_processor = InputProcessor()
        self.image_generator = ImageGenerator()
        self.voice_generator = VoiceGenerator()
        self.video_generator = VideoGenerator()  # NEW: Veo video generation
        self.video_assembler = VideoAssembler()
        self.subtitle_generator = SubtitleGenerator()
        self.thumbnail_generator = ThumbnailGenerator(self.image_generator)
        self.youtube_uploader = YouTubeUploader()
        
        try:
            self.screenplay_generator = ScreenplayGenerator()
        except ValueError as e:
            logger.warning(f"ScreenplayGenerator initialization warning: {e}")
            self.screenplay_generator = None
        
        # Check if we should use Veo for video generation
        self.use_veo = os.environ.get("USE_VEO_VIDEO", "false").lower() == "true"
        if self.use_veo and self.video_generator.client:
            logger.info("Veo video generation enabled")
        else:
            logger.info("Using image-based video assembly (Veo disabled or unavailable)")

    def process_request(self, input_type, input_data, video_type, progress_callback=None):
        """
        Orchestrates the entire video generation process.
        """
        logger.info(f"Starting process_request. Input Type: {input_type}, Video Type: {video_type}")
        
        def report_progress(message, step, total_steps):
            if progress_callback:
                percent = int((step / total_steps) * 100)
                progress_callback(message, percent)
        
        try:
            total_steps = 100 # Abstract total steps
            current_step = 0
            
            # 1. Input Processing
            report_progress("Processing input...", 5, total_steps)
            text_content = self._handle_input(input_type, input_data)
            if not text_content:
                return "Error: No text content extracted."

            logger.info(f"Extracted Text Length: {len(text_content)}")
            segments = self.input_processor.segment_text(text_content)
            logger.info(f"Text segmented into {len(segments)} parts.")

            if not self.screenplay_generator:
                return "Error: Screenplay Generator not initialized."

            # 2. Asset Generation Loop
            scenes = []
            output_dir = 'ai_novel_to_video/output'
            os.makedirs(output_dir, exist_ok=True)

            # Calculate steps for loop (allocating 60% of progress to this loop)
            loop_progress_start = 10
            loop_progress_end = 70
            progress_per_segment = (loop_progress_end - loop_progress_start) / len(segments)

            for i, segment in enumerate(segments):
                current_loop_progress = loop_progress_start + (i * progress_per_segment)
                report_progress(f"Processing segment {i+1}/{len(segments)}: Generating Screenplay...", current_loop_progress, total_steps)
                
                logger.info(f"Processing segment {i+1}/{len(segments)}")
                
                # Generate Screenplay
                screenplay = self.screenplay_generator.paragraph_to_screenplay(segment)
                logger.info(f"Generated screenplay for segment {i+1}")
                
                # Check if fallback was used
                if screenplay.get('_fallback'):
                    logger.warning(f"Screenplay parsing fallback used for segment {i+1}: {screenplay.get('_error', 'Unknown error')}")
                
                # Image Generation - use parsed scene_description
                report_progress(f"Processing segment {i+1}/{len(segments)}: Generating Image...", current_loop_progress + (progress_per_segment * 0.3), total_steps)
                scene_desc = screenplay.get('scene_description', '')
                if scene_desc:
                    image_prompt = f"Cinematic shot: {scene_desc}"
                else:
                    # Fallback to raw text
                    image_prompt = f"Cinematic shot of: {segment[:100]}"
                    
                image_path = os.path.join(output_dir, f"scene_{i+1}.png")
                generated_image = self.image_generator.generate_image(image_prompt, image_path)
                logger.info(f"Generated image for segment {i+1}")
                
                # Optional: Generate video from image using Veo (if enabled)
                video_clip_path = None
                if self.use_veo and self.video_generator.client:
                    report_progress(f"Processing segment {i+1}/{len(segments)}: Generating Video with Veo...", current_loop_progress + (progress_per_segment * 0.45), total_steps)
                    video_clip_path = os.path.join(output_dir, f"scene_{i+1}_veo.mp4")
                    
                    # Create animation prompt from scene description
                    veo_prompt = f"Animate this scene: {scene_desc[:200]}" if scene_desc else f"Animate: {segment[:100]}"
                    
                    try:
                        generated_video = self.video_generator.generate_video_from_image(
                            prompt=veo_prompt,
                            image_path=generated_image,
                            output_path=video_clip_path,
                            duration_seconds=5
                        )
                        if generated_video:
                            logger.info(f"Generated Veo video for segment {i+1}")
                        else:
                            logger.warning(f"Veo video generation failed for segment {i+1}, will use static image")
                            video_clip_path = None
                    except Exception as e:
                        logger.error(f"Error generating Veo video for segment {i+1}: {e}")
                        video_clip_path = None
                
                # Voice Generation
                report_progress(f"Processing segment {i+1}/{len(segments)}: Generating Voice...", current_loop_progress + (progress_per_segment * 0.6), total_steps)
                
                audio_path = os.path.join(output_dir, f"voice_{i+1}.mp3")
                audio_script = screenplay.get('audio_script')
                full_spoken_text = ""

                if audio_script and isinstance(audio_script, list) and len(audio_script) > 0:
                    logger.info(f"Generating multi-voice conversation for segment {i+1}")
                    generated_audio = self.voice_generator.generate_conversation(audio_script, audio_path)
                    # Construct full text for subtitles
                    full_spoken_text = " ".join([seg.get('text', '') for seg in audio_script])
                else:
                    # Fallback to single voice
                    voiceover_text = screenplay.get('voiceover_text', '')
                    if not voiceover_text:
                        voiceover_text = segment[:500]
                    
                    full_spoken_text = voiceover_text
                    logger.info(f"Generating single voice for segment {i+1}")
                    generated_audio = self.voice_generator.generate_voice(voiceover_text, audio_path)
                
                logger.info(f"Generated voice for segment {i+1}")
                
                # Store scene with screenplay data
                scenes.append({
                    'image': generated_image,
                    'video_clip': video_clip_path,  # NEW: Veo-generated video clip (if available)
                    'audio': generated_audio,
                    'text': full_spoken_text, # Use spoken text for subtitles
                    'screenplay': screenplay, 
                    'voiceover_text': full_spoken_text,
                    'raw_segment': segment
                })

            # 3. Subtitle Generation
            report_progress("Generating subtitles...", 75, total_steps)
            logger.info("Generating subtitles...")
            srt_path = os.path.join(output_dir, 'subtitles.srt')
            self.subtitle_generator.generate_srt(scenes, srt_path)

            # 4. Video Assembly
            report_progress("Assembling video (this may take a while)...", 80, total_steps)
            logger.info("Assembling video...")
            video_path = os.path.join(output_dir, 'final_video.mp4')
            final_video = self.video_assembler.assemble_video(scenes, video_path)

            if not final_video:
                logger.error("Video assembly failed.")
                return "Error: Video assembly failed."

            # 5. Thumbnail Generation
            report_progress("Generating thumbnail...", 90, total_steps)
            logger.info("Generating thumbnail...")
            thumb_prompt = f"Cinematic cover art for: {segments[0][:100]}"
            thumb_path = os.path.join(output_dir, 'thumbnail.png')
            self.thumbnail_generator.generate_thumbnail("My AI Story", thumb_prompt, thumb_path)

            # 6. YouTube Upload
            report_progress("Uploading to YouTube...", 95, total_steps)
            logger.info("Uploading to YouTube...")
            video_title = f"AI Story: {segments[0][:30]}..."
            video_desc = f"Generated from text:\n\n{segments[0][:200]}...\n\n#AI #Storytelling"
            video_tags = ["AI", "Story", "VideoGeneration"]
            
            self.youtube_uploader.upload_video(
                final_video, video_title, video_desc, video_tags, thumb_path
            )

            report_progress("Done!", 100, total_steps)
            logger.info("Pipeline completed successfully.")
            return f"Success! Video generated at {final_video}"

        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            return f"Error processing request: {str(e)}"

    def _handle_input(self, input_type, input_data):
        if input_type == 'text':
            return input_data.get('text_input')
        elif input_type == 'pdf':
            if 'pdf_path' in input_data:
                return self.input_processor.extract_text_from_pdf(input_data['pdf_path'])
            
            pdf_file = input_data.get('pdf_file')
            if pdf_file:
                filepath = os.path.join('ai_novel_to_video/input', pdf_file.filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                pdf_file.save(filepath)
                return self.input_processor.extract_text_from_pdf(filepath)
        elif input_type == 'url':
            return self.input_processor.extract_text_from_url(input_data.get('url_input'))
        return None
