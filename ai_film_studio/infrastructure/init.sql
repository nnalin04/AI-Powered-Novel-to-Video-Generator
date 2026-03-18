-- Create the vector extension if it doesn't exist
CREATE EXTENSION IF NOT EXISTS vector;

-- Ensure tables exist (Schema Definition)
CREATE TABLE IF NOT EXISTS episodes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    config_snapshot JSONB
);

CREATE TABLE IF NOT EXISTS scenes (
    id SERIAL PRIMARY KEY,
    episode_id INT REFERENCES episodes(id),
    sequence_order INT,
    script_text TEXT,
    visual_description TEXT,
    video_url TEXT,
    audio_track_path TEXT,
    duration FLOAT,
    status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    type VARCHAR(50),
    embedding VECTOR(768),
    metadata JSONB,
    version INT
);
