from utils.youtube_api import search_videos, get_video_details
import pandas as pd
import isodate
from datetime import datetime
import openai
from dotenv import load_dotenv
import os

def parse_duration(duration_str):
    return isodate.parse_duration(duration_str).total_seconds() / 60  # in minutes

def main():
    # use_gpt = False  # Set to True if you want to use OpenAI to generate the summary
    topic = input("Enter topic to search on YouTube: ")
    video_ids = search_videos(topic)
    video_data = get_video_details(video_ids)

    records = []
    for item in video_data:
        stats = item.get('statistics', {})
        snippet = item['snippet']
        duration = parse_duration(item['contentDetails']['duration'])

        records.append({
            'title': snippet['title'],
            'channel': snippet['channelTitle'],
            'published': snippet['publishedAt'],
            'views': int(stats.get('viewCount', 0)),
            'likes': int(stats.get('likeCount', 0)),
            'comments': int(stats.get('commentCount', 0)),
            'duration_minutes': round(duration, 2),
            'video_id': item['id'],
            'url': f"https://www.youtube.com/watch?v={item['id']}",
        })

    df = pd.DataFrame(records)

    # Convert published column to datetime and remove timezone info
    df['published'] = pd.to_datetime(df['published']).dt.tz_localize(None)

    # Derived metrics
    df['likes_per_view'] = df['likes'] / df['views']
    df['comments_per_minute'] = df['comments'] / (df['duration_minutes'] + 0.1)  # avoid divide-by-zero
    now = pd.Timestamp.now(tz=None)  # Ensure timezone-naive
    df['views_per_day'] = df['views'] / ((now - df['published']).dt.days + 1)

    # Normalize each metric
    for col in ['likes_per_view', 'comments_per_minute', 'views_per_day', 'views']:
        min_val = df[col].min()
        max_val = df[col].max()
        df[f'norm_{col}'] = (df[col] - min_val) / (max_val - min_val + 1e-9)

    # Final score (scale 1–10)
    df['final_score'] = (
        df['norm_likes_per_view'] * 0.3 +
        df['norm_comments_per_minute'] * 0.2 +
        df['norm_views_per_day'] * 0.3 +
        df['norm_views'] * 0.2
    ) * 10

    # Ranking
    df['rank'] = df['final_score'].rank(ascending=False, method='min').astype(int)

    df = df.sort_values(by='views', ascending=False)
    print("\n📺 Top Videos:\n")
    print(df[['title', 'views', 'likes', 'comments', 'duration_minutes', 'channel', 'url']])

    # Export table to Excel
    output_path = "top_videos_scored.xlsx"
    df.to_excel(output_path, index=False)
    print(f"\n📁 Table exported to: {output_path}")

    # Generate top 3 video summary (manually)
    top3 = df.sort_values(by="rank").head(3)

    manual_summary = f"# Top 3 YouTube Videos for '{topic}'\n\n"
    top_score = top3['final_score'].max()

    for i, row in top3.iterrows():
        stars = round((row['final_score'] / top_score) * 5, 2)
        manual_summary += f"{i+1}. **{row['title']}** by *{row['channel']}*\n"
        manual_summary += f"🔗 [Watch here]({row['url']})\n"
        manual_summary += f"⭐ Score: {stars} / 5\n\n"

    print("\n📄 Manual Summary of Top 3 Videos:\n")
    print(manual_summary)

    with open("top_3_summary.md", "w", encoding="utf-8") as f:
        f.write(manual_summary)

    print("\n📝 Manual summary saved to top_3_summary.md")

if __name__ == "__main__":
    main()