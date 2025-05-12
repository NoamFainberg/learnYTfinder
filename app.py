import streamlit as st
import pandas as pd
import isodate
from datetime import datetime
import os

# Load .env locally, use st.secrets on Streamlit Cloud
if os.path.exists('.env'):
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY") or st.secrets.get("YOUTUBE_API_KEY")
print("[DEBUG] YOUTUBE_API_KEY loaded:", YOUTUBE_API_KEY)

from utils.youtube_api import search_videos, get_video_details

def parse_duration(duration_str):
    duration = isodate.parse_duration(duration_str)
    total_seconds = duration.total_seconds()
    if total_seconds >= 3600:
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        return f"{hours}:{minutes:02}:{seconds:02}", total_seconds / 60
    else:
        return f"{int(total_seconds // 60)}:{int(total_seconds % 60):02}", total_seconds / 60

st.set_page_config(page_title="YouTube Video Finder", layout="centered")

# --- learnYT Centered Heading with One Spark Each Side ---
st.markdown('''
<style>
#learnyt-title {
  text-align: center;
  font-size: 2.25em;
  font-weight: 900;
  letter-spacing: 0.7px;
  margin-top: 3.5em;
  margin-bottom: 1.8em;
  background: linear-gradient(90deg, #7f53ff 10%, #f9c3e6 80%);
  color: #fff;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 2px 18px rgba(127,83,255,0.10), 0 1px 0 #fff;
  font-family: 'Segoe UI', 'Montserrat', 'Inter', sans-serif;
  display: block;
}
.learnyt-spark {
  font-size: 1.25em;
  vertical-align: middle;
  filter: drop-shadow(0 1px 2px #eee);
  display: inline-block;
}
#learnyt-emoji {
  font-size: 1.15em;
  vertical-align: middle;
  margin: 0 0.18em;
  filter: drop-shadow(0 1px 2px #eee);
  display: inline-block;
}
</style>
<div style="width:100%;text-align:center;">
  <h1 id="learnyt-title" style="display:inline-block;">
    <span class="learnyt-spark">✨</span>
    <span id="learnyt-emoji">learnYT</span>
    <span class="learnyt-spark">✨</span>
  </h1>
</div>
''', unsafe_allow_html=True)

# --- Friendly CTA above input ---
st.markdown('<div style="text-align:center; font-size:1.18em; color:#444; font-weight:600; margin-bottom:0.6em;">What do you want to learn today? <span style="color:#f3a683;">Type a topic and let the podium magic begin!</span></div>', unsafe_allow_html=True)

# --- Styled Search Bar ---
st.markdown("""
<style>
body, .stApp {
    background: linear-gradient(135deg, #dee4ff, #f9c3e6) !important;
    color: #1a1a1a;
    font-family: 'Segoe UI', sans-serif;
}
.stTextInput > div > div > input {
    border-radius: 14px;
    border: 1.5px solid #ffe066;
    font-size: 1.1em;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    padding: 0.9em 1.1em;
    background: #fff !important;
    color: #111;
    transition: border 0.2s;
}
.stTextInput > div[data-testid="stTextInputRootElement"] {
    background: transparent !important;
}

.stTextInput > div > div > input:focus {
    border: 2px solid #f3a683;
    outline: none;
}
</style>
""", unsafe_allow_html=True)

topic = st.text_input("", "", key="topic_search", label_visibility="collapsed", placeholder="Type a topic and press Enter...")
if not topic.strip():
    st.stop()

# (Removed duplicate st.text_input for 'Enter a topic to search for educational videos:')

