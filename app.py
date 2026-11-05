"""Social Media Engagement Dashboard & Strategic Recommender.

An end-to-end analytics platform to track content engagement metrics,
visualize cross-platform performance, and recommend optimal posting schedules.
"""

from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analytics import (
    compute_content_type_performance,
    compute_kpi_summary,
    compute_time_series_trend,
)
from data_loader import fetch_youtube_api_data, generate_synthetic_data, load_custom_csv
from recommender import (
    compute_posting_time_heatmap,
    generate_content_strategy,
    get_top_posting_windows,
)

# Page Configuration
st.set_page_config(
    page_title="Social Media Engagement Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #6366F1;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }
    .strategy-box {
        background-color: #1E293B;
        border-left: 4px solid #6366F1;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 14px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if "raw_data" not in st.session_state:
    st.session_state["raw_data"] = generate_synthetic_data(num_records=400)

# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Dashboard Controls")
    st.markdown("Customize your data source and active analytics filters.")

    data_source = st.radio(
        "Data Source Mode",
        ["Default Dataset (Instagram & YouTube)", "Upload Custom CSV", "Live YouTube API"],
    )

    if data_source == "Upload Custom CSV":
        uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
        if uploaded_file is not None:
            try:
                st.session_state["raw_data"] = load_custom_csv(uploaded_file)
                st.success("Custom CSV loaded successfully!")
            except Exception as e:
                st.error(f"Error reading CSV: {e}")

    elif data_source == "Live YouTube API":
        with st.expander("API Credentials", expanded=True):
            yt_key = st.text_input("YouTube Data API Key", type="password")
            yt_channel = st.text_input("Channel ID", placeholder="e.g. UC_x5XG1OV2P6uZZ5FSM9Ttw")
            if st.button("Fetch Live Channel Data"):
                if yt_key and yt_channel:
                    with st.spinner("Querying YouTube API..."):
                        try:
                            live_df = fetch_youtube_api_data(yt_key, yt_channel)
                            if not live_df.empty:
                                st.session_state["raw_data"] = live_df
                                st.success(f"Fetched {len(live_df)} videos!")
                            else:
                                st.warning("No videos returned.")
                        except Exception as e:
                            st.error(f"API Error: {e}")
                else:
                    st.warning("Please provide both API Key and Channel ID.")

    st.markdown("---")
    st.subheader("Filter Content")

    df_full = st.session_state["raw_data"]

    # Platform Filter
    available_platforms = sorted(df_full["platform"].unique())
    selected_platforms = st.multiselect("Platforms", available_platforms, default=available_platforms)

    # Content Type Filter
    available_types = sorted(df_full[df_full["platform"].isin(selected_platforms)]["content_type"].unique())
    selected_types = st.multiselect("Content Formats", available_types, default=available_types)

    # Category Filter
    available_cats = sorted(df_full["category"].unique())
    selected_cats = st.multiselect("Pillars / Categories", available_cats, default=available_cats)

    # Date Range Filter
    min_date = df_full["published_at"].min().date()
    max_date = df_full["published_at"].max().date()
    date_range = st.date_input("Date Window", value=(min_date, max_date), min_value=min_date, max_value=max_date)

# Apply Filters
df_filtered = df_full[
    (df_full["platform"].isin(selected_platforms)) &
    (df_full["content_type"].isin(selected_types)) &
    (df_full["category"].isin(selected_cats))
]

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_d, end_d = date_range
    df_filtered = df_filtered[
        (df_filtered["published_at"].dt.date >= start_d) &
        (df_filtered["published_at"].dt.date <= end_d)
    ]

# Header
st.title("📊 Social Media Engagement Dashboard")
st.markdown("Omnichannel performance tracker, best posting time heatmaps, and content strategy recommendations.")

if df_filtered.empty:
    st.warning("No records match the current filter selection. Please broaden your sidebar filters.")
    st.stop()

# Executive KPI Cards
kpis = compute_kpi_summary(df_filtered)

c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{kpis['total_impressions']:,}</div>
        <div class="metric-label">Total Impressions</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{kpis['total_reach']:,}</div>
        <div class="metric-label">Estimated Reach</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{kpis['total_likes']:,}</div>
        <div class="metric-label">Total Likes</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{kpis['total_shares']:,}</div>
        <div class="metric-label">Total Shares</div>
    </div>
    """, unsafe_allow_html=True)
with c5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{kpis['total_comments']:,}</div>
        <div class="metric-label">Comments</div>
    </div>
    """, unsafe_allow_html=True)
with c6:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{kpis['overall_er']}%</div>
        <div class="metric-label">Overall Eng. Rate</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabs Navigation
tab_overview, tab_heatmap, tab_strategy, tab_posts = st.tabs([
    "📈 Performance Trends",
    "🗓️ Best Posting Times",
    "🎯 Content Strategy Playbook",
    "📋 Content Explorer & Export",
])

# ----------------- TAB 1: OVERVIEW & TRENDS -----------------
with tab_overview:
    col_t1, col_t2 = st.columns([7, 5])

    with col_t1:
        st.subheader("Historical Engagement Rate Trend")
        trend_df = compute_time_series_trend(df_filtered, freq="W")
        fig_trend = px.line(
            trend_df,
            x="published_at",
            y="avg_er",
            color="platform",
            markers=True,
            labels={"published_at": "Week", "avg_er": "Average Engagement Rate (%)", "platform": "Platform"},
            title="Weekly Engagement Rate by Platform",
            color_discrete_map={"Instagram": "#E1306C", "YouTube": "#FF0000"},
            template="plotly_dark",
        )
        fig_trend.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_t2:
        st.subheader("Interactions Composition")
        interactions_breakdown = {
            "Likes": kpis["total_likes"],
            "Comments": kpis["total_comments"],
            "Shares": kpis["total_shares"],
            "Saves": kpis["total_saves"],
        }
        fig_donut = px.pie(
            names=list(interactions_breakdown.keys()),
            values=list(interactions_breakdown.values()),
            hole=0.55,
            color_discrete_sequence=["#6366F1", "#10B981", "#F59E0B", "#EC4899"],
            template="plotly_dark",
        )
        fig_donut.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_donut, use_container_width=True)

    st.subheader("Content Format Breakdown")
    format_stats = compute_content_type_performance(df_filtered)
    fig_fmt = px.bar(
        format_stats,
        x="content_type",
        y="avg_engagement_rate",
        color="platform",
        barmode="group",
        labels={"content_type": "Format", "avg_engagement_rate": "Avg Engagement Rate (%)"},
        color_discrete_map={"Instagram": "#E1306C", "YouTube": "#FF0000"},
        template="plotly_dark",
    )
    fig_fmt.update_layout(height=340, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_fmt, use_container_width=True)


