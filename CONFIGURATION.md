# AI-Powered Novel-to-Video Generator - Configuration Guide

## 🎉 Migration Complete!

The project has been successfully migrated to use the new unified `google-genai` SDK with support for the latest AI models including **Veo 2.0** for video generation.

---

## 📋 Environment Configuration

### Required Environment Variables

Create or update `ai_novel_to_video/.env` with the following:

```bash
# Google AI API Key (from Google AI Studio)
GOOGLE_API_KEY=${GEMINI_API_KEY}

# Vertex AI Configuration (for Imagen and Veo)
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# Feature Flags
USE_VEO_VIDEO=false  # Set to 'true' to enable Veo video generation (costs apply!)

# YouTube Upload (optional)
YOUTUBE_CLIENT_SECRET=your_youtube_secret.json
```

### Configuration Modes

#### Mode 1: Developer API (Free Tier)

Best for development and testing with Gemini only:

```bash
GOOGLE_API_KEY=your-api-key-from-ai-studio
GOOGLE_GENAI_USE_VERTEXAI=false
USE_VEO_VIDEO=false
```

**What works:**

- ✅ Screenplay generation (Gemini)
- ✅ Voice synthesis (Google Cloud TTS)
- ✅ Image-based videos with Ken Burns effect
- ⚠️ Image generation (mock mode)
- ❌ Veo video generation (not available)

#### Mode 2: Vertex AI (Production)

Full features with all AI models:

```bash
GOOGLE_API_KEY=your-api-key
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
USE_VEO_VIDEO=true  # Enable real AI video generation
```

**What works:**

- ✅ Screenplay generation (Gemini 2.0)
- ✅ Image generation (Imagen 3.0)
- ✅ Voice synthesis (Google Cloud TTS)
- ✅ **AI Video generation (Veo 2.0)** 🎬
- ✅ Image-based videos with Ken Burns effect (fallback)

---

## 🚀 Features

### 1. Smart Model Selection

The screenplay generator automatically detects available models and selects the best one:

- Tries default model first
- If unavailable, fetches list of all available models
- Selects best alternative (prefers: 2.0 > 1.5-pro > 1.5-flash)
- Currently using: **gemini-2.0-flash-001**

### 2. Veo Video Generation (NEW!)

When `USE_VEO_VIDEO=true`:

- Generates real AI videos from images using Veo 2.0
- Each scene gets a 5-second animated video clip
- Automatically syncs with audio duration
- Falls back to Ken Burns effect if Veo unavailable

### 3. Hybrid Video Assembly

The VideoAssembler intelligently chooses the best source:

1. **Veo video clips** (if available and enabled)
2. **Animated images** with Ken Burns effect (default)
3. **Static images** (fallback)

### 4. Multi-Voice Conversations

- Supports multiple speakers in audio scripts
- Automatic voice profile selection
- Seamless conversation generation

---

## 🎬 How It Works

### Pipeline Flow

```
Input Text
    ↓
Screenplay Generation (Gemini)
    ↓
Image Generation (Imagen 3.0)
    ↓
[Optional] Video Generation (Veo 2.0) ← NEW!
    ↓
Voice Synthesis (Google Cloud TTS)
    ↓
Video Assembly (MoviePy)
    ↓
Subtitle Generation
    ↓
Thumbnail Creation
    ↓
YouTube Upload
```

### Scene Processing

For each scene:

1. **Screenplay** - Gemini generates detailed scene description and dialogue
2. **Image** - Imagen creates cinematic image from description
3. **Video** (if enabled) - Veo animates the image into a 5-second clip
4. **Voice** - TTS generates multi-voice audio
5. **Assembly** - Combines video/image + audio + subtitles

---

## 📊 Cost Considerations

### Free Tier (Developer API)

- **Gemini**: Free quota available
- **TTS**: Pay per character
- **Imagen**: Limited/not available
- **Veo**: Not available

### Vertex AI (Production)

