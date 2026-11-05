"""Analytics and Metrics Computation Module for Social Media Dashboard."""

from typing import Any, Dict
import numpy as np
import pandas as pd


def compute_kpi_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate executive high-level summary KPIs."""
    if df.empty:
        return {}

    total_impressions = int(df["impressions"].sum())
    total_reach = int(df["reach"].sum())
    total_likes = int(df["likes"].sum())
    total_comments = int(df["comments"].sum())
    total_shares = int(df["shares"].sum())
    total_saves = int(df["saves"].sum())
    total_interactions = int(df["total_interactions"].sum())

    overall_er = round((total_interactions / max(total_impressions, 1)) * 100, 2)
    avg_post_er = round(df["engagement_rate"].mean(), 2)

    return {
        "total_posts": len(df),
        "total_impressions": total_impressions,
        "total_reach": total_reach,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_shares": total_shares,
        "total_saves": total_saves,
        "total_interactions": total_interactions,
        "overall_er": overall_er,
        "avg_post_er": avg_post_er,
    }


def compute_content_type_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze engagement metrics sliced by content type."""
    summary = df.groupby(["platform", "content_type"]).agg(
        post_count=("post_id", "count"),
        avg_impressions=("impressions", "mean"),
        avg_likes=("likes", "mean"),
        avg_comments=("comments", "mean"),
        avg_shares=("shares", "mean"),
        avg_engagement_rate=("engagement_rate", "mean"),
    ).reset_index()

    summary["avg_impressions"] = summary["avg_impressions"].round(0).astype(int)
    summary["avg_likes"] = summary["avg_likes"].round(0).astype(int)
    summary["avg_comments"] = summary["avg_comments"].round(0).astype(int)
    summary["avg_shares"] = summary["avg_shares"].round(0).astype(int)
    summary["avg_engagement_rate"] = summary["avg_engagement_rate"].round(2)

    return summary.sort_values(by="avg_engagement_rate", ascending=False)


def compute_time_series_trend(df: pd.DataFrame, freq: str = "W") -> pd.DataFrame:
    """Group engagement metrics over time (Weekly or Monthly)."""
    df_copy = df.copy()
    df_copy = df_copy.set_index("published_at")
    trend = df_copy.groupby([pd.Grouper(freq=freq), "platform"]).agg(
        impressions=("impressions", "sum"),
        interactions=("total_interactions", "sum"),
        avg_er=("engagement_rate", "mean"),
        posts=("post_id", "count"),
    ).reset_index()
    trend["avg_er"] = trend["avg_er"].round(2)
    return trend