st.markdown("""
<style>
body, .stApp {
    background: linear-gradient(135deg, #dee4ff, #f9c3e6);
    color: #1a1a1a;
    font-family: 'Segoe UI', sans-serif;
}
.podium-container {
    display: flex;
    justify-content: center;
    align-items: flex-end;
    gap: 32px;
    margin: 2em 0 3em 0;
}
.podium-card {
    position: relative;
    width: 300px;
    max-width: 300px;
    background: #fff;
    border-radius: 18px 18px 12px 12px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.12);
    padding: 1.7em 1.2em 1.2em 1.2em;
    box-sizing: border-box;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
    transition: transform 0.2s;
}
.podium-1 { min-height: 480px; margin-top: 0px; background: linear-gradient(135deg, #ffe066 70%, #fffbe0 100%); z-index: 3; }
.podium-2 { min-height: 440px; margin-top: 40px; background: linear-gradient(135deg, #b2bec3 70%, #f0f2f6 100%); z-index: 2; }
.podium-3 { min-height: 400px; margin-top: 80px; background: linear-gradient(135deg, #f3a683 70%, #fff0e0 100%); z-index: 1; }
.podium-rank {
    position: absolute;
    top: 8px;
    left: 50%;
    transform: translateX(-50%);
    background: #222;
    color: #fff;
    font-size: 2.5em;
    font-weight: bold;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    border: 4px solid #fff;
    z-index: 10;
}
.podium-thumb {
    width: 90%;
    border-radius: 10px;
    margin-top: 36px;
    margin-bottom: 0.7em;
    object-fit: cover;
}
.podium-title {
    font-size: 1.1em;
    font-weight: 600;
    text-align: center;
    margin: 0.4em 0 0.1em 0;
    white-space: normal;
    overflow-wrap: break-word;
    word-break: break-word;
    width: 100%;
    display: -webkit-box;
    -webkit-line-clamp: 5;
    -webkit-box-orient: vertical;
    overflow: hidden;
    max-height: 6.5em; /* ~5 lines */
}
.podium-author {
    font-size: 0.95em;
    color: #555;
    margin-bottom: 0.3em;
    text-align: center;
}
.podium-score {
    font-size: 1em;
    color: #222;
    margin-bottom: 0.2em;
    font-weight: 500;
}
.podium-watch {
    font-size: 0.95em;
    color: #888;
    margin-bottom: 0;
}
</style>
</style>
""", unsafe_allow_html=True)

# Removed duplicate topic input (was: st.text_input('Enter a topic to search for educational videos:', ''))