# ----------------- TAB 2: BEST POSTING TIMES -----------------
with tab_heatmap:
    st.subheader("🗓️ Heatmap: Day of Week vs. Hour of Day")
    st.markdown("Colors represent the **Average Engagement Rate (%)** achieved by posts published in each specific time slot.")

    pivot_data = compute_posting_time_heatmap(df_filtered, metric="engagement_rate")

    fig_heat = px.imshow(
        pivot_data,
        labels=dict(x="Hour of Day (24h)", y="Day of Week", color="Eng. Rate (%)"),
        x=[f"{h:02d}:00" for h in range(24)],
        y=pivot_data.index,
        color_continuous_scale="Plasma",
        aspect="auto",
        template="plotly_dark",
    )
    fig_heat.update_layout(height=420, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("---")
    st.subheader("🚀 Top 3 Recommended Windows to Post")
    top_slots = get_top_posting_windows(df_filtered, top_n=3)

    slot_cols = st.columns(3)
    for i, slot in enumerate(top_slots):
        with slot_cols[i]:
            st.markdown(f"""
            <div class="strategy-box">
                <h4 style="margin: 0; color: #818CF8;">#{i+1} Best Window</h4>
                <h3 style="margin: 6px 0; color: #F8FAFC;">{slot['day']} @ {slot['hour']}</h3>
                <p style="margin: 0; color: #10B981; font-weight: 600;">Expected Boost: {slot['expected_boost']}</p>
                <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.85rem;">Average ER: {slot['avg_er']}% ({slot['historical_posts']} posts analyzed)</p>
            </div>
            """, unsafe_allow_html=True)


# ----------------- TAB 3: CONTENT STRATEGY -----------------
with tab_strategy:
    st.subheader("🎯 Data-Backed Strategic Recommendations")
    st.markdown("Automated algorithmic suggestions derived from cross-platform correlation and interaction patterns.")

    strategies = generate_content_strategy(df_filtered)

    for item in strategies:
        st.markdown(f"""
        <div class="strategy-box">
            <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #818CF8; font-weight: 700;">{item['category']}</span>
            <h4 style="margin: 6px 0 4px 0; color: #F8FAFC;">{item['recommendation']}</h4>
            <p style="margin: 4px 0; color: #CBD5E1; font-size: 0.95rem;">💡 <b>Why:</b> {item['rationale']}</p>
            <p style="margin: 4px 0 0 0; color: #34D399; font-size: 0.92rem;">👉 <b>Action Item:</b> {item['action']}</p>
        </div>
        """, unsafe_allow_html=True)


# ----------------- TAB 4: CONTENT EXPLORER -----------------
with tab_posts:
    st.subheader("📋 Granular Post Inventory")
    st.markdown(f"Displaying **{len(df_filtered)}** posts matching the active filters.")

    csv_export = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_export,
        file_name="social_media_engagement_data.csv",
        mime="text/csv",
    )

    display_cols = [
        "post_id", "platform", "content_type", "category",
        "published_at", "impressions", "reach", "likes",
        "comments", "shares", "engagement_rate", "caption"
    ]
    st.dataframe(
        df_filtered[display_cols],
        use_container_width=True,
        hide_index=True,
    )
