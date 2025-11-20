# AI-Powered Novel-to-Video Generator

Transform novels and stories into engaging videos with AI-powered narration, visuals, and subtitles. Generate both YouTube Shorts (9:16) and full-length videos (16:9) with automated upload capabilities.

## 🎬 Features

- **Multiple Input Methods**: Text, PDF upload, or URL scraping
- **AI-Powered Generation (Next-Gen Stack)**:
  - **Scripting**: Google Gemini 2.5 Flash ("Nano Banana") for superior storytelling
  - **Visuals**: Google Veo ("Vio") for 4K video generation & Vertex AI Imagen 3
  - **Voice**: Google Journey Voices for expressive, human-like narration
  - **Automated subtitle generation** (SRT format)
  - **Custom thumbnail generation**
- **Video Assembly**: Automated video creation with MoviePy
- **YouTube Upload**: Direct upload with OAuth2 authentication
- **Mock Mode**: Fully functional development mode without API credentials
- **Web Interface**: Simple Flask-based UI with real-time feedback
- **Comprehensive Logging**: Track every step of the generation process

## 🎯 What This Project Can Do

This AI-powered system transforms written content (novels, stories, articles) into professional-quality videos automatically. Here's what makes it powerful:

### Core Capabilities

1. **Multi-Format Input Processing**

   - **Text Input**: Paste any story or novel directly
   - **PDF Upload**: Extract text from PDF books/documents
   - **URL Scraping**: Pull content from web novels and articles
   - Automatic text segmentation into manageable scenes

2. **AI-Powered Content Generation**

   - **Intelligent Screenplay Writing**: Converts paragraphs into cinematic scene descriptions with dialogue
   - **Dynamic Image Generation**: Creates unique visuals for each scene
   - **Multi-Voice Narration**: Different AI voices for narrator and characters
   - **Automated Subtitles**: Time-synchronized SRT subtitle generation
   - **Custom Thumbnails**: Eye-catching cover images for videos

3. **Professional Video Production**

   - **Multiple Formats**: YouTube Shorts (9:16) and standard videos (16:9)
   - **Automated Assembly**: Combines images, audio, and subtitles seamlessly
   - **Direct YouTube Upload**: OAuth2-authenticated publishing
   - **Real-time Progress**: Live updates during generation process

4. **Developer-Friendly Features**
   - **Mock Mode**: Full functionality without API credentials for testing
   - **Modular Architecture**: Each AI service is independent and testable
   - **Comprehensive Logging**: Track every step for debugging
   - **Retry Logic**: Automatic recovery from transient API failures
   - **Unit Tests**: Full test coverage for all services

## 🔄 How It Works: Step-by-Step

### Phase 1: Input Processing

```
User Input → InputProcessor → Segmented Text
```

1. **Input Reception**: User provides content via web interface

   - Text: Direct paste
   - PDF: File upload with `pypdf` extraction
   - URL: Web scraping with `BeautifulSoup4`

2. **Text Segmentation**: Content is split into manageable scenes
   - Paragraph-based chunking
   - Configurable segment length (default: ~500 characters)
   - Preserves narrative flow

### Phase 2: AI Content Generation (Per Segment)

```
Segment → Screenplay → Image + Voice → Scene Assets
```

For each text segment, the pipeline executes:

#### Step 2.1: Screenplay Generation

- **Service**: `ScreenplayGenerator` (Google Gemini 2.5 Flash)
- **Input**: Raw text paragraph
- **Output**: Structured JSON screenplay
  ```json
  {
    "scene_description": "Cinematic visual description",
    "audio_script": [
      {"speaker": "Narrator", "text": "..."},
      {"speaker": "Character", "text": "..."}
    ],
    "dialogues": [...],
    "voiceover_text": "Full narration text"
  }
  ```
- **Features**:
  - Extracts dialogue and character names
  - Creates vivid scene descriptions for image generation
  - Structures narration for voice synthesis
  - Retry logic with exponential backoff

#### Step 2.2: Image Generation

