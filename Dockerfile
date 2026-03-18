FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# ffmpeg: for video processing
# libsm6, libxext6: for opencv/image processing
# git: for installing python packages from git
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose API port
EXPOSE 8000

CMD ["uvicorn", "ai_film_studio.web.api:app", "--host", "0.0.0.0", "--port", "8000"]
