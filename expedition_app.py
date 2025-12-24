import streamlit as st

# Import your modules
# Assuming planner_app.py exists or is placeholder
try:
    from planner_app import render_planner
except ImportError:
    def render_planner():
        st.info("Trip Planner module not found.")

# Import dashboard app (dashboard.py)
try:
    from dashboard_app import render_coastal_dashboard, get_dashboard_context
except ImportError:
    # Fallback if dashboard.py is named differently (e.g. dashboard.py vs dashboard_app.py)
    # Adjust import based on your actual filename. Assuming 'dashboard' based on context.
    from dashboard import render_coastal_dashboard, get_dashboard_context

# Import map module
from coastal_map import render_coastal_map

st.set_page_config(
    layout="wide",
    page_title="Expedition App",
)

# --- HOMEPAGE STATE ---
if "page" not in st.session_state:
    st.session_state.page = "home"


# --- HOMEPAGE ---
def render_homepage():
    st.title("🧭 Expedition App")
    st.subheader("Choose a module to begin")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🗺️ Trip Planner")
        st.markdown(
            "Plan multi‑day fishing trips with scoring, routing, and region logic."
        )
        if st.button("Open Trip Planner"):
            st.session_state.page = "planner"

    with col2:
        st.markdown("### 🌊 Coastal Dashboard")
        st.markdown(
            "Live river conditions, storm‑cycle analysis, and hydrology insights."
        )
        if st.button("Open Coastal Dashboard"):
            st.session_state.page = "dashboard"

    with col3:
        st.markdown("### 🗺️ Map View")
        st.markdown(
            "Interactive coastal map with markers, heat maps, and tooltips."
        )
        if st.button("Open Map"):
            st.session_state.page = "map"


# --- ROUTING LOGIC ---
if st.session_state.page == "home":
    render_homepage()

elif st.session_state.page == "planner":
    st.button("← Back to Home", on_click=lambda: st.session_state.update(page="home"))
    render_planner()

elif st.session_state.page == "dashboard":
    st.button("← Back to Home", on_click=lambda: st.session_state.update(page="home"))
    render_coastal_dashboard()

elif st.session_state.page == "map":
    st.button("← Back to Home", on_click=lambda: st.session_state.update(page="home"))
    
    # Fetch data context
    coastal_data, default_filters = get_dashboard_context()
    
    # We can use default filters or add sidebar filters here specifically for the map
    # For now, we pass the data to the map renderer
    render_coastal_map(coastal_data, default_filters)