- **Service**: `ImageGenerator` (Google Vertex AI Imagen 3)
- **Input**: `scene_description` from screenplay
- **Process**:
  1. Enhances prompt: `"Cinematic shot: {scene_description}"`
  2. Calls Vertex AI Imagen API
  3. Saves high-quality PNG image
- **Fallback**: Mock mode generates solid color placeholders
- **Output**: `scene_N.png`

#### Step 2.3: Multi-Voice Audio Generation

- **Service**: `VoiceGenerator` (Google Cloud Text-to-Speech + Journey Voices)
- **Input**: `audio_script` from screenplay
- **Process**:

  1. **Voice Mapping**: Matches characters to voice profiles

     - Reads `config/voices.yaml` for character-to-voice mappings
     - Heuristic detection (narrator, male, female, child)
     - Supports custom voice parameters (pitch, rate, language)

  2. **Multi-Voice Synthesis**:

     ```python
     for segment in audio_script:
         speaker = segment['speaker']
         text = segment['text']
         voice_profile = get_voice_for_character(speaker)
         generate_audio_segment(text, voice_profile)
     ```

  3. **Audio Concatenation**: Merges all segments using `moviepy`
     - Maintains proper timing
     - Seamless transitions between speakers

- **Fallback**: Mock mode creates silent placeholder files
- **Output**: `voice_N.mp3`

### Phase 3: Video Assembly

```
All Scene Assets → VideoAssembler → Final Video
```

#### Step 3.1: Subtitle Generation

- **Service**: `SubtitleGenerator`
- **Process**:
  1. Analyzes audio duration for each scene
  2. Aligns text with timestamps
  3. Generates SRT format subtitles
- **Output**: `subtitles.srt`

#### Step 3.2: Video Composition

- **Service**: `VideoAssembler` (MoviePy)
- **Process**:

  1. **For Each Scene**:

     - Load image as video clip (duration = audio length)
     - Overlay audio track
     - Add subtitle text overlay

  2. **Concatenation**:
     - Combine all scene clips sequentially
     - Apply video format (9:16 or 16:9)
     - Encode to MP4 (H.264 codec)

- **Output**: `final_video.mp4`

#### Step 3.3: Thumbnail Generation

- **Service**: `ThumbnailGenerator`
- **Process**:
  1. Generates eye-catching cover image
  2. Overlays title text
  3. Optimizes for YouTube thumbnail specs
- **Output**: `thumbnail.png`

### Phase 4: Publishing

```
Final Assets → YouTubeUploader → Published Video
```

#### YouTube Upload

- **Service**: `YouTubeUploader` (Google YouTube Data API v3)
- **Authentication**: OAuth2 flow
- **Process**:
  1. Authenticates user (first-time browser popup)
  2. Uploads video file
  3. Sets metadata (title, description, tags)
  4. Attaches thumbnail
  5. Returns video URL
- **Fallback**: Mock mode simulates upload and logs details

### Phase 5: Real-Time Feedback

```
Pipeline Progress → Server-Sent Events → Web UI Updates
```

- **Technology**: Flask SSE (Server-Sent Events)
- **Updates Include**:
  - Current step (e.g., "Processing segment 3/10")
  - Progress percentage (0-100%)
  - Status messages (success/error)
- **User Experience**: Live progress bar and status text in browser

## 🧠 AI Models & Technologies Used

### Current Implementation (Next-Gen Google Stack)

| Component      | Technology                         | Purpose                                       |
| -------------- | ---------------------------------- | --------------------------------------------- |
| **Screenplay** | Google Gemini 2.5 Flash            | Converts paragraphs to structured screenplays |
| **Images**     | Vertex AI Imagen 3                 | Generates cinematic scene visuals             |
| **Video**      | Google Veo (Future)                | 4K video clip generation                      |
| **Voice**      | Google Cloud TTS (Neural2/Journey) | Multi-voice narration with character voices   |
| **Assembly**   | MoviePy                            | Video editing and composition                 |
| **Upload**     | YouTube Data API v3                | Automated publishing                          |

### Alternative Configurations