if topic:
    with st.spinner("Fetching and analyzing videos..."):
        video_ids = search_videos(topic)
        video_data = get_video_details(video_ids)
        print("[DEBUG] video_data:", video_data)

        records = []
        for item in video_data:
            stats = item.get('statistics', {})
            snippet = item['snippet']
            duration_str, duration_minutes = parse_duration(item['contentDetails']['duration'])

            records.append({
                'title': snippet['title'],
                'channel': snippet['channelTitle'],
                'published': snippet['publishedAt'],
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0)),
                'duration_minutes': round(duration_minutes, 2),
                'duration_str': duration_str,
                'video_id': item['id'],
                'url': f"https://www.youtube.com/watch?v={item['id']}",
            })

        df = pd.DataFrame(records)
        print("[DEBUG] df.columns:", df.columns)
        if 'published' in df.columns:
            df['published'] = pd.to_datetime(df['published']).dt.tz_localize(None)
        else:
            st.error("❌ The 'published' column is missing. Please ensure the API response includes it.")
            st.stop()

        df['likes_per_view'] = df['likes'] / df['views']
        df['comments_per_minute'] = df['comments'] / (df['duration_minutes'] + 0.1)
        now = pd.Timestamp.now(tz=None)
        df['views_per_day'] = df['views'] / ((now - df['published']).dt.days + 1)

        for col in ['likes_per_view', 'comments_per_minute', 'views_per_day', 'views']:
            min_val = df[col].min()
            max_val = df[col].max()
            df[f'norm_{col}'] = (df[col] - min_val) / (max_val - min_val + 1e-9)

        df['final_score'] = (
            df['norm_likes_per_view'] * 0.3 +
            df['norm_comments_per_minute'] * 0.2 +
            df['norm_views_per_day'] * 0.3 +
            df['norm_views'] * 0.2
        ) * 10

        df['rank'] = df['final_score'].rank(ascending=False, method='min').astype(int)

        # Remove shorts (videos under 1 minute)
        df = df[df['duration_minutes'] >= 1.01].copy()

        # Re-rank remaining videos
        df = df.sort_values("final_score", ascending=False).reset_index(drop=True)
        df["rank"] = df.index + 1

        top3 = df.sort_values("rank").head(3)
        top_score = top3['final_score'].max()
        st.markdown('<h3 style="text-align:center;">🏆 Top 3 Recommendations</h3>', unsafe_allow_html=True)

        # Podium layout for top 3 cards (improved structure)
        podium_html = '<div class="podium-container">'
        top3_list = top3.to_dict(orient="records")
        # Render 2nd place (left) if exists
        if len(top3_list) > 1:
            podium_html += (
                f'<div class="podium-card podium-2">'
                f'<div class="podium-rank">2</div>'
                f'<img class="podium-thumb" src="https://img.youtube.com/vi/{top3_list[1]["video_id"]}/0.jpg" />'
                f'<div class="podium-title" title="{top3_list[1]["title"]}">#2 &mdash; {top3_list[1]["title"]}</div>'
                f'<div class="podium-author">{top3_list[1]["channel"]}</div>'
                f'<div class="podium-score">Score: {round(top3_list[1]["final_score"],2)}</div>'
                f'<div class="podium-watch">⏱️ {top3_list[1]["duration_str"]}<br>🔗 <a href="{top3_list[1]["url"]}" target="_blank">Watch</a></div>'
                f'</div>'
            )
        # Render 1st place (center) if exists
        if len(top3_list) > 0:
            podium_html += (
                f'<div class="podium-card podium-1">'
                f'<div class="podium-rank">1</div>'
                f'<img class="podium-thumb" src="https://img.youtube.com/vi/{top3_list[0]["video_id"]}/0.jpg" />'
                f'<div class="podium-title" title="{top3_list[0]["title"]}">#1 &mdash; {top3_list[0]["title"]}</div>'
                f'<div class="podium-author">{top3_list[0]["channel"]}</div>'
                f'<div class="podium-score">Score: {round(top3_list[0]["final_score"],2)}</div>'
                f'<div class="podium-watch">⏱️ {top3_list[0]["duration_str"]}<br>🔗 <a href="{top3_list[0]["url"]}" target="_blank">Watch</a></div>'
                f'</div>'
            )
        # Render 3rd place (right) if exists
        if len(top3_list) > 2:
            podium_html += (
                f'<div class="podium-card podium-3">'
                f'<div class="podium-rank">3</div>'
                f'<img class="podium-thumb" src="https://img.youtube.com/vi/{top3_list[2]["video_id"]}/0.jpg" />'
                f'<div class="podium-title" title="{top3_list[2]["title"]}">#3 &mdash; {top3_list[2]["title"]}</div>'
                f'<div class="podium-author">{top3_list[2]["channel"]}</div>'
                f'<div class="podium-score">Score: {round(top3_list[2]["final_score"],2)}</div>'
                f'<div class="podium-watch">⏱️ {top3_list[2]["duration_str"]}<br>🔗 <a href="{top3_list[2]["url"]}" target="_blank">Watch</a></div>'
                f'</div>'
            )
        podium_html += "</div>"
        st.markdown(podium_html, unsafe_allow_html=True)

        # Show videos 4 and 5 only inside a native Streamlit expander, side by side
        # Use only the native Streamlit expander with a styled label
        with st.expander('✨ **Show More Suggestions**', expanded=False):
            next2 = df.sort_values("rank").iloc[3:5]
            cols = st.columns(2)
            for idx, (i, row) in enumerate(next2.iterrows()):
                with cols[idx]:
                    st.markdown(f'''
                    <div style="background:#fff; border-radius:14px; box-shadow:0 4px 16px rgba(0,0,0,0.10); padding:1.2em 1em 1em 1em; margin:0.8em 0; display:flex; flex-direction:column; align-items:center;">
                        <img src="https://img.youtube.com/vi/{row['video_id']}/0.jpg" style="width:95%;border-radius:10px;margin-bottom:0.7em;object-fit:cover;" />
                        <div style="font-size:1.08em;font-weight:600;text-align:center;margin:0.2em 0 0.1em 0;overflow-wrap:break-word;word-break:break-word;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;max-height:4em;">#{row['rank']} — {row['title']}</div>
                        <div style="font-size:0.95em;color:#555;margin-bottom:0.3em;text-align:center;">{row['channel']}</div>
                        <div style="font-size:1em;color:#222;margin-bottom:0.2em;font-weight:500;">Score: {round(row['final_score'],2)}</div>
                        <div style="font-size:0.95em;color:#888;margin-bottom:0;">⏱️ {row['duration_str']}<br>🔗 <a href="{row['url']}" target="_blank">Watch</a></div>
                    </div>
                    ''', unsafe_allow_html=True)

        # Only build markdown_summary for top3
        markdown_summary = f"# Top 3 YouTube Videos for '{topic}'\n\n"
        for i, row in top3.iterrows():
            if row['duration_minutes'] < 1.01:
                continue