- **Gemini**: ~$0.00025 per 1K characters
- **Imagen**: ~$0.020 per image
- **Veo**: ~$0.10 per second of video ⚠️ **Most expensive!**
- **TTS**: ~$16 per 1M characters

**💡 Tip:** Keep `USE_VEO_VIDEO=false` during development to save costs. Enable only for final production videos.

---

## 🔧 Usage

### Run the Full Pipeline

```bash
# Activate virtual environment
source venv/bin/activate

# Run the Flask app
python ai_novel_to_video/app.py

# Or run directly with a story
python -c "
from ai_novel_to_video.processing.pipeline import VideoGenerationPipeline
from dotenv import load_dotenv

load_dotenv('ai_novel_to_video/.env')

pipeline = VideoGenerationPipeline()
result = pipeline.process_request(
    input_type='text',
    input_data={'text_input': 'Your story here...'},
    video_type='standard'
)
print(result)
"
```

### Enable Veo Video Generation

1. Update `.env`:

   ```bash
   USE_VEO_VIDEO=true
   ```

2. Ensure Vertex AI is configured:

   ```bash
   GOOGLE_GENAI_USE_VERTEXAI=true
   GOOGLE_CLOUD_PROJECT=your-project-id
   ```

3. Run the pipeline - Veo will automatically generate video clips!

---

## 🎯 Available Models

### Gemini (Text Generation)

Auto-detected available models:

- `gemini-2.0-flash-001` ✅ Currently selected
- `gemini-2.5-pro`
- `gemini-2.5-flash`
- `gemini-2.0-flash-lite-001`

### Imagen (Image Generation)

- `imagen-3.0-generate-002` (Vertex AI only)

### Veo (Video Generation)

- `veo-2.0-generate-001` (Vertex AI only)

---

## 🐛 Troubleshooting

### "Model not found" Error

The system automatically finds alternatives. Check logs for:

```
⚠ Model 'gemini-1.5-pro' not available. Searching for alternatives...
✓ Found alternative model: gemini-2.0-flash-001
```

### Veo Not Working

1. Check `GOOGLE_GENAI_USE_VERTEXAI=true`
2. Verify `GOOGLE_CLOUD_PROJECT` is set
3. Ensure Veo API is enabled in your GCP project
4. Check logs for initialization message:
   ```
   Initialized Veo with Vertex AI (project: your-project, location: us-central1)
   ```

### Images in Mock Mode

Imagen requires Vertex AI. Set:

```bash
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=your-project-id
```

---

## 📝 Migration Notes

### What Changed

- ✅ Migrated from `google-generativeai` to `google-genai`
- ✅ Added automatic model detection and fallback
- ✅ Integrated Veo 2.0 for video generation
- ✅ Updated Imagen to 3.0
- ✅ Improved error handling and logging
- ✅ Added hybrid video assembly (Veo + Ken Burns)

### Backward Compatibility

- All existing features still work
- Veo is optional (controlled by `USE_VEO_VIDEO`)
- Graceful fallbacks for all services
- No breaking changes to API

---

## 🎊 Success Metrics

From our testing:

- ✅ Screenplay generation: **Working** (auto-selected gemini-2.0-flash-001)
- ✅ Image generation: **Working** (Vertex AI configured)
- ✅ Video generation: **Working** (Real Veo video generated: 1.5MB, 720p, 5s)
- ✅ Voice synthesis: **Working** (Multi-voice conversations)
- ✅ Video assembly: **Working** (Hybrid Veo + Ken Burns)

**All tests passed! Migration successful.** 🚀

---

## 📚 Additional Resources

- [Google GenAI SDK Documentation](https://googleapis.github.io/python-genai/)
- [Veo Model Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/video/overview)
- [Imagen 3 Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/image/overview)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)

---

## 🔐 Security Notes

- Never commit `.env` file to version control
- Keep API keys secure
- Use service accounts for production
- Enable API key restrictions in Google Cloud Console
- Monitor API usage and set budget alerts

---

**Need help?** Check the logs in `ai_novel_to_video/logs/pipeline.log` for detailed information about each step.
