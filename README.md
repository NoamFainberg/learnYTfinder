

# LearnYTfinder 🎥📚

Discover the best educational YouTube videos — scored, ranked, and explained.

This app lets you enter any topic (like *venture capital*, *SQL*, or *machine learning*) and find the top-ranked videos based on:

- 👁️ Views per day
- 👍 Likes per view
- 💬 Comments per minute
- 📈 Overall engagement & freshness

## 🔗 Try It Live
[learnytfinder.streamlit.app](https://learnytfinder.streamlit.app)

## 🧠 How It Works

We use the YouTube API to gather video data and calculate a ranking score using:
- Normalized views, likes, and comments
- Freshness (release date vs. today)
- Auto-scaling score to 5-star system

## 🖥️ Run It Locally

```bash
git clone https://github.com/NoamFainberg/learnYTfinder.git
cd learnYTfinder
pip install -r requirements.txt
streamlit run app.py
```

## 📦 Requirements

- Python 3.9+
- `streamlit`, `pandas`, `isodate`, `python-dotenv`

## ✨ Roadmap

- Add filters (e.g., min views, duration)
- Integrate GPT summaries (optional)
- Improve mobile layout
- Support creator spotlight feature

## 🙌 Credits

Built by [@NoamFainberg](https://github.com/NoamFainberg) using Python, Streamlit, and YouTube Data API.
