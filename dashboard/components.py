"""
Reusable premium HTML components for the dashboard.
"""
import streamlit as st


def render_hero():
    st.markdown("""
    <div class="hero-header">
        <h1>⚡ SocialPulse AI</h1>
        <p class="hero-subtitle">AI-Powered Social Media Intelligence Terminal</p>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(icon, value, label, delta=None, delta_dir="up"):
    delta_html = ""
    if delta:
        cls = "delta-up" if delta_dir == "up" else "delta-down"
        arrow = "▲" if delta_dir == "up" else "▼"
        delta_html = f'<div class="metric-delta {cls}">{arrow} {delta}</div>'
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_section_header(icon, title):
    st.markdown(f"""
    <div class="section-header">
        <span class="icon">{icon}</span>
        <span class="title">{title}</span>
    </div>
    """, unsafe_allow_html=True)


def render_recommendation_card(rec):
    pcls = f"priority-{rec['priority']}"
    st.markdown(f"""
    <div class="rec-card">
        <div class="rec-icon">{rec['icon']}</div>
        <div class="rec-title">{rec['title']}</div>
        <div class="rec-desc">{rec['description']}</div>
        <span class="rec-priority {pcls}">{rec['priority']}</span>
    </div>
    """, unsafe_allow_html=True)


def render_info_panel(title, text):
    st.markdown(f"""
    <div class="info-panel">
        <h4>{title}</h4>
        <p>{text}</p>
    </div>
    """, unsafe_allow_html=True)


def render_ticker(items):
    """items: list of dicts with keys: label, value, direction (up/down/neutral)"""
    parts = []
    for item in items:
        cls = item.get("direction", "neutral")
        vcls = "up" if cls == "up" else ("down" if cls == "down" else "")
        parts.append(
            f'<span class="ticker-item">{item["label"]}: '
            f'<span class="value {vcls}">{item["value"]}</span></span>'
        )
    inner = " │ ".join(parts)
    st.markdown(f'<div class="ticker-bar">{inner}</div>', unsafe_allow_html=True)


def render_score_badge(score):
    if score >= 70:
        cls = "score-excellent"
    elif score >= 40:
        cls = "score-good"
    else:
        cls = "score-poor"
    st.markdown(f"""
    <div style="text-align:center;margin:20px 0;">
        <div class="score-badge {cls}">{score}</div>
    </div>
    """, unsafe_allow_html=True)
