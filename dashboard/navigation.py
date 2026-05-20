"""
Modern sidebar navigation with dropdowns and categories.
"""
import streamlit as st


def render_modern_nav():
    """Render a modern navigation menu with categories and dropdowns."""

    st.markdown("""
    <style>
    /* Modern Navigation Styles */
    .nav-header {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        padding: 20px 0;
        margin-bottom: 10px;
        border-bottom: 2px solid rgba(252, 213, 53, 0.2);
    }

    .nav-logo {
        font-size: 2.2rem;
        font-weight: 800;
    }

    .nav-title {
        font-size: 1.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FCD535 0%, #F0B90B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .nav-subtitle {
        font-size: 0.65rem;
        color: #B7BDC6;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 600;
    }

    .nav-category {
        margin-top: 20px;
        margin-bottom: 8px;
    }

    .nav-category-label {
        font-size: 0.7rem;
        color: #FCD535;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 800;
        padding: 0 12px;
        display: block;
        margin-bottom: 10px;
    }

    .nav-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 14px;
        margin: 4px 8px;
        border-radius: 8px;
        background: transparent;
        border: 1px solid transparent;
        color: #B7BDC6;
        font-size: 0.9rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .nav-item:hover {
        background: rgba(252, 213, 53, 0.1);
        border-color: rgba(252, 213, 53, 0.2);
        color: #FCD535;
        transform: translateX(4px);
    }

    .nav-item.active {
        background: rgba(252, 213, 53, 0.15);
        border-color: #FCD535;
        border-left: 3px solid #FCD535;
        color: #FCD535;
        font-weight: 700;
        margin-left: 11px;
        padding-left: 11px;
    }

    .nav-icon {
        font-size: 1.3rem;
        min-width: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .nav-divider {
        height: 1px;
        background: rgba(252, 213, 53, 0.1);
        margin: 12px 8px;
    }

    .nav-footer {
        margin-top: 30px;
        padding-top: 15px;
        border-top: 1px solid rgba(252, 213, 53, 0.1);
        text-align: center;
    }

    .nav-footer-text {
        font-size: 0.68rem;
        color: #848E9C;
        line-height: 1.5;
    }

    .badge {
        display: inline-block;
        background: rgba(246, 70, 93, 0.2);
        color: #F6465D;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="nav-header">
        <div class="nav-logo">⚡</div>
        <div>
            <div class="nav-title">SocialPulse</div>
            <div class="nav-subtitle">Intelligence Hub</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation Categories
    nav_items = {
        "CORE": [
            ("🏠", "Overview", "Overview"),
        ],
        "ANALYSIS": [
            ("🧠", "Sentiment Analysis", "Sentiment"),
            ("⚡", "Engagement & Viral", "Engagement"),
            ("👑", "Influencer & Trends", "Influencer"),
        ],
        "AI FEATURES": [
            ("🤖", "AI Recommendations", "Recommendation"),
        ],
        "DATA": [
            ("📄", "Dataset & Export", "Dataset"),
        ],
    }

    selected_page = None

    for category, items in nav_items.items():
        st.markdown(f'<div class="nav-category-label">{category}</div>', unsafe_allow_html=True)

        for icon, label, key in items:
            if st.button(f"{icon}  {label}", key=f"nav_{key}", width="stretch"):
                st.session_state.current_page = key

        st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="nav-footer">
        <div class="nav-footer-text">
            <strong>Built with ❤️</strong><br>
            Python • Streamlit • AI<br>
            © 2026 SocialPulse AI
        </div>
    </div>
    """, unsafe_allow_html=True)

    return st.session_state.get("current_page", "Overview")


# Store selection in session state
if "selected_nav" not in st.session_state:
    st.session_state.selected_nav = "Overview"
