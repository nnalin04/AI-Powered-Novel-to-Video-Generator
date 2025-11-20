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
