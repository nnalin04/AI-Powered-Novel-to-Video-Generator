from flask import Flask, render_template, request
import os
from ai_novel_to_video.services.input_processor import InputProcessor
from ai_novel_to_video.services.screenplay_generator import ScreenplayGenerator
from ai_novel_to_video.services.image_generator import ImageGenerator
from ai_novel_to_video.services.voice_generator import VoiceGenerator
from ai_novel_to_video.services.video_assembler import VideoAssembler
from ai_novel_to_video.services.subtitle_generator import SubtitleGenerator
from ai_novel_to_video.services.thumbnail_generator import ThumbnailGenerator
from ai_novel_to_video.services.youtube_uploader import YouTubeUploader
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize services
input_processor = InputProcessor()
image_generator = ImageGenerator() # Will auto-fallback to mock if no creds
voice_generator = VoiceGenerator() # Will auto-fallback to mock if no creds
video_assembler = VideoAssembler() # Will auto-fallback to mock if no moviepy
subtitle_generator = SubtitleGenerator()
thumbnail_generator = ThumbnailGenerator(image_generator)
youtube_uploader = YouTubeUploader() # Will auto-fallback to mock if no client_secrets.json

# ScreenplayGenerator requires API key, ensure it's handled gracefully if missing during dev
try:
    screenplay_generator = ScreenplayGenerator()
except ValueError as e:
    print(f"Warning: {e}")
    screenplay_generator = None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_type = request.form['input_type']
        video_type = request.form['video_type']
        
        text_content = ""
        
        try:
            if input_type == 'text':
                text_content = request.form['text_input']
            elif input_type == 'pdf':
                pdf_file = request.files['pdf_file']
                if pdf_file:
                    filepath = os.path.join('ai_novel_to_video/input', pdf_file.filename)
                    pdf_file.save(filepath)
                    print(f"Uploaded PDF: {pdf_file.filename}")
                    text_content = input_processor.extract_text_from_pdf(filepath)
            elif input_type == 'url':
                url_input = request.form['url_input']
                print(f"URL Input: {url_input}")
                text_content = input_processor.extract_text_from_url(url_input)
            
            if not text_content:
                return "Error: No text content could be extracted."

            print(f"Extracted Text Length: {len(text_content)}")
            
            segments = input_processor.segment_text(text_content)
            print(f"Segments: {len(segments)}")
            
            screenplays = []
            scenes = [] # Initialize scenes list here
            if screenplay_generator:
                for i, segment in enumerate(segments):
                    screenplay = screenplay_generator.paragraph_to_screenplay(segment)
                    screenplays.append(screenplay)
                    print(f"Generated Screenplay for segment {i+1}.")
                    
                    # Generate Image for the scene
                    # Extract a simple prompt from the segment for now (in real app, parse JSON)
                    # TODO: Parse the JSON output from Gemini to get the real scene description
                    image_prompt = f"Cinematic shot of: {segment[:100]}" 
                    output_image_path = os.path.join('ai_novel_to_video/output', f"scene_{i+1}.png")
                    
                    # Ensure output directory exists
                    os.makedirs('ai_novel_to_video/output', exist_ok=True)
                    
                    image_path = image_generator.generate_image(image_prompt, output_image_path)
                    print(f"Generated Image: {image_path}")
                    
                    # Generate Voiceover
                    # TODO: Parse JSON to get actual voiceover text
                    voice_text = f"Narrator: {segment[:200]}"
                    output_audio_path = os.path.join('ai_novel_to_video/output', f"voice_{i+1}.mp3")
                    
                    audio_path = voice_generator.generate_voice(voice_text, output_audio_path)
                    print(f"Generated Audio: {audio_path}")
                    
                    # Add text to scene for subtitles
                    scenes.append({'image': image_path, 'audio': audio_path, 'text': segment})
            
            # Generate Subtitles
            output_srt_path = os.path.join('ai_novel_to_video/output', 'subtitles.srt')
            subtitle_generator.generate_srt(scenes, output_srt_path)
            
            # Assemble Video
            output_video_path = os.path.join('ai_novel_to_video/output', 'final_video.mp4')
            final_video = video_assembler.assemble_video(scenes, output_video_path)
            
            if final_video:
                print(f"SUCCESS: Final video generated at {final_video}")
                
                # Generate Thumbnail
                thumbnail_prompt = f"Cinematic cover art for: {segments[0][:100]}"
                thumbnail_path = os.path.join('ai_novel_to_video/output', 'thumbnail.png')
                thumbnail_generator.generate_thumbnail("My AI Story", thumbnail_prompt, thumbnail_path)
                
                # Upload to YouTube
                print("Starting YouTube Upload...")
                video_title = f"AI Story: {segments[0][:30]}..."
                video_description = f"Generated from text:\n\n{segments[0][:200]}...\n\n#AI #Storytelling"
                video_tags = ["AI", "Story", "VideoGeneration"]
                
                youtube_uploader.upload_video(
                    final_video, 
                    video_title, 
                    video_description, 
                    video_tags, 
                    thumbnail_path
                )
                
            else:
                print("Error: Failed to generate final video.")
                
        except Exception as e:
            print(f"Error: {e}")
            else:
                return "Error: Screenplay Generator not initialized (Check API Key)."

            # TODO: Pass screenplays to the next stage (Image/Video Generation)
            
            return f"Processing Complete! Generated {len(screenplays)} screenplay segments. Check console for details."

        except Exception as e:
            print(f"Error processing request: {e}")
            return f"Error: {e}"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)