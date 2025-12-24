import streamlit as st
import pydeck as pdk
import pandas as pd

# Handle Streamlit version compatibility for fragments
if hasattr(st, "fragment"):
    fragment = st.fragment
elif hasattr(st, "experimental_fragment"):
    fragment = st.experimental_fragment
else:
    def fragment(func):
        return func

# ============================================================
# DATA TRANSFORMATION & CACHING
# ============================================================

@st.cache_data(show_spinner=False)
def _get_master_dataframe(coastal_data):
    """
    Process raw coastal_data dictionary into a Pandas DataFrame.
    Cached to prevent re-computation on every rerun.
    """
    rows = []

    for region_name, entries in coastal_data.items():
        for e in entries:
            spec = e.get("spec", {})
            
            # --------------------------------------------------------
            # COORDINATE LOOKUP
            # --------------------------------------------------------
            lat = spec.get("Lat") or spec.get("lat")
            lon = spec.get("Lon") or spec.get("lon")
            
            # Fallback coordinates
            if lat is None or lon is None:
                name_clean = spec.get("Name", "").lower()
                if "smith" in name_clean: lat, lon = 41.9, -124.1
                elif "klamath" in name_clean: lat, lon = 41.5, -124.0
                elif "trinity" in name_clean: lat, lon = 41.1, -123.7
                elif "mad" in name_clean: lat, lon = 40.9, -124.0
                elif "eel" in name_clean: lat, lon = 40.5, -124.1
                elif "van duzen" in name_clean: lat, lon = 40.5, -124.0
                elif "mattole" in name_clean: lat, lon = 40.3, -124.3
                elif "navarro" in name_clean: lat, lon = 39.2, -123.7
                elif "garcia" in name_clean: lat, lon = 38.9, -123.7
                elif "gualala" in name_clean: lat, lon = 38.8, -123.5
                elif "russian" in name_clean: lat, lon = 38.4, -123.1
                elif "chetco" in name_clean: lat, lon = 42.0, -124.2
                elif "rogue" in name_clean: lat, lon = 42.4, -124.4
                elif "elk" in name_clean: lat, lon = 42.7, -124.5
                elif "sixes" in name_clean: lat, lon = 42.8, -124.5
                elif "coquille" in name_clean: lat, lon = 43.1, -124.4
                elif "coos" in name_clean: lat, lon = 43.3, -124.2
                elif "umpqua" in name_clean: lat, lon = 43.7, -124.1
                elif "siuslaw" in name_clean: lat, lon = 44.0, -124.1
                elif "alsea" in name_clean: lat, lon = 44.4, -124.0
                elif "yaquina" in name_clean: lat, lon = 44.6, -124.0
                elif "siletz" in name_clean: lat, lon = 44.9, -124.0
                elif "nestucca" in name_clean: lat, lon = 45.2, -123.9
                elif "trask" in name_clean: lat, lon = 45.4, -123.8
                elif "wilson" in name_clean: lat, lon = 45.5, -123.8
                elif "kilchis" in name_clean: lat, lon = 45.5, -123.8
                elif "nehalem" in name_clean: lat, lon = 45.7, -123.9
                elif "bogachiel" in name_clean: lat, lon = 47.9, -124.5
                elif "calawah" in name_clean: lat, lon = 47.9, -124.4
                elif "sol duc" in name_clean: lat, lon = 48.0, -124.5
                elif "hoh" in name_clean: lat, lon = 47.8, -124.2
                elif "queets" in name_clean: lat, lon = 47.5, -124.3
                elif "quinault" in name_clean: lat, lon = 47.3, -124.2
                elif "humptulips" in name_clean: lat, lon = 47.2, -124.0
                elif "chehalis" in name_clean: lat, lon = 46.9, -123.8
                elif "satsop" in name_clean: lat, lon = 47.0, -123.5
                elif "wynoochee" in name_clean: lat, lon = 47.0, -123.6
                elif "willapa" in name_clean: lat, lon = 46.7, -123.8
                elif "naselle" in name_clean: lat, lon = 46.4, -123.8
                else: continue # Skip if no coords found

            # --------------------------------------------------------
            # EXTRACT DATA
            # --------------------------------------------------------
            name = spec.get("Name", "Unknown")
            score = e.get("score", 0.0)
            cond_text = e.get("cond_text", "no data")
            trend_text = e.get("trend_text", "")
            arrow = e.get("arrow", "")
            pct_change = e.get("pct_change")
            last_val = e.get("last_val")
            time_str = e.get("time_str", "")
            cond_color = e.get("cond_color", "#CCCCCC")
            
            window_status = e.get("window", "—")
            storm_cycle_raw = e.get("storm_cycle", ("Unknown", "❔", "#E0E0E0"))
            if isinstance(storm_cycle_raw, tuple) and len(storm_cycle_raw) == 3:
                storm_label, storm_emoji, storm_color = storm_cycle_raw
            else:
                storm_label, storm_emoji, storm_color = "Unknown", "❔", "#E0E0E0"

            source = e.get("source", "none")
            confidence = e.get("confidence", "none")
            hydro_insight = e.get("hydro_insight", "")

            # --------------------------------------------------------
            # CALCULATE SCORES
            # --------------------------------------------------------
            if last_val is not None and source != "none" and confidence != "none":
                confidence_level = "high"
                confidence_score = 1.0
            elif source != "none" or confidence != "none":
                confidence_level = "medium"
                confidence_score = 0.5
            else:
                confidence_level = "low"
                confidence_score = 0.2

            ws = str(window_status).lower()
            if "open" in ws: window_score = 1.0
            elif "soon" in ws or "opening" in ws or "pending" in ws: window_score = 0.7
            elif "closed" in ws or "no window" in ws: window_score = 0.1
            else: window_score = 0.4

            sl = str(storm_label).lower()
            if "rising" in sl: storm_score = 0.8
            elif "peak" in sl: storm_score = 1.0
            elif "drop" in sl or "recession" in sl: storm_score = 0.5
            elif "post" in sl: storm_score = 0.3
            else: storm_score = 0.4

            cond = cond_text.lower()
            if cond == "in shape": cond_score = 1.0
            elif cond == "low": cond_score = 0.7
            elif cond == "slightly high": cond_score = 0.5
            elif cond == "blown out": cond_score = 0.1
            elif cond in ["no data", "below legal", "too low"]: cond_score = 0.2
            else: cond_score = 0.4

            # --------------------------------------------------------
            # TOOLTIP CONSTRUCTION (HTML)
            # --------------------------------------------------------
            pct_str = f"{pct_change:+.1f}%" if pct_change is not None else "—"
            flow_str = f"{last_val:.0f}" if last_val is not None else "—"

            # Added HTML bolding and line breaks
            tooltip = (
                f"<b>{name}</b> <span style='color:#ccc; font-size:0.9em;'>({region_name})</span><br/>"
                f"<b>Status:</b> {cond_text}<br/>"
                f"<b>Flow/Stage:</b> {flow_str}<br/>"
                f"<b>Trend:</b> {arrow} {pct_str} • {trend_text}<br/>"
                f"<b>Storm:</b> {storm_emoji} {storm_label}<br/>"
                f"<b>Window:</b> {window_status}<br/>"
                f"<b>Confidence:</b> {confidence_level}<br/>"
                f"<b>Updated:</b> {time_str}<br/>"
                f"<div style='margin-top:4px; font-style:italic;'>{hydro_insight}</div>"
            )

            rows.append({
                "name": name,
                "region": region_name,
                "lat": float(lat),
                "lon": float(lon),
                "score": float(score),
                "cond_text": cond_text,
                "cond_color": cond_color,
                "cond_score": cond_score,
                "trend_text": trend_text,
                "arrow": arrow,
                "pct_change": pct_change,
                "last_val": last_val,
                "time_str": time_str,
                "window_status": window_status,
                "window_score": window_score,
                "storm_label": storm_label,
                "storm_emoji": storm_emoji,
                "storm_color": storm_color,
                "storm_score": storm_score,
                "source": source,
                "confidence": confidence,
                "confidence_level": confidence_level,
                "confidence_score": confidence_score,
                "hydro_insight": hydro_insight,
                "tooltip": tooltip,
            })

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)


