# AI-Powered Novel-to-Video Generator (Shorts & Full-Length)

---

## Objective
Develop a Python-based local application that converts a novel (from URL, text, or PDF) into either short-form vertical videos (YouTube Shorts, Instagram Reels) or full-length cinematic videos, complete with narration, animation, subtitles, and thumbnails — all powered primarily by Google AI APIs.

The program will include a local web interface where the user can upload a file or paste text, select whether to generate a "Short" or "Full Video," and trigger the automated workflow.

---

## Key Features Overview

| Feature | Description |
|---|---|
| LLM Integration | Powered by Google Gemini 1.5 Pro API |
| Smart Text Segmentation | LLM-based scene detection for coherent storytelling |
| AI Image & Animation | Vertex AI Imagen + Ken Burns effect for motion |
| Multi-Voice Generation | Character-specific voices using Google Cloud TTS |
| Background Music | Mood-based music selection and mixing |
| Subtitles | Generated via Gemini 1.5 API based on voiceover text |
| Video Assembly | Uses `ffmpeg` for merging video, audio, music, and subtitles |
| Upload Automation | Uses YouTube Data API v3 for video upload |
| Local UI | Flask + HTML/JS with real-time progress updates (SSE) |

---

## Documentation Links (for Google API Integration)

- [Google Gemini API](https://ai.google.dev/docs/gemini_api_overview)
- [Google Cloud Text-to-Speech](https://cloud.google.com/text-to-speech/docs/reference/rest)
- [Google Vertex AI Imagen](https://cloud.google.com/vertex-ai/docs/generative-ai/image/overview)
- [YouTube Data API v3](https://developers.google.com/youtube/v3/docs)

---

## Functional Requirements

### 1. Local Web Interface
A simple Flask-based web page that allows:
- **Upload PDF** or **Paste Text** directly.
- Dropdown Menu: Select either:
  - 🎬 *Short Video (9:16 vertical)*
  - 📺 *Full-Length Video (16:9 horizontal)*
- Submit Button: Starts the AI generation pipeline.

UI shows **real-time progress** (Server-Sent Events) with detailed status logs.

---

### 2. Input Handling
Supports:
- Story/Web Novel URL scraping (using `trafilatura` for clean extraction)
- Plain Text input (via web form)
- PDF Upload (manual upload or from watched folder)

Automatically detects and processes the input type.

---

### 3. Text Processing
- Extract clean story text.
- **Smart Segmentation**: Use Gemini to split text into logical scenes/dialogue blocks.
- Maintain logical story continuity for cinematic flow.

---

### 4. Paragraph-to-Screenplay Conversion (LLM with Gemini 1.5 Pro)
- Convert each paragraph into a screenplay object using Gemini API.
- Structure:
  ```json
  {
    "scene_description": "Detailed cinematic scene description",
    "dialogues": [{"character": "A", "line": "..."}, {"character": "B", "line": "..."}],
    "voiceover_text": "Narration text for TTS"
  }
  ```
- Output stored as JSON per paragraph

### 5. Image & Animation Generation (Google Vertex AI Imagen / MediaPipe)

- Use Vertex AI Imagen to generate scene visuals in:
  - 9:16 format for Shorts
  - 16:9 format for full-length videos
- **Animation**: Apply Ken Burns effect (pan/zoom) to static images for dynamism.
- Maintain character consistency across frames using embeddings or reference cache.

### 6. Voiceover Generation (Google Cloud TTS)

- Generate natural narration using Google WaveNet voices.
- **Multi-Voice**: Detect characters and assign distinct voice profiles automatically.
- Save each segment as .mp3 or .wav.

### 7. Subtitle Generation

- Use Gemini API to generate time-aligned subtitles (SRT/VTT) based on narration text and duration.
- Include configurable style templates (font, size, color).

### 8. Video Assembly (Local Processing)

- Use ffmpeg or moviepy to merge:
  - Background animation (Ken Burns)
  - Voiceover audio
  - **Background Music**: Mood-matched royalty-free tracks with ducking.
  - Captions
- Add intro/outro overlays:
  - For Shorts: “Part X – To Be Continued…”
  - For Full Videos: “The End”
- Output:
  - Shorts: 1080x1920 MP4
  - Full-Length: 1920x1080 MP4

### 9. Thumbnail Generation

- Generate consistent thumbnails using Vertex AI Imagen or Canva API.
- Add dynamic text overlays (“Part X”, title highlights).

### 10. Upload Automation

- Upload directly to YouTube Shorts or standard YouTube videos using the YouTube Data API v3.
- Add titles, descriptions, and tags automatically.
- Optionally allow Instagram/TikTok upload extension later.

### 11. File & Workflow Management

- Organized local directory structure:
  ```
  /ai_novel_to_video/
    ├── input/
    ├── processing/
    ├── output/
    │    ├── shorts/
    │    └── full_videos/
    ├── logs/
  ```
- Auto-cleanup of temporary files after successful runs.

### 12. Error Handling & Logging

- Comprehensive error handling for all Google API calls.
- Retry failed requests with exponential backoff.
- Maintain rotating logs (loguru or logging module).
- Display errors on the web dashboard in real-time.

### 13. Configuration & Security

- Load all credentials from .env file (no hardcoded keys).
- Example:
  ```
  GOOGLE_API_KEY="your_gemini_api_key"
  YOUTUBE_CLIENT_SECRET="your_youtube_secret.json"
  ```
- Configurable environment variables for:
  - Model type (Gemini, Imagen)
  - Output resolution
  - Voice preferences

## Non-Functional Requirements

Python 3.10+
Local runtime (no cloud hosting required)
Compatible with macOS, Linux, and Windows
Uses Flask for web UI and REST endpoints
Modular and extensible architecture

## Technology Stack (2025 Edition)
| Component | Technology |
|---|---|
| LLM | Google Gemini 1.5 Pro API |
| Image Generation | Google Vertex AI Imagen |
| Voiceover | Google Cloud TTS (WaveNet) |
| Animation | MoviePy (Ken Burns) / MediaPipe |
| Subtitles | Gemini 1.5 API |
| Video Assembly | ffmpeg / moviepy |
| Upload | YouTube Data API v3 |
| Web Interface | Flask + HTML + TailwindCSS (optional) |
| Logging | Loguru / Python logging |
## Deliverables

- `app.py` — Flask web server with upload & dropdown UI

- `generate_video.py` — Core workflow script

- `.env` — Stores API keys securely

- `templates/index.html` — Simple upload & selection interface

- `README.md` — Setup instructions and environment details


---

Would you like me to now generate the starter project structure and minimal working Flask web UI code (so you can run it locally right away)?