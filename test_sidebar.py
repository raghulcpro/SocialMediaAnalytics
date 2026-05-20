"""
Minimal test app to debug sidebar visibility
"""
import streamlit as st

# Page config
st.set_page_config(
    page_title="Test Sidebar",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Test sidebar
with st.sidebar:
    st.write("# ⚡ SIDEBAR TEST")
    st.write("If you can see this, the sidebar is working!")

    st.markdown("---")

    choice = st.radio(
        "Choose a page:",
        ["Home", "About", "Contact"]
    )

    st.write(f"You selected: {choice}")

# Main content
st.write("# Main Content Area")
st.write(f"Sidebar works? Check the LEFT side of the screen!")
st.write(f"Selected: {choice if 'choice' in locals() else 'None'}")