def _apply_filters_to_df(df, filters):
    """
    Fast boolean masking instead of row iteration.
    """
    if df.empty:
        return df

    mask_cond = pd.Series(False, index=df.index)
    if filters.get("in_shape", True): mask_cond |= (df["cond_text"] == "in shape")
    if filters.get("low", True): mask_cond |= (df["cond_text"] == "low")
    if filters.get("slightly_high", True): mask_cond |= (df["cond_text"] == "slightly high")
    if filters.get("blown_out", True): mask_cond |= (df["cond_text"] == "blown out")
    if filters.get("below_legal", True): mask_cond |= (df["cond_text"] == "below legal")
    if filters.get("low", True): mask_cond |= (df["cond_text"] == "too low")
    if filters.get("no_data", True): mask_cond |= (df["cond_text"] == "no data")

    mask_trend = pd.Series(False, index=df.index)
    if filters.get("rising", True): mask_trend |= df["trend_text"].str.contains("↑", na=False)
    if filters.get("dropping", True): mask_trend |= df["trend_text"].str.contains("↓", na=False)
    if filters.get("stable", True): mask_trend |= df["trend_text"].str.contains("↔", na=False)

    return df[mask_cond & mask_trend]


# ============================================================
# PYDECK LAYER BUILDERS
# ============================================================

