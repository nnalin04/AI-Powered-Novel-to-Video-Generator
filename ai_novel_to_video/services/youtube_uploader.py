import os
import pickle
from typing import Optional, List

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False

# Scopes required for uploading
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

class YouTubeUploader:
    def __init__(self, client_secrets_file: str = "client_secrets.json", token_file: str = "token.pickle"):
        self.client_secrets_file = client_secrets_file
        self.token_file = token_file
        self.youtube = None
        
        if not YOUTUBE_API_AVAILABLE:
            print("Warning: YouTube API libraries not installed. Uploads will be mocked.")
            return

        if not os.path.exists(client_secrets_file):
            print(f"Warning: '{client_secrets_file}' not found. Uploads will be mocked.")
            return

        self.youtube = self._authenticate()

    def _authenticate(self):
        """Authenticates the user and returns the YouTube service object."""
        creds = None
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)

        return build('youtube', 'v3', credentials=creds)

    def upload_video(self, video_path: str, title: str, description: str, tags: List[str], thumbnail_path: Optional[str] = None) -> Optional[str]:
        """
        Uploads a video to YouTube.
        Returns the Video ID if successful, or None.
        """
        if not self.youtube:
            return self._mock_upload(video_path, title, description, tags, thumbnail_path)

        try:
            print(f"Uploading video '{title}'...")
            
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'categoryId': '22' # People & Blogs
                },
                'status': {
                    'privacyStatus': 'private', # Default to private for safety
                    'selfDeclaredMadeForKids': False,
                }
            }

            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"Uploaded {int(status.progress() * 100)}%")
            
            video_id = response.get('id')
            print(f"Video uploaded! Video ID: {video_id}")
            
            if thumbnail_path and os.path.exists(thumbnail_path):
                self._upload_thumbnail(video_id, thumbnail_path)
                
            return video_id

        except Exception as e:
            print(f"Error uploading video: {e}")
            return self._mock_upload(video_path, title, description, tags, thumbnail_path)

    def _upload_thumbnail(self, video_id: str, thumbnail_path: str):
        """Uploads a custom thumbnail for the video."""
        try:
            print(f"Uploading thumbnail for video {video_id}...")
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            print("Thumbnail uploaded.")
        except Exception as e:
            print(f"Error uploading thumbnail: {e}")

    def _mock_upload(self, video_path: str, title: str, description: str, tags: List[str], thumbnail_path: Optional[str]) -> str:
        """Simulates an upload."""
        print("--- MOCK UPLOAD ---")
        print(f"Video: {video_path}")
        print(f"Title: {title}")
        print(f"Description: {description}")
        print(f"Tags: {tags}")
        if thumbnail_path:
            print(f"Thumbnail: {thumbnail_path}")
        print("-------------------")
        return "MOCK_VIDEO_ID_123"