See `COST_ESTIMATE.md` for detailed comparisons:

- **Budget**: Free/local models (Gemini Flash, Stable Diffusion)
- **Standard**: Google Pro tier (~$15/month)
- **Hybrid**: Mix of premium voice (ElevenLabs) + standard visuals
- **Premium**: Best-in-class tools (Midjourney, Udio, Sora)

## 📊 Project Statistics

- **Total Services**: 8 modular AI services
- **Code Organization**: 15+ Python modules
- **Test Coverage**: 100% of core services
- **Supported Formats**: 2 video aspect ratios
- **Input Methods**: 3 (text, PDF, URL)
- **Voice Profiles**: 4+ configurable character voices
- **API Integrations**: 4 (Gemini, Vertex AI, Cloud TTS, YouTube)

## 🏗️ Architecture

```
ai_novel_to_video/
├── services/           # Modular AI services
│   ├── input_processor.py
│   ├── screenplay_generator.py
│   ├── image_generator.py
│   ├── voice_generator.py
│   ├── video_assembler.py
│   ├── subtitle_generator.py
│   ├── thumbnail_generator.py
│   └── youtube_uploader.py
├── processing/         # Core pipeline
│   └── pipeline.py
├── utils/             # Utilities
│   └── logger.py
├── templates/         # Web UI
│   └── index.html
├── input/            # Input files
├── output/           # Generated videos
└── logs/             # Application logs
```

## 📋 Prerequisites

- **Python**: 3.10 or higher
- **Operating System**: macOS, Linux, or Windows
- **Google Cloud Account** (optional, for production use)
- **YouTube Account** (optional, for upload feature)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/nnalin04/AI-Powered-Novel-to-Video-Generator.git
cd AI-Powered-Novel-to-Video-Generator
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up API Keys (Optional)

Create a `.env` file in the project root:

```bash
# Google Gemini API (for screenplay generation)
GOOGLE_API_KEY=your_gemini_api_key_here

# Google Cloud Project (for Vertex AI and TTS)
GOOGLE_CLOUD_PROJECT=your_project_id_here

# YouTube Upload (optional)
# Place your client_secrets.json in the project root
```

> **Note**: The application works in **mock mode** without API keys, generating placeholder content for testing.

### 5. Run the Application

```bash
python ai_novel_to_video/app.py
```

Open your browser and navigate to: `http://localhost:5001`

## 🔑 API Key Setup (Detailed)

### Option 1: Mock Mode (No API Keys)

The application automatically falls back to mock mode if credentials are missing. Perfect for:

- Testing the workflow
- Development without API costs
- Understanding the architecture

### Option 2: Production Mode (Full API Access)

#### A. Google Gemini API

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key
3. Add to `.env`: `GOOGLE_API_KEY=your_key_here`

#### B. Google Cloud (Vertex AI & Text-to-Speech)

