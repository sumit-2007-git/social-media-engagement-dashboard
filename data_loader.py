"""Data Loader and Generator Module for Social Media Engagement Dashboard.

Supports:
- High-fidelity synthetic generation for Instagram & YouTube.
- Live YouTube Data API v3 integration.
- Custom CSV ingestion.
"""

from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import requests

HASHTAG_POOLS = {
    "tech": ["#tech", "#coding", "#ai", "#python", "#datascience", "#developer", "#webdev"],
    "marketing": ["#marketing", "#socialmedia", "#growth", "#branding", "#digitalmarketing"],
    "lifestyle": ["#lifestyle", "#vlog", "#dailyroutine", "#creator", "#contentcreator"],
    "fitness": ["#fitness", "#health", "#workout", "#motivation", "#wellness"],
}

CONTENT_TYPES = {
    "Instagram": ["Reel", "Carousel", "Single Image", "Story"],
    "YouTube": ["Long Video", "Shorts", "Community Post", "Live Stream"],
}


def generate_synthetic_data(num_records: int = 400, seed: int = 42) -> pd.DataFrame:
    """Generate realistic historical engagement data for Instagram & YouTube."""
    random.seed(seed)
    np.random.seed(seed)

    records = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    for i in range(1, num_records + 1):
        platform = random.choices(["Instagram", "YouTube"], weights=[0.55, 0.45])[0]
        content_type = random.choice(CONTENT_TYPES[platform])

        # Random timestamp with peak posting tendencies
        random_days = random.uniform(0, 180)
        base_time = start_date + timedelta(days=random_days)
        # skew toward 9 AM - 11 AM and 6 PM - 9 PM
        hour = random.choices(
            list(range(24)),
            weights=[
                1, 1, 1, 1, 1, 2, 4, 6, 8, 12, 10, 9,
                7, 6, 6, 7, 9, 12, 14, 13, 10, 6, 3, 2
            ]
        )[0]
        minute = random.randint(0, 59)
        published_at = base_time.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # Baseline reach based on content type
        if content_type in ["Reel", "Shorts"]:
            base_impressions = int(np.random.lognormal(mean=9.5, sigma=0.8))  # Higher viral reach
        elif content_type in ["Carousel", "Long Video"]:
            base_impressions = int(np.random.lognormal(mean=8.8, sigma=0.6))
        else:
            base_impressions = int(np.random.lognormal(mean=8.0, sigma=0.5))

        impressions = max(500, base_impressions)
        reach = int(impressions * random.uniform(0.75, 0.95))

        # Engagement components
        like_ratio = random.uniform(0.04, 0.12)
        comment_ratio = random.uniform(0.005, 0.03)
        share_ratio = random.uniform(0.01, 0.05) if content_type in ["Reel", "Shorts", "Carousel"] else random.uniform(0.002, 0.02)
        save_ratio = random.uniform(0.01, 0.06) if platform == "Instagram" else random.uniform(0.005, 0.02)

        likes = int(impressions * like_ratio)
        comments = int(impressions * comment_ratio)
        shares = int(impressions * share_ratio)
        saves = int(impressions * save_ratio)

        # Category and hashtags
        category = random.choice(list(HASHTAG_POOLS.keys()))
        tags_sample = random.sample(HASHTAG_POOLS[category], k=random.randint(2, 4))
        hashtags_str = " ".join(tags_sample)

        total_interactions = likes + comments + shares + saves
        engagement_rate = round((total_interactions / impressions) * 100, 2)

        records.append({
            "post_id": f"POST_{platform[:2].upper()}_{i:04d}",
            "platform": platform,
            "content_type": content_type,
            "category": category.capitalize(),
            "published_at": published_at,
            "day_of_week": published_at.strftime("%A"),
            "hour_of_day": published_at.hour,
            "impressions": impressions,
            "reach": reach,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "saves": saves,
            "total_interactions": total_interactions,
            "engagement_rate": engagement_rate,
            "hashtags": hashtags_str,
            "caption": f"Exciting update about {category}! Check this out and let us know your thoughts {hashtags_str}",
        })

    df = pd.DataFrame(records)
    df = df.sort_values(by="published_at", ascending=False).reset_index(drop=True)
    return df


