"""
Dashboard page: Dataset Explorer & Export.
"""
import streamlit as st
import pandas as pd
from dashboard.components import render_section_header, render_metric_card
from utils.sentiment import extract_keywords
from utils.platform_config import get_platform_config


def render(df, platform="Twitter / X"):
    cfg = get_platform_config(platform)
    post_label = cfg["post_label"]

    render_section_header("📄", "Dataset Explorer")

    # ── Dataset Stats ────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("📋", str(len(df)), "Total Records")
    with c2:
        render_metric_card("📊", str(len(df.columns)), "Total Columns")
    with c3:
        render_metric_card("📅", str(df["Date"].nunique()) if "Date" in df.columns else "N/A", "Unique Dates")
    with c4:
        render_metric_card("👤", str(df["Username"].nunique()) if "Username" in df.columns else "N/A", "Unique Users")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filters ──────────────────────────────────────────────────────
    render_section_header("🔍", "Filter & Search")
    col1, col2, col3 = st.columns(3)

    filtered = df.copy()
    with col1:
        if "Sentiment" in df.columns:
            sents = st.multiselect("Sentiment", df["Sentiment"].unique().tolist(), default=df["Sentiment"].unique().tolist())
            filtered = filtered[filtered["Sentiment"].isin(sents)]
    with col2:
        if "Category" in df.columns:
            cats = st.multiselect("Category", df["Category"].unique().tolist(), default=df["Category"].unique().tolist())
            filtered = filtered[filtered["Category"].isin(cats)]
    with col3:
        search = st.text_input(f"Search {post_label.lower()}s", "")
        if search:
            filtered = filtered[filtered["Tweet"].str.contains(search, case=False, na=False)]

    st.markdown(f"**Showing {len(filtered)} of {len(df)} records**")

    # Rename columns for display
    display_df = filtered.rename(columns={
        "Tweet": post_label,
        "Retweets": cfg["shares_label"],
        "Replies": cfg["comments_label"],
        "Views": cfg["impressions_label"],
    })
    st.dataframe(display_df, width="stretch", height=400)

    # ── Word Cloud (keyword list) ────────────────────────────────────
    render_section_header("☁️", "Top Keywords")
    all_text = " ".join(filtered["Tweet"].tolist())
    keywords = extract_keywords(all_text, top_n=20)
    if keywords:
        kdf = pd.DataFrame(keywords, columns=["Keyword", "Frequency"])
        cols = st.columns(5)
        for i, (_, row) in enumerate(kdf.iterrows()):
            with cols[i % 5]:
                size = min(1.5 + row["Frequency"] * 0.15, 2.5)
                st.markdown(
                    f"<span style='font-size:{size}rem;color:#FCD535;font-weight:700;'>{row['Keyword']}</span>"
                    f" <span style='color:#848E9C;font-size:0.8rem;'>({row['Frequency']})</span>",
                    unsafe_allow_html=True
                )

    # ── Export ────────────────────────────────────────────────────────
    render_section_header("📥", "Export Analytics")
    col_a, col_b = st.columns(2)
    with col_a:
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button("📄 Download CSV Report", csv, "socialpulse_report.csv", "text/csv")
    with col_b:
        # JSON export
        json_data = filtered.to_json(orient="records", indent=2)
        st.download_button("📋 Download JSON Report", json_data, "socialpulse_report.json", "application/json")

    # ── Automated EDA Report ──────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    render_section_header("🤖", "Statistical Summary")
    st.markdown("""
    A quick overview of the numeric distribution and core statistics of your filtered dataset.
    """)
    if st.button("Generate Statistical Summary"):
        with st.spinner("Calculating statistics..."):
            stats_df = filtered.describe().T
            st.dataframe(stats_df, width="stretch")
