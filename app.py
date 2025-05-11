import streamlit as st
import pandas as pd
import isodate
from datetime import datetime
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
st.title("📺 YouTube Video Finder & Scorer")

st.markdown("""
<style>
    body, .stApp {
        background-color: white;
        color: black;
    }
    .video-container {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        margin-bottom: 2em;
        gap: 2em;
    }
    .podium {
        text-align: center;
        padding: 1em;
        border-radius: 10px;
    }
    .first { background-color: #ffd700; height: 260px; }
    .second { background-color: #c0c0c0; height: 220px; }
    .third { background-color: #cd7f32; height: 200px; }
    .video-card {
        border-radius: 12px;
        padding: 1em;
        background: linear-gradient(135deg, #fefefe, #f2f2f2);
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        margin-bottom: 1.5em;
        text-align: left;
    }
    .video-rank {
        font-weight: bold;
        font-size: 1.2rem;
        border-radius: 8px;
        padding: 0.3em 0.6em;
        display: inline-block;
        color: white;
        background-color: #f39c12;
        margin-bottom: 0.5em;
    }
    .video-thumbnail {
        border-radius: 10px;
        width: 100%;
        max-width: 360px;
    }
    .video-stars {
        font-size: 1.1rem;
        color: #f1c40f;
    }
</style>
""", unsafe_allow_html=True)

topic = st.text_input("Enter a topic to search for educational videos:", "")

if topic:
    with st.spinner("Fetching and analyzing videos..."):
        video_ids = search_videos(topic)
        video_data = get_video_details(video_ids)

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
        df['published'] = pd.to_datetime(df['published']).dt.tz_localize(None)

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
        st.subheader("🏆 Top 3 Recommendations")

        st.markdown("### 📋 Video Recommendations")
        for i, row in top3.iterrows():
            stars = "⭐" * round((row['final_score'] / top_score) ** 0.7 * 5)
            st.markdown(f"""
            <div class="video-card">
                <div class="video-rank">#{i + 1}</div>
                <img class="video-thumbnail" src="https://img.youtube.com/vi/{row['video_id']}/0.jpg" />
                <h4>{row['title']}</h4>
                <p><em>{row['channel']}</em></p>
                <p class="video-stars">{stars}</p>
                <p>⏱️ {row['duration_str']}<br>🔗 <a href="{row['url']}" target="_blank">Watch on YouTube</a></p>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("🔽 Show Next 2 Suggestions"):
            next2 = df.sort_values("rank").iloc[3:5]
            for i, row in next2.iterrows():
                if row['duration_minutes'] < 1.01:
                    continue
                st.image(f"https://img.youtube.com/vi/{row['video_id']}/0.jpg", width=320)
                st.markdown(f"""
**#{row['rank']} — {row['title']}**  
*Channel:* {row['channel']}  
⏱️ Duration: {row['duration_str']}  
🔗 [Watch on YouTube]({row['url']})
---
""", unsafe_allow_html=True)

        # Export options
        excel_path = "top_videos_scored.xlsx"
        df.to_excel(excel_path, index=False)

        markdown_summary = f"# Top 3 YouTube Videos for '{topic}'\n\n"
        for i, row in top3.iterrows():
            if row['duration_minutes'] < 1.01:
                continue
            stars = round((row['final_score'] / top_score) ** 0.7 * 5, 2)
            markdown_summary += f"#{row['rank']} — **{row['title']}** by *{row['channel']}*\n"
            markdown_summary += f"🔗 [Watch here]({row['url']})\n"
            markdown_summary += f"⭐ Score: {stars} / 5\n\n"

        st.download_button("📥 Download Excel", data=open(excel_path, "rb"), file_name="top_videos_scored.xlsx")
        st.download_button("📥 Download Markdown Summary", data=markdown_summary, file_name="top_3_summary.md")
