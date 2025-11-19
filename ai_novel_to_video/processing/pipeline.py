import os
from ai_novel_to_video.services.input_processor import InputProcessor
from ai_novel_to_video.services.screenplay_generator import ScreenplayGenerator
from ai_novel_to_video.services.image_generator import ImageGenerator
from ai_novel_to_video.services.voice_generator import VoiceGenerator
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
        self.video_assembler = VideoAssembler()
        self.subtitle_generator = SubtitleGenerator()
        self.thumbnail_generator = ThumbnailGenerator(self.image_generator)
        self.youtube_uploader = YouTubeUploader()
        
        try:
            self.screenplay_generator = ScreenplayGenerator()
        except ValueError as e:
            logger.warning(f"ScreenplayGenerator initialization warning: {e}")
            self.screenplay_generator = None

    def process_request(self, input_type, input_data, video_type):
        """
        Orchestrates the entire video generation process.
        """
        logger.info(f"Starting process_request. Input Type: {input_type}, Video Type: {video_type}")
        
        try:
            # 1. Input Processing
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

            for i, segment in enumerate(segments):
                logger.info(f"Processing segment {i+1}/{len(segments)}")
                
                # Generate Screenplay
                screenplay = self.screenplay_generator.paragraph_to_screenplay(segment)
                logger.info(f"Generated screenplay for segment {i+1}")
                
                # Check if fallback was used
                if screenplay.get('_fallback'):
                    logger.warning(f"Screenplay parsing fallback used for segment {i+1}: {screenplay.get('_error', 'Unknown error')}")
                
                # Image Generation - use parsed scene_description
                scene_desc = screenplay.get('scene_description', '')
                if scene_desc:
                    image_prompt = f"Cinematic shot: {scene_desc}"
                else:
                    # Fallback to raw text
                    image_prompt = f"Cinematic shot of: {segment[:100]}"
                    
                image_path = os.path.join(output_dir, f"scene_{i+1}.png")
                generated_image = self.image_generator.generate_image(image_prompt, image_path)
                logger.info(f"Generated image for segment {i+1}")
                
                # Voice Generation - use parsed voiceover_text
                voiceover_text = screenplay.get('voiceover_text', '')
                if voiceover_text:
                    voice_text = voiceover_text
                else:
                    # Fallback to raw segment
                    voice_text = segment[:500]
                
                audio_path = os.path.join(output_dir, f"voice_{i+1}.mp3")
                generated_audio = self.voice_generator.generate_voice(voice_text, audio_path)
                logger.info(f"Generated voice for segment {i+1}")
                
                # Store scene with screenplay data
                scenes.append({
                    'image': generated_image,
                    'audio': generated_audio,
                    'text': segment,
                    'screenplay': screenplay, # Keep screenplay for potential future use
                    'voiceover_text': voiceover_text if voiceover_text else segment
                })

            # 3. Subtitle Generation
            logger.info("Generating subtitles...")
            srt_path = os.path.join(output_dir, 'subtitles.srt')
            self.subtitle_generator.generate_srt(scenes, srt_path)

            # 4. Video Assembly
            logger.info("Assembling video...")
            video_path = os.path.join(output_dir, 'final_video.mp4')
            final_video = self.video_assembler.assemble_video(scenes, video_path)

            if not final_video:
                logger.error("Video assembly failed.")
                return "Error: Video assembly failed."

            # 5. Thumbnail Generation
            logger.info("Generating thumbnail...")
            thumb_prompt = f"Cinematic cover art for: {segments[0][:100]}"
            thumb_path = os.path.join(output_dir, 'thumbnail.png')
            self.thumbnail_generator.generate_thumbnail("My AI Story", thumb_prompt, thumb_path)

            # 6. YouTube Upload
            logger.info("Uploading to YouTube...")
            video_title = f"AI Story: {segments[0][:30]}..."
            video_desc = f"Generated from text:\n\n{segments[0][:200]}...\n\n#AI #Storytelling"
            video_tags = ["AI", "Story", "VideoGeneration"]
            
            self.youtube_uploader.upload_video(
                final_video, video_title, video_desc, video_tags, thumb_path
            )

            logger.info("Pipeline completed successfully.")
            return f"Success! Video generated at {final_video}"

        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            return f"Error processing request: {str(e)}"

    def _handle_input(self, input_type, input_data):
        if input_type == 'text':
            return input_data.get('text_input')
        elif input_type == 'pdf':
            pdf_file = input_data.get('pdf_file')
            if pdf_file:
                filepath = os.path.join('ai_novel_to_video/input', pdf_file.filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                pdf_file.save(filepath)
                return self.input_processor.extract_text_from_pdf(filepath)
        elif input_type == 'url':
            return self.input_processor.extract_text_from_url(input_data.get('url_input'))
        return None
