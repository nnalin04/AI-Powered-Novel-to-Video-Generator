import vertexai
from google.cloud import aiplatform
import json
import os

creds_path = '/Users/nishitnalinsrivastava/dev/AI Agent/AI-Powered Novel-to-Video Generator/secrets/vertex-service-key.json'
with open(creds_path, 'r') as f:
    creds = json.load(f)
    project_id = creds.get('project_id')

vertexai.init(project=project_id, location='us-central1')
aiplatform.init(project=project_id, location='us-central1')

print("--- Available Models ---")
# Generative AI platform doesn't have a simple 'list' for all foundation models via this SDK usually
# But we can try to initialize common ones to see if they exist or check model garden
models = [
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-1.0-pro",
    "gemini-1.5-pro-001",
    "gemini-1.5-flash-001",
    "gemini-1.5-pro-002",
    "gemini-1.5-flash-002"
]

for m in models:
    try:
        from vertexai.generative_models import GenerativeModel
        gm = GenerativeModel(m)
        # We can't easily 'check' without a call, so we'll just report we are trying aliases now
        print(f"Candidate: {m}")
    except Exception as e:
        print(f"Error with {m}: {e}")

