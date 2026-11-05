# 📊 Social Media Engagement Dashboard & Strategic Recommender

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=sumit-2007-git/social-media-engagement-dashboard)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An end-to-end social media intelligence platform that ingests, analyzes, and visualizes cross-platform engagement metrics (Instagram & YouTube) and utilizes an algorithmic recommendation engine to uncover optimal posting times and high-ROI content strategies.

---

## 🌟 Key Features

- **Omnichannel Metrics Tracking**: In-depth analysis of Likes, Comments, Shares, Saves, Impressions, Reach, and calculated Engagement Rate.
- **Engagement Rate Formulation**:
  $$\text{Engagement Rate (\%)} = \left(\frac{\text{Likes} + \text{Comments} + \text{Shares} + \text{Saves}}{\text{Impressions}}\right) \times 100$$
- **Interactive Day-Hour Heatmap**: 24×7 cross-tabulated heatmap showing historic performance trends by day and hour of publication.
- **Automated Posting Window Recommender**: Computes top 3 optimal publication slots with expected percentage engagement boost.
- **Strategic Content Playbook**: Actionable algorithmic recommendations for format distribution (Reels/Shorts vs. Longform), viral share triggers, and topical pillars.
- **Multiple Data Ingestion Modes**:
  1. High-fidelity synthetic generation simulating 400+ historical posts.
  2. Live YouTube Data API v3 connector (enter API key + Channel ID).
  3. Custom CSV drag-and-drop file uploader.
- **Data Export**: Single-click CSV export of filtered dataset.

---

## 🏗️ Project Architecture

```
social-media-engagement-dashboard/
├── app.py                  # Main Streamlit interactive web application
├── analytics.py            # High-level KPIs, growth calculations, and time-series trends
├── recommender.py          # Heatmap computation, top windows, and strategy generator
├── data_loader.py          # Synthetic generator, YouTube API fetcher, and CSV parser
├── requirements.txt        # Python dependency manifest
├── Dockerfile              # Production container build definition
├── Procfile                # Heroku / Railway deployment entrypoint
├── render.yaml             # Render infrastructure-as-code deployment configuration
└── .streamlit/
    └── config.toml         # Custom dark-mode theme and UI preferences
```

---

## 🚀 Quickstart & Local Installation

### 1. Clone the repository
```bash
git clone https://github.com/sumit-2007-git/social-media-engagement-dashboard.git
cd social-media-engagement-dashboard
```

### 2. Set up virtual environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the application
```bash
streamlit run app.py
```
The dashboard will open automatically in your browser at `http://localhost:8501`.

---

## 🌐 1-Click Cloud Deployment

### Option A: Streamlit Community Cloud (Recommended & Free)
1. Fork or push this repository to your GitHub account.
2. Visit [share.streamlit.io](https://share.streamlit.io/).
3. Select your repository: `sumit-2007-git/social-media-engagement-dashboard`.
4. Main file path: `app.py`.
5. Click **Deploy!** Your app is live with a permanent public link.

### Option B: Render / Railway / Docker
Use the included `Dockerfile` or `render.yaml` for instant container deployment.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
