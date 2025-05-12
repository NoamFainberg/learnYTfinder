from googleapiclient.discovery import build
import streamlit as st
import os

# Load .env locally, use st.secrets on Streamlit Cloud
if os.path.exists('.env'):
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
API_KEY = os.getenv("YOUTUBE_API_KEY") or st.secrets.get("YOUTUBE_API_KEY")

youtube = build('youtube', 'v3', developerKey=API_KEY)

def search_videos(query, max_results=10):
    try:
        request = youtube.search().list(
            q=query,
            part='id',
            type='video',
            maxResults=max_results
        )
        response = request.execute()
        video_ids = [item['id']['videoId'] for item in response['items']]
        return video_ids
    except Exception as e:
        print(f"❌ Error during search: {e}")
        return []

def get_video_details(video_ids):
    try:
        request = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=','.join(video_ids)
        )
        response = request.execute()
        return response['items']
    except Exception as e:
        print(f"❌ Error fetching video details: {e}")
        return []