def fetch_youtube_api_data(api_key: str, channel_id: str, max_results: int = 50) -> pd.DataFrame:
    """Fetch live channel uploads and statistics via YouTube Data API v3."""
    base_url = "https://www.googleapis.com/youtube/v3"

    # Step 1: Get upload playlist
    channel_url = f"{base_url}/channels?part=contentDetails&id={channel_id}&key={api_key}"
    resp = requests.get(channel_url, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("items"):
        raise ValueError("Channel not found. Verify Channel ID and API Key.")

    uploads_playlist_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # Step 2: Fetch playlist items
    playlist_url = f"{base_url}/playlistItems?part=snippet&playlistId={uploads_playlist_id}&maxResults={max_results}&key={api_key}"
    resp_playlist = requests.get(playlist_url, timeout=10)
    resp_playlist.raise_for_status()
    items = resp_playlist.json().get("items", [])

    video_ids = [item["snippet"]["resourceId"]["videoId"] for item in items]
    if not video_ids:
        return pd.DataFrame()

    # Step 3: Fetch video statistics
    videos_url = f"{base_url}/videos?part=snippet,statistics&id={','.join(video_ids)}&key={api_key}"
    resp_videos = requests.get(videos_url, timeout=10)
    resp_videos.raise_for_status()
    video_details = resp_videos.json().get("items", [])

    parsed = []
    for vid in video_details:
        snip = vid["snippet"]
        stats = vid.get("statistics", {})
        published = datetime.fromisoformat(snip["publishedAt"].replace("Z", "+00:00"))

        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))
        shares = int(likes * 0.15)  # YouTube API doesn't expose public share count
        saves = int(likes * 0.08)

        total = likes + comments + shares + saves
        er = round((total / max(views, 1)) * 100, 2)

        parsed.append({
            "post_id": vid["id"],
            "platform": "YouTube",
            "content_type": "Long Video" if "short" not in snip.get("title", "").lower() else "Shorts",
            "category": "Tech",
            "published_at": published,
            "day_of_week": published.strftime("%A"),
            "hour_of_day": published.hour,
            "impressions": views,
            "reach": int(views * 0.85),
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "saves": saves,
            "total_interactions": total,
            "engagement_rate": er,
            "hashtags": " ".join([f"#{t}" for t in snip.get("tags", [])[:4]]),
            "caption": snip.get("title", ""),
        })

    return pd.DataFrame(parsed)


def load_custom_csv(uploaded_file) -> pd.DataFrame:
    """Parse and validate user-uploaded CSV file."""
    df = pd.read_csv(uploaded_file)
    required_cols = {"platform", "likes", "comments", "impressions"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Uploaded CSV is missing mandatory columns: {missing}")

    if "published_at" in df.columns:
        df["published_at"] = pd.to_datetime(df["published_at"])
        df["day_of_week"] = df["published_at"].dt.day_name()
        df["hour_of_day"] = df["published_at"].dt.hour
    else:
        df["published_at"] = pd.date_range(end=datetime.now(), periods=len(df), freq="D")
        df["day_of_week"] = df["published_at"].dt.day_name()
        df["hour_of_day"] = df["published_at"].dt.hour

    if "shares" not in df.columns:
        df["shares"] = (df["likes"] * 0.1).astype(int)
    if "saves" not in df.columns:
        df["saves"] = (df["likes"] * 0.05).astype(int)
    if "reach" not in df.columns:
        df["reach"] = (df["impressions"] * 0.85).astype(int)
    if "content_type" not in df.columns:
        df["content_type"] = "Post"
    if "category" not in df.columns:
        df["category"] = "General"

    df["total_interactions"] = df["likes"] + df["comments"] + df["shares"] + df["saves"]
    df["engagement_rate"] = round((df["total_interactions"] / df["impressions"].replace(0, 1)) * 100, 2)

    return df
