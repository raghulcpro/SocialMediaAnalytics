"""
Dashboard page: Analytics Deep Dive — Correlation Analysis & ML Feature Importance.
"""
import streamlit as st
import pandas as pd
import numpy as np
from dashboard.components import render_section_header, render_metric_card, render_info_panel
from utils.analytics import compute_correlation_matrix, compute_feature_importance, extract_topics, forecast_engagement
from utils.charts import correlation_heatmap, feature_importance_chart, scatter_chart, forecast_chart
from utils.platform_config import get_platform_config


def render(df, platform="Twitter / X"):
    cfg = get_platform_config(platform)
    render_section_header("🔬", "Analytics Deep Dive")

    st.markdown("""
    <div style="padding:12px 18px;border-radius:10px;background:rgba(252,213,53,0.06);
    border:1px solid rgba(252,213,53,0.12);margin-bottom:20px;">
        <span style="color:#FCD535;font-weight:700;">🧬 ML-Powered Analysis</span>
        <span style="color:#B7BDC6;font-size:0.9rem;margin-left:8px;">
            Correlation matrix, feature importance rankings, and statistical insights
            powered by scikit-learn.
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    # SECTION 1: CORRELATION MATRIX
    # ══════════════════════════════════════════════════════════════════
    render_section_header("🔗", "Feature Correlation Matrix")

    corr = compute_correlation_matrix(df)

    if corr.empty:
        st.warning("Not enough numeric features for correlation analysis.")
    else:
        # Correlation heatmap
        fig = correlation_heatmap(corr, "Pearson Correlation — All Engagement Features")
        st.plotly_chart(fig, use_container_width=True)

        # ── Top Correlated Pairs ─────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        render_section_header("📊", "Strongest Correlations")

        # Extract top pairs (exclude self-correlations)
        pairs = []
        cols = corr.columns.tolist()
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                pairs.append({
                    "Feature A": cols[i],
                    "Feature B": cols[j],
                    "Correlation": corr.iloc[i, j],
                    "Abs": abs(corr.iloc[i, j]),
                    "Direction": "🟢 Positive" if corr.iloc[i, j] > 0 else "🔴 Negative",
                    "Strength": _strength_label(abs(corr.iloc[i, j])),
                })
        pairs_df = pd.DataFrame(pairs).sort_values("Abs", ascending=False)

        # Show top 8 pairs
        top_pairs = pairs_df.head(8)

        col1, col2 = st.columns(2)
        with col1:
            # Strongest positive
            pos = pairs_df[pairs_df["Correlation"] > 0].head(1)
            if not pos.empty:
                r = pos.iloc[0]
                render_metric_card(
                    "🟢", f"{r['Correlation']:.3f}",
                    f"Strongest +ve: {r['Feature A']} × {r['Feature B']}",
                )
        with col2:
            # Strongest negative
            neg = pairs_df[pairs_df["Correlation"] < 0].head(1)
            if not neg.empty:
                r = neg.iloc[0]
                render_metric_card(
                    "🔴", f"{r['Correlation']:.3f}",
                    f"Strongest -ve: {r['Feature A']} × {r['Feature B']}",
                )

        # Table of top pairs
        display_pairs = top_pairs[["Feature A", "Feature B", "Correlation", "Direction", "Strength"]].reset_index(drop=True)
        display_pairs.index = display_pairs.index + 1
        st.dataframe(display_pairs, use_container_width=True)

        # ── Interactive Scatter Explorer ──────────────────────────────
        render_section_header("🎯", "Correlation Explorer")
        st.markdown(
            "<p style='color:#848E9C;font-size:0.9rem;'>Pick two features to visualize their relationship.</p>",
            unsafe_allow_html=True,
        )

        numeric_features = corr.columns.tolist()
        c1, c2 = st.columns(2)
        with c1:
            feat_x = st.selectbox("X-Axis Feature", numeric_features, index=0, key="corr_x")
        with c2:
            default_y = min(1, len(numeric_features) - 1)
            feat_y = st.selectbox("Y-Axis Feature", numeric_features, index=default_y, key="corr_y")

        if feat_x != feat_y:
            r_val = corr.loc[feat_x, feat_y]
            fig = scatter_chart(
                df, feat_x, feat_y,
                color="Sentiment" if "Sentiment" in df.columns else None,
                title=f"{feat_x} vs {feat_y}  (r = {r_val:.3f})",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Select two different features to see their correlation scatter plot.")

    # ══════════════════════════════════════════════════════════════════
    # SECTION 2: ML FEATURE IMPORTANCE
    # ══════════════════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)
    render_section_header("🤖", "ML Feature Importance")

    st.markdown("""
    <div style="padding:10px 16px;border-radius:8px;background:rgba(14,203,129,0.06);
    border:1px solid rgba(14,203,129,0.12);margin-bottom:16px;">
        <span style="color:#0ECB81;font-weight:600;">RandomForest Regressor</span>
        <span style="color:#848E9C;font-size:0.85rem;margin-left:6px;">
            Trained to predict EngagementScore. Shows which features matter most.
        </span>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("🧠 Training ML model..."):
        importance = compute_feature_importance(df)

    if importance["features"]:
        # Model performance metrics
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            r2 = importance["r2_score"]
            r2_label = "Excellent" if r2 > 80 else "Good" if r2 > 60 else "Moderate" if r2 > 40 else "Low"
            render_metric_card("🎯", f"{r2}%", f"Model R² Score ({r2_label})")
        with col_m2:
            render_metric_card("🌲", "100", "Trees in Forest")
        with col_m3:
            render_metric_card("📐", str(len(importance["features"])), "Features Analyzed")

        st.markdown("<br>", unsafe_allow_html=True)

        # Feature importance bar chart
        fig = feature_importance_chart(
            importance["features"],
            importance["importances"],
            "What Drives Engagement? — Feature Importance Ranking",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Top drivers insight panel
        top_3 = importance["features"][:3]
        top_3_vals = importance["importances"][:3]
        insight_text = f"""
**Top 3 Engagement Drivers:**

1. **{top_3[0]}** — accounts for **{top_3_vals[0]:.1f}%** of prediction power
2. **{top_3[1]}** — accounts for **{top_3_vals[1]:.1f}%** of prediction power
3. **{top_3[2]}** — accounts for **{top_3_vals[2]:.1f}%** of prediction power

These features combined explain **{sum(top_3_vals):.1f}%** of what makes a post perform well.
"""
        render_info_panel("🧠 Key Insight", insight_text)

        # Feature importance table
        fi_df = pd.DataFrame({
            "Rank": range(1, len(importance["features"]) + 1),
            "Feature": importance["features"],
            "Importance (%)": importance["importances"],
            "Cumulative (%)": [round(sum(importance["importances"][:i+1]), 2)
                               for i in range(len(importance["importances"]))],
        })
        st.dataframe(fi_df, use_container_width=True)

    else:
        st.warning("Not enough data to train the ML model. Need at least 5 posts.")

    # ══════════════════════════════════════════════════════════════════
    # SECTION 3: STATISTICAL SUMMARY
    # ══════════════════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)
    render_section_header("📈", "Statistical Summary")

    numeric_cols = ["Likes", "Retweets", "Replies", "Views", "Saves",
                    "EngagementScore", "EngagementRate", "ViralScore", "QualityScore"]
    available_stats = [c for c in numeric_cols if c in df.columns]

    if available_stats:
        stats = df[available_stats].describe().T
        stats["skew"] = df[available_stats].skew()
        stats["kurtosis"] = df[available_stats].kurtosis()
        stats = stats.round(2)

        # Rename for display using platform labels
        rename_map = {
            "Retweets": cfg["shares_label"],
            "Replies": cfg["comments_label"],
            "Views": cfg["impressions_label"],
        }
        stats = stats.rename(index={k: v for k, v in rename_map.items() if k in stats.index})

        st.dataframe(stats, use_container_width=True)

        # Interpretation panel
        high_skew = [(col, df[col].skew()) for col in available_stats if abs(df[col].skew()) > 1.5]
        if high_skew:
            skew_text = "**Highly skewed features detected** (|skew| > 1.5):\n\n"
            for col, s in high_skew:
                direction = "right-skewed (long tail of high values)" if s > 0 else "left-skewed (long tail of low values)"
                display_col = rename_map.get(col, col)
                skew_text += f"- **{display_col}**: skew = {s:.2f} → {direction}\n"
            skew_text += "\n*High skew means a few posts get extreme values while most stay low. This is typical for viral content.*"
            render_info_panel("📊 Distribution Insight", skew_text)

    # ══════════════════════════════════════════════════════════════════
    # SECTION 4: TIME-SERIES FORECASTING
    # ══════════════════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)
    render_section_header("🔮", "Predictive Forecasting (Holt-Winters)")
    
    st.markdown("""
    <div style="padding:10px 16px;border-radius:8px;background:rgba(59,130,246,0.06);
    border:1px solid rgba(59,130,246,0.12);margin-bottom:16px;">
        <span style="color:#3B82F6;font-weight:600;">Exponential Smoothing</span>
        <span style="color:#848E9C;font-size:0.85rem;margin-left:6px;">
            Analyzes historical engagement trends and seasonality to forecast the next 7 days.
        </span>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("📈 Generating forecast..."):
        forecast_df = forecast_engagement(df, days_to_forecast=7)
    
    if not forecast_df.empty:
        # Create historical dataframe for the chart
        df_hist = df.copy()
        df_hist["Date"] = pd.to_datetime(df_hist["Date"], errors="coerce")
        df_hist = df_hist.dropna(subset=["Date"])
        daily_hist = df_hist.groupby(df_hist["Date"].dt.date)["EngagementScore"].sum().reset_index()
        daily_hist["Date"] = pd.to_datetime(daily_hist["Date"])
        daily_hist = daily_hist.sort_values("Date")
        
        fig = forecast_chart(daily_hist, forecast_df, "7-Day Engagement Forecast")
        st.plotly_chart(fig, use_container_width=True)
        
        # Display forecast table
        col_f1, col_f2 = st.columns([1, 2])
        with col_f1:
            total_pred = forecast_df["Forecast"].sum()
            render_metric_card("🎯", f"{total_pred:,.0f}", "Projected 7-Day Engagement")
        with col_f2:
            display_f = forecast_df.copy()
            display_f["Date"] = display_f["Date"].dt.strftime("%Y-%m-%d")
            display_f["Forecast"] = display_f["Forecast"].round(0).astype(int)
            st.dataframe(display_f.set_index("Date").T, use_container_width=True)
    else:
        st.warning("Not enough historical data spanning multiple days to generate a reliable forecast. Need at least 7 days of data.")

    # ══════════════════════════════════════════════════════════════════
    # SECTION 5: TOPIC MODELING (NLP)
    # ══════════════════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)
    render_section_header("🧠", "Unsupervised Topic Modeling (NMF)")
    
    st.markdown("""
    <div style="padding:10px 16px;border-radius:8px;background:rgba(139,92,246,0.06);
    border:1px solid rgba(139,92,246,0.12);margin-bottom:16px;">
        <span style="color:#8B5CF6;font-weight:600;">TF-IDF + Matrix Factorization</span>
        <span style="color:#848E9C;font-size:0.85rem;margin-left:6px;">
            Automatically discovers latent themes in your content and evaluates which themes drive the most engagement.
        </span>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("🧩 Extracting latent topics..."):
        topics = extract_topics(df, n_topics=4)
        
    if topics:
        cols = st.columns(len(topics))
        for i, t in enumerate(topics):
            with cols[i]:
                st.markdown(f"**Topic #{t['topic_id']}**")
                render_metric_card("🔥", f"{t['avg_engagement']:,.0f}", f"Avg Engagement ({t['post_count']} posts)")
                st.markdown("**Top Keywords:**")
                for kw in t['keywords']:
                    st.markdown(f"- `{kw}`")
    else:
        st.warning("Not enough text data to extract meaningful topics.")


def _strength_label(abs_r: float) -> str:
    """Classify correlation strength."""
    if abs_r >= 0.8:
        return "🔥 Very Strong"
    elif abs_r >= 0.6:
        return "💪 Strong"
    elif abs_r >= 0.4:
        return "📊 Moderate"
    elif abs_r >= 0.2:
        return "📉 Weak"
    else:
        return "⚪ Very Weak"