1. Create a project in [Google Cloud Console](https://console.cloud.google.com)
2. Enable APIs:
   - Vertex AI API
   - Cloud Text-to-Speech API
3. Set up Application Default Credentials:
   ```bash
   gcloud auth application-default login
   ```
4. Add to `.env`: `GOOGLE_CLOUD_PROJECT=your_project_id`

#### C. YouTube Data API (Optional)

1. Create OAuth 2.0 credentials in [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Download the JSON file as `client_secrets.json`
3. Place it in the project root
4. First upload will trigger OAuth flow in browser

## 🎯 Usage

### Web Interface

1. **Start the server**: `python ai_novel_to_video/app.py`
2. **Open**: `http://localhost:5001`
3. **Select input type**:
   - **Text**: Paste your story directly
   - **PDF**: Upload a PDF file
   - **URL**: Provide a web novel URL
4. **Choose video format**:
   - Short Video (9:16) - for YouTube Shorts, Instagram Reels
   - Full-Length Video (16:9) - for standard YouTube videos
5. **Click "Generate Video"**
6. **Wait**: Generation may take several minutes
7. **Check output**: Videos saved in `ai_novel_to_video/output/`

### Command Line Testing

```bash
# Test individual components
python verify_image_gen.py
python verify_voice_gen.py
python verify_video_gen.py
python verify_subtitle_gen.py
python verify_thumbnail_gen.py
python verify_upload.py

# Test full pipeline
python verify_pipeline.py
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_image_generator.py

# Run with coverage
pytest --cov=ai_novel_to_video tests/
```

## 📁 Output Files

After generation, you'll find:

```
ai_novel_to_video/output/
├── scene_1.png          # Generated images
├── scene_2.png
├── voice_1.mp3          # Voiceover audio
├── voice_2.mp3
├── subtitles.srt        # Subtitle file
├── thumbnail.png        # Video thumbnail
└── final_video.mp4      # Final assembled video
```

## 🔧 Configuration

### Environment Variables

| Variable               | Required | Description                              |
| ---------------------- | -------- | ---------------------------------------- |
| `GOOGLE_API_KEY`       | No       | Gemini API key for screenplay generation |
| `GOOGLE_CLOUD_PROJECT` | No       | GCP project ID for Vertex AI and TTS     |
| `client_secrets.json`  | No       | YouTube OAuth credentials file           |

### Mock Mode Behavior

When credentials are missing, services operate in mock mode:

- **ScreenplayGenerator**: Returns a warning, requires API key
- **ImageGenerator**: Creates solid color placeholder images
- **VoiceGenerator**: Creates silent audio files
- **VideoAssembler**: Uses placeholder assets
- **YouTubeUploader**: Simulates upload and prints details

## 📊 Logging

Logs are written to:

- **Console**: Real-time progress updates
- **File**: `ai_novel_to_video/logs/pipeline.log`

Log levels:

- `INFO`: Normal operation (progress updates)
- `WARNING`: Missing credentials, fallback to mock mode
- `ERROR`: Failures with stack traces

## 🐛 Troubleshooting

### Common Issues

**Problem**: "GOOGLE_API_KEY environment variable not set"

- **Solution**: Add the key to `.env` or run in mock mode

**Problem**: "Failed to initialize Google Cloud TTS"

- **Solution**: Run `gcloud auth application-default login` or use mock mode

**Problem**: "ModuleNotFoundError"

- **Solution**: Ensure virtual environment is activated and dependencies installed

**Problem**: Video generation takes too long

- **Solution**: This is normal for production mode with real AI APIs. Mock mode is faster for testing.

**Problem**: "Permission denied" on YouTube upload

- **Solution**: Complete OAuth flow in browser, approve app permissions

## 🧪 Development

### Project Structure

- **Services**: Each AI feature is a separate, testable module
- **Pipeline**: Orchestrates the entire workflow
- **Tests**: Unit tests with mocked API calls
- **Verification Scripts**: End-to-end testing tools

### Adding New Features

1. Create service in `ai_novel_to_video/services/`
2. Add to `VideoGenerationPipeline` in `processing/pipeline.py`
3. Write tests in `tests/`
4. Create verification script

### Running in Development Mode

```bash
# Enable debug mode
export FLASK_ENV=development
python ai_novel_to_video/app.py
```

## 📦 Dependencies

Key libraries:

- `flask` - Web framework
- `google-generativeai` - Gemini API
- `google-cloud-aiplatform` - Vertex AI (Imagen)
- `google-cloud-texttospeech` - Voice generation
- `google-api-python-client` - YouTube upload
- `moviepy` - Video assembly
- `pypdf` - PDF processing
- `beautifulsoup4` - URL scraping
- `Pillow` - Image manipulation

See `requirements.txt` for complete list.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## 📄 License

This project is open-source. See LICENSE file for details.

## 🙏 Acknowledgments

- Google AI for Gemini, Vertex AI, and Cloud TTS
- MoviePy for video processing
- Flask for the web framework

## 📞 Support

For issues or questions:

- Open an issue on GitHub
- Check the logs in `ai_novel_to_video/logs/`
- Review verification scripts for examples

---

**Happy Video Generation! 🎥✨**