def _build_marker_layer(df, show_estimated=True):
    if df.empty: return None
    
    if not show_estimated:
        df = df[df["confidence_level"] == "high"]

    def hex_to_rgb(h):
        h = h.lstrip('#')
        return [int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)]

    layer_df = df.copy()
    layer_df['color_rgb'] = layer_df['cond_color'].apply(hex_to_rgb)
    
    s_min, s_max = 4, 18
    sc_min, sc_max = layer_df['score'].min(), layer_df['score'].max()
    if sc_max == sc_min: sc_max += 1
    
    layer_df['size'] = layer_df['score'].apply(
        lambda s: s_min + (s_max - s_min) * ((s - sc_min) / (sc_max - sc_min))
    )

    return pdk.Layer(
        "ScatterplotLayer",
        data=layer_df,
        get_position=["lon", "lat"],
        get_radius="size * 2000",
        get_fill_color="color_rgb",
        pickable=True,
        opacity=0.8,
        stroked=True,
        get_line_color=[0, 0, 0],
        get_line_width=100,
    )


def _build_heatmap_layer(df, mode, show_estimated=True):
    if df.empty: return None

    if not show_estimated:
        df = df[df["confidence_level"] == "high"]

    layer_df = df.copy()

    col_map = {
        "Score": "score",
        "Window": "window_score",
        "Confidence": "confidence_score",
        "Storm-cycle": "storm_score"
    }
    col = col_map.get(mode, "score")
    
    layer_df["weight"] = layer_df[col]

    return pdk.Layer(
        "HeatmapLayer",
        data=layer_df,
        get_position=["lon", "lat"],
        get_weight="weight",
        radius_pixels=80,
        intensity=1,
        threshold=0.05,
    )


def _compute_initial_view(df):
    if df.empty:
        return pdk.ViewState(latitude=44.0, longitude=-124.0, zoom=5, pitch=0)

    lat_center = df["lat"].mean()
    lon_center = df["lon"].mean()

    return pdk.ViewState(
        latitude=float(lat_center),
        longitude=float(lon_center),
        zoom=6,
        pitch=0,
    )


def _render_legend():
    st.markdown(
        """
        <div style="font-size:0.80rem; line-height:1.4; margin-bottom:8px;">
            <b>Legend</b><br>
            <span style="color:#C8E6C9;">●</span> In shape &nbsp;
            <span style="color:#FFEB3B;">●</span> Low &nbsp;
            <span style="color:#FFCC80;">●</span> Slightly high &nbsp;
            <span style="color:#FFCDD2;">●</span> Blown out &nbsp;
            <span style="color:#E0E0E0;">●</span> No data<br>
            📡 Measured &nbsp; 📏 Stage-only &nbsp; 🧪 Estimated &nbsp; 🕒 Stale
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MAIN ENTRY POINT
# ============================================================

@fragment
def render_coastal_map(coastal_data, filters):
    st.subheader("🗺️ Coastal Map View")

    master_df = _get_master_dataframe(coastal_data)

    if master_df.empty:
        st.warning("No map data available.")
        return

    df = _apply_filters_to_df(master_df, filters)

    if df.empty:
        st.info("No rivers match the current filters.")
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1: show_markers = st.checkbox("Show markers", True, key="map_mark")
    with c2: show_heatmap = st.checkbox("Show heat map", False, key="map_heat")
    with c3: show_estimated = st.checkbox("Include estimated", True, key="map_est")
    with c4: heat_mode = st.selectbox("Heat map mode", ["Score", "Window", "Confidence", "Storm-cycle"], key="map_mode")

    _render_legend()

    layers = []
    
    if show_heatmap:
        l = _build_heatmap_layer(df, heat_mode, show_estimated)
        if l: layers.append(l)
        
    if show_markers:
        l = _build_marker_layer(df, show_estimated)
        if l: layers.append(l)

    if not layers:
        st.write("Enable markers and/or heat map to see data.")
        return

    lat_mean = df["lat"].mean()
    lon_mean = df["lon"].mean()
    view_state = pdk.ViewState(latitude=lat_mean, longitude=lon_mean, zoom=6, pitch=0)

    # UPDATED TOOLTIP STYLE + MAP DIMENSIONS
    deck = pdk.Deck(
        map_style=pdk.map_styles.CARTO_LIGHT,  
        initial_view_state=view_state,
        layers=layers,
        tooltip={
            "html": "{tooltip}",
            "style": {
                "backgroundColor": "rgba(0, 0, 0, 0.85)",
                "color": "white",
                "fontSize": "13px",
                "padding": "10px",
                "borderRadius": "4px",
                "zIndex": "1000",
                "maxWidth": "250px", # Force wrap
                "whiteSpace": "normal",
                "lineHeight": "1.4"
            }
        },
    )
    
    # Restrict width using columns and increase height
    _, map_col, _ = st.columns([1, 6, 1])
    with map_col:
        st.pydeck_chart(deck, height=750)