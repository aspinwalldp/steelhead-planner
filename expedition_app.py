import streamlit as st
import pandas as pd
import datetime
import requests
from datetime import timedelta
import re
import math

# Optional: yfinance for live oil prices
try:
    import yfinance as yf
except ImportError:
    yf = None

# --- CONFIGURATION ---
st.set_page_config(page_title="Steelhead Navigator", layout="wide", page_icon="🧭")

# Reset logic
if 'reset_id' not in st.session_state:
    st.session_state.reset_id = 0

def trigger_reset():
    st.session_state.reset_id += 1
    st.experimental_rerun()

# ===== 1. DATA & METADATA =====

RIVER_SPECS = {
    "NorCal": [
        {
            "Name": "Smith River (CA)",
            "ID": "11532500",
            "T": "1200-8000 cfs",
            "Low": 600,
            "P": "00060",
            "N": "Holy Grail. Closed < 600 cfs.",
            "Closed": False,
            "Restriction": "",
            "Lat": 41.78983661888987,
            "Lon": -124.08491018355784
        },
        {
            "Name": "Eel (Main)",
            "ID": "11477000",
            "T": "1500-4500 cfs",
            "Low": 350,
            "P": "00060",
            "N": "Scotia Gauge. Closed < 350 cfs.",
            "Closed": False,
            "Restriction": "",
            "Lat": 40.44310024552732,
            "Lon": -123.9862593123425
        },
        {
            "Name": "SF Eel",
            "ID": "11476500",
            "T": "340-1800 cfs",
            "Low": 340,
            "P": "00060",
            "N": "Clears fast. Closed < 340 cfs.",
            "Closed": False,
            "Restriction": "",
            "Lat": 40.27894822555081,
            "Lon": -123.86371952859773
        },
        {
            "Name": "Van Duzen",
            "ID": "11478500",
            "T": "150-1200 cfs",
            "Low": 150,
            "P": "00060",
            "N": "Dirty Van. Closed < 150 cfs.",
            "Closed": False,
            "Restriction": "",
            "Lat": 40.476167136759635,
            "Lon": -123.93600786480076
        }
    ],

    "Oregon": [
        {
            "Name": "Chetco",
            "ID": "14400000",
            "T": "1000-4000 cfs",
            "Low": 800,
            "P": "00060",
            "N": "Magic window. Bobber rules often low water.",
            "Closed": False,
            "Restriction": "",
            "Lat": 42.08,
            "Lon": -124.22
        },
        {
            "Name": "Elk River",
            "ID": "14338000",
            "T": "3.5-5.5 ft",
            "Low": 3.0,
            "P": "00065",
            "N": "Tiny system. Clears fast.",
            "Closed": False,
            "Restriction": "",
            "Lat": 42.75,
            "Lon": -124.48
        },
        {
            "Name": "Sixes River",
            "ID": "14327150",
            "T": "4.0-7.0 ft",
            "Low": 3.5,
            "P": "00065",
            "N": "Dark tannin.",
            "Closed": False,
            "Restriction": "",
            "Lat": 42.84,
            "Lon": -124.45
        },
        {
            "Name": "Rogue",
            "ID": "14372300",
            "T": "2000-6000 cfs",
            "Low": 1200,
            "P": "00060",
            "N": "Agness Gauge. Big water.",
            "Closed": False,
            "Restriction": "",
            "Lat": 42.42,
            "Lon": -124.41
        },
        {
            "Name": "N. Umpqua",
            "ID": "14319500",
            "T": "1500-4000 cfs",
            "Low": 1000,
            "P": "00060",
            "N": "Fly Only. Technical.",
            "Closed": False,
            "Restriction": "",
            "Lat": 43.34,
            "Lon": -122.73
        },
        {
            "Name": "Umpqua (Main)",
            "ID": "14321000",
            "T": "4000-10000 cfs",
            "Low": 3000,
            "P": "00060",
            "N": "Swinging water.",
            "Closed": False,
            "Restriction": "",
            "Lat": 43.68,
            "Lon": -124.10
        }
    ],

    "OP": [
        {
            "Name": "Bogachiel",
            "ID": "12043000",
            "T": "500-2500 cfs",
            "Low": 150,
            "P": "00060",
            "N": "Crowded but reliable.",
            "Lat": 47.93,
            "Lon": -124.45
        },
        {
            "Name": "Calawah",
            "ID": "12043300",
            "T": "300-1500 cfs",
            "Low": 150,
            "P": "00060",
            "N": "Steep and fast.",
            "Lat": 47.96,
            "Lon": -124.39
        },
        {
            "Name": "Hoh",
            "ID": "12041200",
            "T": "1000-4000 cfs",
            "Low": 600,
            "P": "00060",
            "N": "Glacial grey.",
            "Lat": 47.86,
            "Lon": -124.25
        },
        {
            "Name": "Queets",
            "ID": "12040500",
            "T": "2000-7000 cfs",
            "Low": 1200,
            "P": "00060",
            "N": "Wild and remote.",
            "Lat": 47.53,
            "Lon": -124.33
        }
    ]
}
RIVER_PRIORITY = {
    "NorCal": ["Smith River (CA)", "SF Eel", "Van Duzen", "Eel (Main)"],
    "Oregon": ["Chetco", "Elk River", "Sixes River", "N. Umpqua", "Rogue", "Umpqua (Main)"],
    "OP": ["Bogachiel", "Calawah", "Hoh", "Queets"],
    "Pyramid": ["Pyramid"],
}

RIVER_TO_NODE = {
    "Smith River (CA)": "Hiouchi",
    "Eel (Main)": "Pepperwood",
    "SF Eel": "Pepperwood",
    "Van Duzen": "Maple Grove",
    "Chetco": "Brookings",
    "Elk River": "Port Orford",
    "Sixes River": "Port Orford",
    "Rogue": "Gold Beach",
    "N. Umpqua": "Steamboat",
    "Umpqua (Main)": "Reedsport",
    "Bogachiel": "Forks",
    "Calawah": "Forks",
    "Hoh": "Hoh",
    "Queets": "Queets",
    "Pyramid": "Pyramid",
}

NODE_COORDS = {
    "Home": (40.76, -111.89),  # SLC-ish
    "Pyramid": (39.95, -119.60),
    "Pepperwood": (40.48, -124.03),
    "Maple Grove": (40.52, -123.90),
    "Hiouchi": (41.79, -124.07),
    "Eureka": (40.80, -124.16),
    "Brookings": (42.05, -124.27),
    "Gold Beach": (42.40, -124.42),
    "Port Orford": (42.74, -124.49),
    "Coos Bay": (43.36, -124.21),
    "Reedsport": (43.70, -124.09),
    "Steamboat": (43.34, -122.73),
    "Forks": (47.95, -124.38),
    "Bogachiel": (47.93, -124.45),
    "Hoh": (47.86, -124.25),
    "Queets": (47.53, -124.33),
    "Eagle": (40.55, -120.80),   # Eagle Lake, CA - south shore access
}

BASE_GAS_PRICES = {
    "Home": 2.99,
    "Pyramid": 4.25,
    "Pepperwood": 4.79,
    "Maple Grove": 4.79,
    "Hiouchi": 4.85,
    "Eureka": 4.79,
    "Brookings": 3.69,
    "Gold Beach": 3.89,
    "Port Orford": 3.99,
    "Coos Bay": 3.59,
    "Reedsport": 3.69,
    "Steamboat": 4.50,
    "Forks": 4.39,
    "Bogachiel": 4.39,
    "Hoh": 4.45,
    "Queets": 4.50,
    "Eagle": 4.10,
}

RIVER_TYPE = {
    "Smith River (CA)": "flashy",
    "Chetco": "flashy",
    "Van Duzen": "flashy",
    "SF Eel": "flashy",
    "Eel (Main)": "big",
    "Rogue": "big",
    "N. Umpqua": "big",
    "Umpqua (Main)": "big",
    "Bogachiel": "flashy",
    "Calawah": "flashy",
    "Hoh": "glacial",
    "Queets": "glacial"
}

# South -> North for modeled rivers.
REGION_RIVER_ORDER = {
    "NorCal": [
        "Eel (Main)",
        "SF Eel",
        "Van Duzen",
        "Smith River (CA)"
    ],
    "Oregon": [
        "Chetco",
        "Elk River",
        "Sixes River",
        "Rogue",
        "Umpqua (Main)",
        "N. Umpqua"
    ]
}

# ===== 2. LIVE INTEL & SCORING =====

@st.cache_data(ttl=600)
def get_usgs_series(site_id, param_code='00060', days=3):
    """Fetch recent USGS flow data."""
    try:
        url = (
            "https://waterservices.usgs.gov/nwis/iv/"
            f"?format=json&sites={site_id}&parameterCd={param_code}&period=P{days}D"
        )
        r = requests.get(url, timeout=6).json()
        ts_list = r.get('value', {}).get('timeSeries', [])
        if not ts_list:
            return []
        ts = ts_list[0]
        vals = ts.get('values', [])[0].get('value', [])
        out = []
        for v in vals:
            try:
                dt = datetime.datetime.fromisoformat(
                    v['dateTime'].replace("Z", "+00:00")
                )
                val = float(v['value'])
                if val >= 0:
                    out.append((dt, val))
            except:
                continue
        return out
    except:
        return []

@st.cache_data(ttl=600)
def get_oil_price():
    """Fetch WTI crude price for gas adjustment."""
    if yf:
        try:
            return yf.Ticker("CL=F").history(period="5d")['Close'].iloc[-1]
        except:
            pass
    return 70.0

@st.cache_data(ttl=3600)
def get_nws_forecast_data(lat, lon):
    """Fetch NOAA weather forecast periods."""
    try:
        h = {"User-Agent": "(steelhead-navigator)"}
        r = requests.get(
            f"https://api.weather.gov/points/{round(lat,4)},{round(lon,4)}",
            headers=h,
            timeout=6
        ).json()
        return requests.get(
            r['properties']['forecast'],
            headers=h,
            timeout=6
        ).json()['properties']['periods']
    except:
        return None

def parse_target_range(target_str):
    """Parse 'low-high units' into floats."""
    try:
        parts = target_str.split('-')
        low = float(parts[0])
        high = float(parts[1].split()[0])
        return low, high
    except:
        return None, None

def compute_flow_index(value, low_limit, target_low, target_high):
    """Convert flow into a normalized 0–1 index."""
    if value < low_limit:
        return 0.0
    if target_low is None or target_high is None or target_low <= 0 or target_high <= 0:
        return 0.6
    if value < target_low:
        frac = (value - low_limit) / (target_low - low_limit) if target_low != low_limit else 0
        return 0.2 + 0.4 * max(0.0, min(frac, 1.0))
    if target_low <= value <= target_high:
        return 1.0
    if value > target_high and value <= 2 * target_high:
        frac = (2 * target_high - value) / target_high
        return 0.8 * max(0.0, min(frac, 1.0))
    return 0.0

def compute_trend_bonus(series):
    """Reward falling flows, penalize rising flows."""
    if len(series) < 2:
        return 0.0
    series = sorted(series, key=lambda x: x[0])
    last = series[-1][1]
    prev = series[-2][1]
    dt_hours = (series[-1][0] - series[-2][0]).total_seconds() / 3600 or 1
    rate = (last - prev) / dt_hours
    if rate <= -200:
        return 0.5
    if -200 < rate <= -50:
        return 0.25
    if 50 <= rate < 200:
        return -0.25
    if rate >= 200:
        return -0.5
    return 0.0

def estimate_precip_for_river(river_name):
    """Estimate precipitation impact based on NOAA text."""
    if "Eel" in river_name or "Van Duzen" in river_name:
        lat, lon = 40.80, -124.16
    elif "Smith" in river_name:
        lat, lon = 41.75, -124.20
    elif river_name in ["Chetco", "Elk River", "Sixes River", "Rogue"]:
        lat, lon = 42.05, -124.27
    elif river_name in ["N. Umpqua", "Umpqua (Main)"]:
        lat, lon = 43.36, -124.21
    elif river_name in ["Bogachiel", "Calawah", "Hoh", "Queets"]:
        lat, lon = 47.95, -124.38
    else:
        return 0.0

    periods = get_nws_forecast_data(lat, lon)
    if not periods:
        return 0.0

    txt = periods[0]["detailedForecast"].lower()

    if "heavy rain" in txt or "1 inch" in txt or "one inch" in txt:
        return -1.0
    if "between half and three quarters" in txt:
        return -0.75
    if "between a quarter and half" in txt:
        return -0.25
    if "a quarter of an inch" in txt:
        return 0.0
    if "light rain" in txt or "showers" in txt:
        return 0.0
    if "dry" in txt or "mostly clear" in txt:
        return 0.5

    return 0.0

def river_type_bonus(river_name, index):
    """Adjust score based on river type behavior."""
    rtype = RIVER_TYPE.get(river_name, "generic")
    if rtype == "flashy":
        if 0.4 <= index <= 0.8:
            return 0.5
        if index < 0.2 or index > 0.9:
            return -0.5
    elif rtype == "big":
        if 0.3 <= index <= 0.6:
            return 0.5
        if index < 0.2 or index > 0.8:
            return -0.5
    elif rtype == "glacial":
        if 0.4 <= index <= 0.7:
            return 0.5
        if index < 0.3 or index > 0.85:
            return -0.5
    return 0.0

def auto_score_river(river_name, spec):
    """Compute the auto-score for a river."""
    # Hard closure override
    if spec.get("Closed", False):
        return {
            "total": 0.0,
            "flow": 0.0,
            "trend": 0.0,
            "weather": 0.0,
            "base": 0.0
        }

    site_id = spec["ID"]
    param = spec.get("P", "00060")
    low_limit = spec.get("Low", 0.0)
    t_low, t_high = parse_target_range(spec["T"])

    series = get_usgs_series(site_id, param)
    if not series:
        # fallback: total=2.5, components unknown → set to 0
        return {
            "total": 2.5,
            "flow": 0.0,
            "trend": 0.0,
            "weather": 0.0,
            "base": 0.0
        }

    last_val = series[-1][1]
    if last_val < low_limit:
        return {
            "total": 0.0,
            "flow": 0.0,
            "trend": 0.0,
            "weather": 0.0,
            "base": 0.0
        }

    flow_idx = compute_flow_index(last_val, low_limit, t_low, t_high)
    trend_bonus = compute_trend_bonus(series)
    precip_bonus = estimate_precip_for_river(river_name)
    type_bonus = river_type_bonus(river_name, flow_idx)

    raw_score = 5.0 * flow_idx + trend_bonus + precip_bonus + type_bonus
    total = max(0.0, min(raw_score, 5.0))

    return {
        "total": total,
        "flow": flow_idx * 5.0,
        "trend": trend_bonus,
        "weather": precip_bonus,
        "base": type_bonus
    }

# ===== 3. SIDEBAR =====

st.title("Steelhead Trip Planner 🧭")

def explain_river_score(region, river_name, score_components):
    """Return the real scoring breakdown from auto_score_river."""
    return score_components.get(river_name, {
        "flow": 0.0,
        "trend": 0.0,
        "weather": 0.0,
        "base": 0.0,
        "total": 0.0
    })

with st.sidebar:
    st.header("🎛️ Mission Controls")

    # --- Timeline ---
    with st.expander("📅 Timeline", expanded=False):
        start_date = st.date_input(
            "Departure",
            datetime.date(2026, 1, 1),
            key=f"date_start_{st.session_state.reset_id}"
        )
        end_date = st.date_input(
            "Return By",
            datetime.date(2026, 1, 17),
            key=f"date_end_{st.session_state.reset_id}"
        )
        total_trip_days = (end_date - start_date).days + 1
        if total_trip_days < 1:
            total_trip_days = 1
        st.caption(f"Trip Duration: {total_trip_days} Days")

    # --- Ratings ---
    ratings = {}
    score_components = {}

    with st.expander("🌊 River Ratings", expanded=True):
        st.caption("Auto-scored from flows, trends, and forecast.")

        # Pyramid manual slider
        ratings["Pyramid"] = st.slider(
            "Pyramid (manual)",
            0.0, 5.0,
            3.5,
            0.25,
            key=f"Pyramid_{st.session_state.reset_id}"
        )

        # Regional rivers
        for region, rivers in RIVER_SPECS.items():
            st.markdown(f"**{region}**")

            for r in rivers:
                name = r["Name"]
                closed = r.get("Closed", False)

                # Full score dict
                score = auto_score_river(name, r)
                auto_total = score["total"]
                score_components[name] = score

                # Base label
                label = name.split('(')[0].strip()

                # Regulatory closure
                if closed:
                    label += " [CLOSED]"
                    auto_total = 0.0

                # Flow-closed indicator
                if not closed and auto_total <= 0.01:
                    label += " (⛔)"

                # Slider default
                default_val = float(round(auto_total * 4) / 4.0)

                ratings[name] = st.slider(
                    label,
                    0.0,
                    5.0,
                    default_val,
                    0.25,
                    key=f"{name}_{st.session_state.reset_id}"
                )

                # Tiny scoring breakdown
                breakdown = explain_river_score(region, name, score_components)
                st.markdown(
                    f"<div style='font-size: 9px; line-height: 1.1; "
                    f"margin-top: -6px; margin-bottom: 2px;'>"
                    f"Flow: {breakdown['flow']:.1f} | "
                    f"Trend: {breakdown['trend']:.1f} | "
                    f"Base: {breakdown['base']:.1f} | "
                    f"Total: {breakdown['total']:.2f}"
                    f"</span>",
                    unsafe_allow_html=True
                )

    # --- Logistics ---
    with st.expander("⚙️ Logistics", expanded=False):
        mpg = st.number_input(
            "MPG",
            5.0,
            40.0,
            23.5,
            0.1,
            key=f"mpg_{st.session_state.reset_id}"
        )
        tank = st.number_input(
            "Range (miles per tank)",
            200,
            600,
            400,
            key=f"tank_{st.session_state.reset_id}"
        )
        live_wti = get_oil_price()
        st.metric("Live WTI", f"${live_wti:.2f}")
        oil_factor = live_wti / 70.0
        oil_adj_slider = st.slider(
            "Gas Price Adjustment",
            -0.5,
            0.5,
            0.0,
            0.05,
            key=f"oil_adj_{st.session_state.reset_id}"
        )
        NODES = {
            loc: {"gas": BASE_GAS_PRICES[loc] * oil_factor + oil_adj_slider}
            for loc in BASE_GAS_PRICES
        }

    # --- Veto options ---
    with st.expander("Veto Options", expanded=False):
        v_pyr = st.checkbox("Veto Pyramid", key=f"v_pyr_{st.session_state.reset_id}")
        v_norcal = st.checkbox("Veto NorCal", key=f"v_norcal_{st.session_state.reset_id}")
        v_ore = st.checkbox("Veto Oregon", key=f"v_ore_{st.session_state.reset_id}")
        v_op = st.checkbox("Veto OP", key=f"v_op_{st.session_state.reset_id}")
        vetoes = {"Pyramid": v_pyr, "NorCal": v_norcal, "Oregon": v_ore, "OP": v_op}

    st.button("Reset Planner", on_click=trigger_reset)

    st.divider()
    st.markdown("### 🔗 Quick Links")
    st.markdown(
        """
* **NorCal:** [Fishing the North Coast](https://fishingthenorthcoast.com/) | [The Fly Shop](https://www.theflyshop.com/stream-report) | [NOAA River Forecast](https://www.cnrfc.noaa.gov/)
* **Pyramid:** [Pyramid Fly Co](https://pyramidflyco.com/fishing-report/) | [Windy.com](https://www.windy.com/39.950/-119.600)
* **Oregon:** [NOAA NW River Forecast](https://www.nwrfc.noaa.gov/rfc/) | [Ashland Fly Shop](https://www.ashlandflyshop.com/blogs/fishing-reports)
* **OP:** [Waters West](https://waterswest.com/fishing-report/)
"""
    )

# ===== 4. REGION SCORING, ORDERING, AND ALLOCATION =====

def get_rivers_sorted(region, ratings, vetoes):
    """
    Returns a list of rivers in a region, sorted by rating, excluding:
      - Closed rivers
      - Region-level vetoes
      - Rivers with zero or negative ratings
    """
    if vetoes.get(region, False):
        return []

    candidates = RIVER_PRIORITY.get(region, [])
    scored = []

    for r in candidates:
        # Find spec
        spec = None
        for rv in RIVER_SPECS.get(region, []):
            if rv["Name"] == r:
                spec = rv
                break

        # Skip regulatory closures
        if spec and spec.get("Closed", False):
            continue

        s = float(ratings.get(r, 0.0))
        if s > 0:
            scored.append((r, s))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [r for r, s in scored]


def score_region(region, ratings, vetoes):
    """Region score = sum of top 2 river ratings."""
    rivers = get_rivers_sorted(region, ratings, vetoes)
    if not rivers:
        return 0.0
    top = rivers[:2]
    return sum(ratings.get(r, 0.0) for r in top)


def get_order_index(region, river, candidate_set=None):
    """Index of river in south→north order."""
    base_order = REGION_RIVER_ORDER.get(region, [])
    if candidate_set is not None:
        order = [r for r in base_order if r in candidate_set]
    else:
        order = base_order

    try:
        return order.index(river)
    except ValueError:
        return len(order)


def build_directional_river_sequence(region, ratings, vetoes, days_needed):
    """
    Directional sequencing for NorCal + Oregon:
      - Start at highest-rated river
      - Move directionally
      - Reverse only if gain >= 0.5
    """
    candidates = get_rivers_sorted(region, ratings, vetoes)
    if not candidates or days_needed <= 0:
        return []

    candidate_set = set(candidates)
    rated = sorted(
        [(r, ratings.get(r, 0.0)) for r in candidates],
        key=lambda x: x[1],
        reverse=True
    )

    anchor_river = rated[0][0]
    sequence = [anchor_river]
    used = {anchor_river}

    def idx(r):
        return get_order_index(region, r, candidate_set=candidate_set)

    anchor_idx = idx(anchor_river)
    higher = [r for r, s in rated[1:] if idx(r) > anchor_idx]
    lower = [r for r, s in rated[1:] if idx(r) < anchor_idx]
    direction = +1 if len(higher) >= len(lower) else -1

    while len(sequence) < days_needed and len(used) < len(candidates):
        current = sequence[-1]
        current_idx = idx(current)
        current_score = ratings.get(current, 0.0)

        forward = []
        reverse = []

        for r, s in rated:
            if r in used:
                continue
            r_idx = idx(r)
            delta = r_idx - current_idx

            if (delta > 0 and direction == +1) or (delta < 0 and direction == -1):
                forward.append((r, s))
            else:
                reverse.append((r, s))

        if forward:
            forward.sort(key=lambda x: x[1], reverse=True)
            next_river = forward[0][0]
            sequence.append(next_river)
            used.add(next_river)
            continue

        if reverse:
            reverse.sort(key=lambda x: x[1], reverse=True)
            best_rev, best_score = reverse[0]
            if best_score >= current_score + 0.5:
                sequence.append(best_rev)
                used.add(best_rev)
                direction *= -1
                continue

        break

    return sequence


def allocate_rivers_in_region(region, days_allocated, ratings, vetoes):
    """
    Returns a list of rivers to fish in this region, ordered by rating,
    filtered by dynamic threshold logic:
      - Best ≥ 4.0 → threshold = 1.0
      - Best 3.5–4.0 → threshold = 0.75
      - Best 2.5–3.0 → threshold = 0.5
      - Best < 2.5 → threshold = 0.25

    Only rivers within threshold of the best are included.
    Stops at the first river that fails the threshold test.
    """

    # Get all rivers for this region
    rivers = REGION_TO_RIVERS.get(region, [])

    # Filter out vetoed rivers
    rivers = [r for r in rivers if not vetoes.get(r, False)]

    if not rivers:
        return []

    # Sort by rating (descending)
    rivers_sorted = sorted(rivers, key=lambda r: ratings.get(r, 0), reverse=True)

    best_river = rivers_sorted[0]
    best_rating = ratings.get(best_river, 0)

    # Determine threshold
    if best_rating >= 4.0:
        threshold = 1.0
    elif best_rating >= 3.5:
        threshold = 0.75
    elif best_rating >= 2.5:
        threshold = 0.5
    else:
        threshold = 0.25

    # Build fishable list
    fishable = [best_river]

    for r in rivers_sorted[1:]:
        diff = best_rating - ratings.get(r, 0)
        if diff <= threshold:
            fishable.append(r)
        else:
            break  # stop at first river that fails

    return fishable


def allocate_days(total_days, region_seq, ratings, vetoes):
    """
    Deacon allocation model:
      - Pyramid: 3 days if >=3.5, 2 days if >=3.25, else 1
      - OP: must have >=2 days or excluded
      - Coast collapse: if all coastal <1.0, dump into Pyramid
      - Otherwise: min 1 day each coastal region (OP min 2)
      - Ensure second-best coastal region gets >=2 days
      - Remaining days go to best coastal region
    """
    if total_days <= 0 or not region_seq:
        return {}

    regions = [r for r in region_seq if r != "Eagle"]

    scores = {r: score_region(r, ratings, vetoes) for r in regions}

    coastal_regs = [r for r in regions if r in ["NorCal", "Oregon", "OP"]]
    coastal_scores = {r: scores.get(r, 0.0) for r in coastal_regs}

    pyr_rating = scores.get("Pyramid", 0.0)

    # Minimum allocations
    alloc = {}
    for reg in regions:
        if reg == "Pyramid":
            if pyr_rating >= 3.5:
                alloc[reg] = 3
            elif pyr_rating >= 3.25:
                alloc[reg] = 2
            else:
                alloc[reg] = 1
        elif reg == "OP":
            alloc[reg] = 2
        else:
            alloc[reg] = 1

    # Coast collapse
    if coastal_regs and max(coastal_scores.values()) < 1.0:
        used = sum(alloc.values())
        remaining = total_days - used
        if remaining > 0:
            if "Pyramid" in alloc:
                alloc["Pyramid"] += remaining
            else:
                best = max(scores.keys(), key=lambda r: scores[r])
                alloc[best] += remaining
        return alloc

    # OP feasibility
    if "OP" in regions:
        used = sum(alloc.values())
        remaining = total_days - used
        if alloc["OP"] + max(remaining, 0) < 2:
            total_days += alloc["OP"]
            del alloc["OP"]
            regions.remove("OP")
            coastal_regs = [r for r in coastal_regs if r != "OP"]
            coastal_scores = {r: scores.get(r, 0.0) for r in coastal_regs}

    # Recompute remaining
    used = sum(alloc.values())
    remaining = total_days - used

    if remaining < 0:
        # Trim lowest-value regions
        for reg in sorted(alloc.keys(), key=lambda r: scores.get(r, 0.0)):
            if remaining == 0:
                break
            min_allowed = (
                3 if reg == "Pyramid" and pyr_rating >= 3.5 else
                2 if (reg == "Pyramid" and pyr_rating >= 3.25) or reg == "OP" else
                1
            )
            while alloc[reg] > min_allowed and remaining < 0:
                alloc[reg] -= 1
                remaining += 1
        return alloc

    if remaining == 0:
        return alloc

    # Distribute remaining days
    coastal_nonempty = {r: s for r, s in coastal_scores.items() if r in alloc}
    if coastal_nonempty:
        ranked = sorted(coastal_nonempty.keys(), key=lambda r: coastal_nonempty[r], reverse=True)
        best = ranked[0]
        second = ranked[1] if len(ranked) > 1 else None

        while remaining > 0:
            if second and alloc.get(second, 0) < 2:
                alloc[second] += 1
                remaining -= 1
                continue
            alloc[best] += 1
            remaining -= 1
    else:
        best = max(scores.keys(), key=lambda r: scores[r])
        alloc[best] += remaining

    return alloc


# ===== 5. BASIN CORRIDOR / EAGLE LOGIC =====

def uses_basin_corridor(region_seq):
    """True if Pyramid or inland transitions exist."""
    if "Pyramid" in region_seq:
        return True
    if "NorCal" in region_seq and "Oregon" in region_seq:
        return True
    if "Oregon" in region_seq and "OP" in region_seq:
        return True
    return False


def eagle_allowed(region_seq, vetoes):
    """Eagle allowed unless OP-only or Pyramid vetoed without inland link."""
    if region_seq == ["OP"]:
        return False
    if vetoes.get("Pyramid", False) and not ("NorCal" in region_seq and "Oregon" in region_seq):
        return False
    return uses_basin_corridor(region_seq)


def eagle_position(region_seq):
    """Insert Eagle after Pyramid or before first inland transition."""
    if "Pyramid" in region_seq:
        return region_seq.index("Pyramid") + 1

    transitions = [("NorCal", "Oregon"), ("Oregon", "OP")]
    for a, b in transitions:
        if a in region_seq and b in region_seq and region_seq.index(a) < region_seq.index(b):
            return region_seq.index(a) + 1

    return len(region_seq)


def eagle_homeward_required(current_loc):
    """If >12 hours from home, Eagle can be used as overnight."""
    miles, hrs = get_drive_distance(current_loc, "Home")
    return hrs > 12.0


# ===== 6. REGION DETECTION & ORDERING =====

def region_has_fishable_rivers(region, ratings, vetoes, min_score=1.0):
    """True if region has at least one river >= min_score."""
    if vetoes.get(region, False):
        return False
    rivers = get_rivers_sorted(region, ratings, vetoes)
    return any(ratings.get(r, 0.0) >= min_score for r in rivers)


def detect_trip_regions(ratings, vetoes):
    """Determine which regions are included."""
    use_pyr = not vetoes.get("Pyramid", False) and ratings.get("Pyramid", 0.0) >= 0.5
    use_norcal = region_has_fishable_rivers("NorCal", ratings, vetoes)
    use_oregon = region_has_fishable_rivers("Oregon", ratings, vetoes)
    use_op = region_has_fishable_rivers("OP", ratings, vetoes)

    regions = {
        "Pyramid": use_pyr,
        "NorCal": use_norcal,
        "Oregon": use_oregon,
        "OP": use_op,
    }

    op_only = use_op and not (use_pyr or use_norcal or use_oregon)
    return regions, op_only


def build_region_sequence(vetoes, ratings):
    """Build ordered region sequence."""
    seq = []

    if not vetoes.get("Pyramid", False) and ratings.get("Pyramid", 0.0) >= 0.5:
        seq.append("Pyramid")

    if region_has_fishable_rivers("NorCal", ratings, vetoes):
        seq.append("NorCal")

    if region_has_fishable_rivers("Oregon", ratings, vetoes):
        seq.append("Oregon")

    if region_has_fishable_rivers("OP", ratings, vetoes):
        op_score = score_region("OP", ratings, vetoes)
        other_scores = score_region("NorCal", ratings, vetoes) + score_region("Oregon", ratings, vetoes)
        if op_score >= 6.0 or (op_score >= 4.0 and other_scores == 0):
            seq.append("OP")

    return seq


def order_filler_regions(possible_regions, ratings, current_region=None):
    """Order filler regions by rating with 0.5 guardrail."""
    regions_sorted = sorted(possible_regions, key=lambda r: ratings.get(r, 0.0), reverse=True)

    if current_region is None:
        return regions_sorted

    ordered = []
    current = current_region

    for reg in regions_sorted:
        if reg == current:
            continue
        gain = ratings.get(reg, 0.0) - ratings.get(current, 0.0)
        if gain >= 0.5:
            ordered.append(reg)
            current = reg

    for reg in regions_sorted:
        if reg not in ordered and reg != current_region:
            ordered.append(reg)

    return ordered


def get_region_hub(region, ratings, vetoes):
    """Return the hub town for a region."""
    if region == "NorCal":
        good = get_rivers_sorted("NorCal", ratings, vetoes)
        if not good:
            return "Pepperwood"
        if "Smith River (CA)" in good[:2]:
            return "Hiouchi"
        if any(r in good for r in ["Eel (Main)", "SF Eel", "Van Duzen"]):
            return "Eureka"
        return "Pepperwood"

    if region == "Oregon":
        good = get_rivers_sorted("Oregon", ratings, vetoes)
        if not good:
            return "Brookings"
        if "Chetco" in good[:2]:
            return "Brookings"
        if any(r in good for r in ["Elk River", "Sixes River"]):
            return "Port Orford"
        if "Rogue" in good:
            return "Gold Beach"
        if any(r in good for r in ["N. Umpqua", "Umpqua (Main)"]):
            return "Coos Bay"
        return "Brookings"

    if region == "OP":
        return "Forks"

    if region == "Pyramid":
        return "Pyramid"

    if region == "Eagle":
        return "Eagle"

    return "Home"

# ===== 7. ITINERARY ENGINE (CORRECTED) =====
# ===== PART 5 — CHUNK 1 OF 4 =====
# Core utilities, directional order, region scoring, and river selection (R‑C)

def get_drive_distance(loc1, loc2):
    """Haversine-based road distance with 1.25 fudge factor."""
    if loc1 == loc2:
        return 0, 0.0
    if loc1 not in NODE_COORDS or loc2 not in NODE_COORDS:
        return 0, 0.0

    lat1, lon1 = NODE_COORDS[loc1]
    lat2, lon2 = NODE_COORDS[loc2]

    R = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat/2)**2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon/2)**2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    miles_straight = R * c
    miles_road = miles_straight * 1.25
    hours = miles_road / 55.0

    return int(round(miles_road)), round(hours, 1)


# ===== Directional order (south → north) =====

DIRECTIONAL_ORDER = {
    "NorCal": [
        "Eel (Main)",
        "SF Eel",
        "Van Duzen",
        "Smith River (CA)"
    ],
    "Oregon": [
        "Chetco",
        "Elk River",
        "Sixes River",
        "Rogue",
        "Umpqua (Main)",
        "N. Umpqua"
    ],
    "OP": [
        "Queets",
        "Hoh",
        "Bogachiel",
        "Calawah"
    ]
}


def get_directional_order(region):
    """Return the directional order list for a region."""
    return DIRECTIONAL_ORDER.get(region, [])


# ===== Region score (R2: sum of top 2 rivers) =====

def get_region_score(region, ratings, vetoes):
    """Region score = sum of top 2 river ratings."""
    rivers = RIVER_SPECS.get(region, [])
    vals = []
    for r in rivers:
        if vetoes.get(r["Name"], False):
            continue
        vals.append(ratings.get(r["Name"], 0.0))
    vals.sort(reverse=True)
    if not vals:
        return 0.0
    if len(vals) == 1:
        return vals[0]
    return vals[0] + vals[1]


# ===== River selection (R‑C: best river → directional order) =====

def allocate_rivers_in_region(region, days, ratings, vetoes):
    """
    R‑C logic:
      1. Pick highest-rated river in region
      2. Then follow directional order (south → north)
      3. Only return 'days' rivers
    """
    if days <= 0:
        return []

    rivers = RIVER_SPECS.get(region, [])
    if not rivers:
        return []

    # Build rating map
    rating_map = {}
    for r in rivers:
        if vetoes.get(r["Name"], False):
            continue
        rating_map[r["Name"]] = ratings.get(r["Name"], 0.0)

    if not rating_map:
        return []

    # Step 1: highest-rated river
    best_river = max(rating_map, key=lambda x: rating_map[x])

    # Step 2: directional order
    order = get_directional_order(region)
    if not order:
        # fallback: just sort by rating
        ordered = sorted(rating_map.keys(), key=lambda x: rating_map[x], reverse=True)
    else:
        # rotate directional list so best river is first
        if best_river in order:
            idx = order.index(best_river)
            ordered = order[idx:] + order[:idx]
        else:
            # if best river not in directional list, fallback to rating order
            ordered = sorted(rating_map.keys(), key=lambda x: rating_map[x], reverse=True)

    # Filter to rivers actually present and not vetoed
    final_list = [r for r in ordered if r in rating_map]

    # Step 3: return only as many as allocated days
    return final_list[:days]
# ===== PART 5 — CHUNK 2 OF 4 =====
# Filler region selection (C3 + R2) and filler rivers

def choose_filler_region(current_region, visited_regions, ratings, vetoes):
    """
    C3 + R2:
      - Compute region score for each visited region (sum of top 2 rivers)
      - Default: stay in current_region
      - Move only if another region's score beats current by ≥ 0.5
    """
    if not visited_regions:
        return current_region

    scores = {}
    for reg in visited_regions:
        scores[reg] = get_region_score(reg, ratings, vetoes)

    current_score = scores.get(current_region, 0.0)
    best_region = current_region
    best_score = current_score

    for reg, sc in scores.items():
        if sc >= best_score + 0.5:
            best_region = reg
            best_score = sc

    return best_region


def choose_filler_river(region, ratings, vetoes):
    """
    Choose the best available river in a region for a filler day.
    Uses same R‑C rating logic but only returns one river.
    """
    rivers = RIVER_SPECS.get(region, [])
    rating_map = {}
    for r in rivers:
        name = r["Name"]
        if vetoes.get(name, False):
            continue
        rating_map[name] = ratings.get(name, 0.0)

    if not rating_map:
        return None

    # Best-rated river
    best_river = max(rating_map, key=lambda x: rating_map[x])
    return best_river
# ===== PART 5 — CHUNK 3 OF 4 =====
# Pyramid block, Eagle block, region transitions, scaffolding

def drive_and_log(rows, current_date, current_loc, next_loc, mpg, NODES, label):
    """Drive from current_loc to next_loc and log it. Returns (new_loc, new_date, days_used_increment)."""
    miles, hrs = get_drive_distance(current_loc, next_loc)
    gas_price = NODES.get(current_loc, {}).get("gas", 4.00)
    gas_cost = (miles / mpg) * gas_price

    rows.append([
        current_date.strftime("%b %d (%a)"),
        next_loc,
        f"DRIVE: {current_loc} → {next_loc} ({label})",
        miles,
        hrs,
        f"${gas_cost:.0f}"
    ])

    # Transition rule (Option B):
    #   - If drive > 3 hours → consumes a full day
    #   - If drive ≤ 3 hours → same-day transition allowed
    if hrs > 3.0:
        return next_loc, current_date + timedelta(days=1), 1
    else:
        return next_loc, current_date, 0


def run_pyramid_block(rows, start_date, mpg, NODES, ratings, vetoes):
    """
    Pyramid block:
      - Day 1: Drive Home → Pyramid
      - Next N days: Fish Pyramid
    """
    pyr_rating = ratings.get("Pyramid", 0.0)

    if pyr_rating >= 3.5:
        pyr_days = 3
    elif pyr_rating >= 3.25:
        pyr_days = 2
    else:
        pyr_days = 1

    current_loc = "Pyramid"
    current_date = start_date
    days_used = 0

    # Day 1: drive Home → Pyramid
    miles, hrs = get_drive_distance("Home", "Pyramid")
    gas_price = NODES.get("Home", {}).get("gas", 4.00)
    gas_cost = (miles / mpg) * gas_price

    rows.append([
        current_date.strftime("%b %d (%a)"),
        "Pyramid",
        "DRIVE: Home → Pyramid (Pyramid)",
        miles,
        hrs,
        f"${gas_cost:.0f}"
    ])

    days_used += 1
    current_date += timedelta(days=1)  # <-- KEY: move to next day before fishing

    # Fish Pyramid for pyr_days
    for _ in range(pyr_days):
        rows.append([
            current_date.strftime("%b %d (%a)"),
            "Pyramid",
            "FISH: Pyramid (Pyramid)",
            0,
            0,
            "-"
        ])
        days_used += 1
        current_date += timedelta(days=1)

    # No extra "advance to next morning" here

    return current_loc, current_date, days_used

def run_eagle_block(rows, current_loc, current_date, days_used, mpg, NODES, next_region, ratings, vetoes):
    """
    Correct Eagle behavior:
    - Drive Pyramid → Eagle (consumes 1 day)
    - Fish Eagle same day (does NOT consume another day)
    - Return updated date + days_used
    """

    # DRIVE TO EAGLE (consumes 1 day)
    miles, hrs = get_drive_distance(current_loc, "Eagle")
    gas_price = NODES.get(current_loc, {}).get("gas", 4.00)
    gas_cost = (miles / mpg) * gas_price

    rows.append([
        current_date.strftime("%b %d (%a)"),
        "Eagle",
        "DRIVE: " + current_loc + " → Eagle (Eagle)",
        miles,
        hrs,
        f"${gas_cost:.0f}"
    ])

    current_loc = "Eagle"
    current_date += timedelta(days=1)
    days_used += 1

    # FISH EAGLE SAME DAY (NO DATE ADVANCE)
    rows.append([
        (current_date - timedelta(days=1)).strftime("%b %d (%a)"),
        "Eagle",
        "FISH: Eagle Lake (Half-Day)",
        0,
        0,
        "-"
    ])

    return current_loc, current_date, days_used

def drive_to_region(rows, current_loc, current_date, days_used, target_region, ratings, vetoes, mpg, NODES):
    """Drive to a region hub using Option B transition rules."""
    hub = get_region_hub(target_region, ratings, vetoes)
    new_loc, new_date, inc = drive_and_log(
        rows,
        current_date,
        current_loc,
        hub,
        mpg,
        NODES,
        target_region
    )
    return new_loc, new_date, days_used + inc

# ===== PART 5 — CHUNK 4 (REBUILT WITH DYNAMIC THRESHOLDS & OP RULE) =====

def region_of_location(loc):
    """Return the region associated with a hub/location."""
    if loc in {"Hiouchi", "Pepperwood", "Maple Grove", "Eureka"}:
        return "NorCal"
    if loc in {"Brookings", "Port Orford", "Gold Beach", "Reedsport", "Steamboat", "Coos Bay"}:
        return "Oregon"
    if loc in {"Forks", "Bogachiel", "Hoh", "Queets"}:
        return "OP"
    if loc == "Pyramid":
        return "Pyramid"
    if loc == "Eagle":
        return "Eagle"
    return None


def finalize_return(rows, current_loc, current_date, total_trip_days, mpg, NODES, start_date):
    """
    Clean, chronological return logic.
    Uses current_date as the next available day.
    Never rewrites earlier days.
    """

    days_used = (current_date - start_date).days
    remaining_days = total_trip_days - days_used

    if remaining_days <= 0:
        return rows

    miles, hrs = get_drive_distance(current_loc, "Home")
    gas_price = NODES.get(current_loc, {}).get("gas", 4.00)
    gas_cost = (miles / mpg) * gas_price

    MAX_HOURS_PER_DAY = 10.0

    # If we can make it home in one day OR only one day remains
    if hrs <= MAX_HOURS_PER_DAY or remaining_days == 1:
        rows.append([
            current_date.strftime("%b %d (%a)"),
            "Home",
            f"RETURN: {current_loc} → Home",
            miles,
            hrs,
            f"${gas_cost:.0f}"
        ])
        return rows

    # Otherwise: two-day return
    half_miles = miles * 0.5
    half_hrs = hrs * 0.5
    half_cost = gas_cost * 0.5

    # Leg 1
    rows.append([
        current_date.strftime("%b %d (%a)"),
        "On Route",
        f"RETURN (Leg 1): {current_loc} → Midpoint",
        half_miles,
        half_hrs,
        f"${half_cost:.0f}"
    ])

    # Leg 2
    rows.append([
        (current_date + timedelta(days=1)).strftime("%b %d (%a)"),
        "Home",
        "RETURN (Leg 2): Midpoint → Home",
        half_miles,
        half_hrs,
        f"${half_cost:.0f}"
    ])

    return rows

def get_rivers_for_region(region):
    """
    Build a list of rivers belonging to a region based on RIVER_TO_NODE.
    This replaces REGION_TO_RIVERS which does not exist in your codebase.
    """
    rivers = []
    for river, hub in RIVER_TO_NODE.items():
        if region_of_location(hub) == region:
            rivers.append(river)
    return rivers

def build_itinerary(start_date, total_trip_days, ratings, vetoes, mpg, NODES):
    """
    Full itinerary engine implementing:
      - Pyramid block (always first)
      - Eagle half-day logic
      - Dynamic river thresholds with second-best logic
      - Entry hub = hub of best river (especially for NorCal)
      - OP only visited if there are 2+ fishable days
      - No bouncing between hubs inside regions
      - Filler logic using PHYSICAL REGION
      - Correct date handling (no drift, no skipped days)
    """

    rows = []
    current_date = start_date
    current_loc = "Home"

    # ===== REGION SEQUENCE =====
    base_seq = build_region_sequence(vetoes, ratings)

    # Pyramid always first if included
    has_pyramid = "Pyramid" in base_seq and not vetoes.get("Pyramid", False)
    if has_pyramid:
        base_seq = ["Pyramid"] + [r for r in base_seq if r != "Pyramid"]

    # Eagle allowed?
    allow_eagle = eagle_allowed(base_seq, vetoes)

    # ===== ALLOCATE DAYS =====
    alloc = allocate_days(total_trip_days, base_seq, ratings, vetoes)

    # Override Pyramid allocation
    if has_pyramid:
        pyr_rating = ratings.get("Pyramid", 0.0)
        if pyr_rating >= 3.5:
            alloc["Pyramid"] = 3
        elif pyr_rating >= 3.25:
            alloc["Pyramid"] = 2
        else:
            alloc["Pyramid"] = 1

    # Build post-Pyramid region list
    post_pyr_seq = [r for r in base_seq if r != "Pyramid"]

    visited_regions = set()

    def days_used_from_date(dt):
        return (dt - start_date).days

    def get_fishable_rivers(region):
        """
        Dynamic threshold + second-best logic:

          - Best ≥ 4.0 → threshold = 1.0
          - Best 3.5–4.0 → threshold = 0.75
          - Best 2.5–3.0 → threshold = 0.5
          - Best < 2.5 → threshold = 0.25

        Rivers sorted by rating (desc).
        Include best, then keep adding until first river that fails threshold.
        """
        rivers_all = get_rivers_for_region(region)
        rivers_all = [r for r in rivers_all if not vetoes.get(r, False)]
        if not rivers_all:
            return []

        rivers_sorted = sorted(rivers_all, key=lambda r: ratings.get(r, 0), reverse=True)
        best_river = rivers_sorted[0]
        best_rating = ratings.get(best_river, 0)

        if best_rating >= 4.0:
            threshold = 1.0
        elif best_rating >= 3.5:
            threshold = 0.75
        elif best_rating >= 2.5:
            threshold = 0.5
        else:
            threshold = 0.25

        fishable = [best_river]
        for r in rivers_sorted[1:]:
            diff = best_rating - ratings.get(r, 0)
            if diff <= threshold:
                fishable.append(r)
            else:
                break  # stop at first failure

        return fishable

    # ===== 1. PYRAMID BLOCK =====
    if has_pyramid:
        current_loc, current_date, _ = run_pyramid_block(
            rows, start_date, mpg, NODES, ratings, vetoes
        )
        visited_regions.add("Pyramid")

    # ===== 2. EAGLE BLOCK =====
    if has_pyramid and allow_eagle and days_used_from_date(current_date) < total_trip_days:
        next_region = post_pyr_seq[0] if post_pyr_seq else None
        current_loc, current_date, _ = run_eagle_block(
            rows,
            current_loc,
            current_date,
            days_used_from_date(current_date),
            mpg,
            NODES,
            next_region,
            ratings,
            vetoes
        )
        visited_regions.add("Eagle")

    # ===== SPECIAL CASE: SAME-DAY EAGLE → NORCAL ENTRY =====
    if current_loc == "Eagle" and post_pyr_seq and post_pyr_seq[0] == "NorCal":
        norcal_rivers = get_fishable_rivers("NorCal")
        if norcal_rivers:
            best_river = norcal_rivers[0]
            eel_system = {"Eel (Main)", "SF Eel", "Van Duzen"}

            if best_river in eel_system:
                entry_hub = "Pepperwood"
            else:
                entry_hub = "Hiouchi"

            miles, hrs = get_drive_distance("Eagle", entry_hub)
            gas_price = NODES.get("Eagle", {}).get("gas", 4.00)
            gas_cost = (miles / mpg) * gas_price

            # Log drive on same day as Eagle half-day (current_date - 1)
            rows.append([
                (current_date - timedelta(days=1)).strftime("%b %d (%a)"),
                entry_hub,
                f"DRIVE: Eagle → {entry_hub} (NorCal Entry)",
                miles,
                hrs,
                f"${gas_cost:.0f}"
            ])

            current_loc = entry_hub
        # current_date stays as the next morning

    # ===== 3. MAIN REGION LOOP =====
    for reg in post_pyr_seq:
        days_used = days_used_from_date(current_date)
        if days_used >= total_trip_days:
            break

        # Get fishable rivers for this region
        rivers = get_fishable_rivers(reg)

        # Special OP rule: only go if 2+ fishable days
        if reg == "OP" and len(rivers) < 2:
            continue

        if not rivers:
            continue

        # Determine entry hub
        if reg == "NorCal":
            best_river = rivers[0]
            eel_system = {"Eel (Main)", "SF Eel", "Van Duzen"}
            if best_river in eel_system:
                region_hub = "Pepperwood"
            else:
                region_hub = "Hiouchi"
        else:
            # Default: hub of best river if available, otherwise region hub
            best_river = rivers[0]
            region_hub = RIVER_TO_NODE.get(best_river, get_region_hub(reg, ratings, vetoes))

        # Drive to region entry hub if needed
        if current_loc != region_hub:
            current_loc, current_date, _ = drive_and_log(
                rows,
                current_date,
                current_loc,
                region_hub,
                mpg,
                NODES,
                label=f"{reg} Entry"
            )
            days_used = days_used_from_date(current_date)
            if days_used >= total_trip_days:
                break

        visited_regions.add(reg)

        # Fish rivers in this region (no bouncing; movement only when river is within threshold)
        for rv in rivers:
            days_used = days_used_from_date(current_date)
            if days_used >= total_trip_days:
                break

            river_hub = RIVER_TO_NODE.get(rv, region_hub)

            if current_loc != river_hub:
                current_loc, current_date, _ = drive_and_log(
                    rows,
                    current_date,
                    current_loc,
                    river_hub,
                    mpg,
                    NODES,
                    label=f"{reg} Rivers"
                )
                days_used = days_used_from_date(current_date)
                if days_used >= total_trip_days:
                    break

            rows.append([
                current_date.strftime("%b %d (%a)"),
                river_hub,
                f"FISH: {rv} ({reg})",
                0,
                0,
                "-"
            ])

            current_date += timedelta(days=1)

    # ===== 4. FILLER DAYS =====
    # Keep at least 2 days available for return if it's long
    while days_used_from_date(current_date) < total_trip_days - 2:
        days_used = days_used_from_date(current_date)
        if days_used >= total_trip_days - 2:
            break

        physical_region = region_of_location(current_loc)

        filler_region = choose_filler_region(
            current_region=physical_region,
            visited_regions=visited_regions,
            ratings=ratings,
            vetoes=vetoes
        )

        hub = get_region_hub(filler_region, ratings, vetoes)

        if current_loc != hub:
            current_loc, current_date, days_used = drive_to_region(
                rows,
                current_loc,
                current_date,
                days_used,
                filler_region,
                ratings,
                vetoes,
                mpg,
                NODES
            )
            if days_used >= total_trip_days:
                break

        visited_regions.add(filler_region)

        rivers = get_fishable_rivers(filler_region)
        rv = rivers[0] if rivers else None

        rows.append([
            current_date.strftime("%b %d (%a)"),
            hub,
            f"FISH: {rv if rv else '(No Available River)'} ({filler_region})",
            0,
            0,
            "-"
        ])

        current_date += timedelta(days=1)

    # ===== 5. RETURN HOME =====
    rows = finalize_return(
        rows,
        current_loc,
        current_date,
        total_trip_days,
        mpg,
        NODES,
        start_date
    )

    return pd.DataFrame(
        rows,
        columns=["Date", "Location", "Activity", "Miles", "Hrs", "Est Cost"]
    )


# ===== 7. BUILD & DISPLAY ITINERARY =====

st.subheader("🔮 Itinerary")

df = build_itinerary(start_date, total_trip_days, ratings, vetoes, mpg, NODES)

if not df.empty:
    # ----- SUMMARY METRICS -----
    total_miles = df["Miles"].sum()
    total_hours = df["Hrs"].sum()
    fish_days = df[df["Activity"].str.contains("FISH", case=False)].shape[0]

    total_fuel = 0
    for c in df["Est Cost"]:
        if "$" in str(c):
            try:
                total_fuel += int(str(c).replace("$", "").replace(",", ""))
            except:
                pass

    # ----- REGION COUNTS -----
    region_lookup = {
        "Pyramid": "Pyramid",
        "Pepperwood": "NorCal", "Maple Grove": "NorCal", "Hiouchi": "NorCal", "Eureka": "NorCal",
        "Brookings": "Oregon", "Gold Beach": "Oregon", "Port Orford": "Oregon",
        "Coos Bay": "Oregon", "Reedsport": "Oregon", "Steamboat": "Oregon",
        "Forks": "OP", "Bogachiel": "OP", "Hoh": "OP", "Queets": "OP",
        "Eagle": "Basin",
    }

    r_counts = {"Pyramid": 0, "NorCal": 0, "Oregon": 0, "OP": 0, "Basin": 0}
    for _, row in df.iterrows():
        loc = row["Location"]
        reg = region_lookup.get(loc, "")
        if reg in r_counts and "FISH" in row["Activity"]:
            r_counts[reg] += 1

    # ----- REGION DAY METRICS -----
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Pyramid Days", r_counts["Pyramid"])
    c2.metric("NorCal Days", r_counts["NorCal"])
    c3.metric("Oregon Days", r_counts["Oregon"])
    c4.metric("OP Days", r_counts["OP"])
    c5.metric("Basin (Eagle) Days", r_counts["Basin"])

    st.divider()

    # ----- TRIP TOTALS -----
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Fish Days", fish_days)
    d2.metric("Total Miles", f"{int(total_miles):,}")
    d3.metric("Drive Hours", f"{total_hours:.1f}")
    d4.metric("Est. Fuel", f"${total_fuel}")

    # ----- FORMAT TABLE FOR DISPLAY -----
    df_display = df.copy()

    # Miles → whole numbers
    df_display["Miles"] = (
        df_display["Miles"]
        .astype(float)
        .round(0)
        .astype(int)
    )

    # Hours → 1 decimal
    df_display["Hrs"] = (
        df_display["Hrs"]
        .astype(float)
        .round(1)
    )

    # ----- BIG HEIGHT TO AVOID INTERNAL SCROLL -----
    height = (len(df_display) + 1) * 32  # one row ~32px

    st.dataframe(
        df_display[["Date", "Location", "Activity", "Miles", "Hrs", "Est Cost"]],
        hide_index=True,
        use_container_width=True,
        height=height
    )

    # ===== MAP VIEW =====
    import pydeck as pdk

    st.subheader("🗺️ Map View")

    # --- Build river dataframe ---
    river_rows = []
    for region, rivers in RIVER_SPECS.items():
        for r in rivers:
            if "Lat" in r and "Lon" in r:
                score = auto_score_river(r["Name"], r)
                river_rows.append({
                    "name": r["Name"],
                    "lat": r["Lat"],
                    "lon": r["Lon"],
                    "region": region,
                    "score": score["total"],
                    "flow": score["flow"],
                    "trend": score["trend"],
                    "weather": score["weather"],
                    "base": score["base"]
                })

    df_rivers = pd.DataFrame(river_rows)

    # --- Build hub dataframe ---
    hub_rows = []
    for hub, (lat, lon) in NODE_COORDS.items():
        hub_rows.append({"hub": hub, "lat": lat, "lon": lon})

    df_hubs = pd.DataFrame(hub_rows)

    # --- Build itinerary polyline (robust version) ---
    itinerary_coords = []

    for _, row in df.iterrows():
        raw = row["Location"]

        # Remove prefixes
        loc = raw.replace("FISH ", "").replace("TRAVEL ", "").strip()

        # Remove suffixes like "(CA)" or "(Main)"
        loc = loc.split("(")[0].strip()

        # Normalize common patterns
        LOCATION_NORMALIZE = {
            "Eagle Lake": "Eagle",
            "Brookings, OR": "Brookings",
            "Gold": "Gold Beach",
            "Port": "Port Orford",
            "Camp": "",
            "Rest": "",
            "Drive": "",
            "Home": "Home",
        }

        # If first word is a known hub, use it
        first = loc.split()[0]
        if first in LOCATION_NORMALIZE:
            loc = LOCATION_NORMALIZE[first] or first

        # Final lookup
        if loc in NODE_COORDS:
            lat, lon = NODE_COORDS[loc]
            itinerary_coords.append([lon, lat])  # ✅ PathLayer requires [lon, lat]

    # Ensure polyline always has at least 2 points
    if len(itinerary_coords) < 2:
        itinerary_coords = []

    df_route = pd.DataFrame([{"path": itinerary_coords}])

    # --- Color scale ---
    def score_to_color(score):
        t = max(0, min(score / 5, 1))
        r = int(255 * t)
        g = int(255 * (1 - t))
        b = 100
        return [r, g, b]

    df_rivers["color"] = df_rivers["score"].apply(score_to_color)

    # --- Layers ---
    river_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_rivers,
        get_position=["lon", "lat"],
        get_radius=5000,
        get_fill_color="color",
        pickable=True,
    )

    hub_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_hubs,
        get_position=["lon", "lat"],
        get_radius=7000,
        get_fill_color=[0, 100, 255],
        pickable=True,
    )

    route_layer = pdk.Layer(
        "PathLayer",
        data=df_route,
        get_path="path",
        get_color=[0, 0, 0],
        width_scale=50,
        width_min_pixels=4,
    )

    # --- Tooltip ---
    tooltip = {
        "html": """
        {% if name %}
            <b>{{name}}</b><br/>
            Score: {{score}}<br/>
            Flow: {{flow}}<br/>
            Trend: {{trend}}<br/>
            Weather: {{weather}}<br/>
            Base: {{base}}
        {% else %}
            <b>{{hub}}</b>
        {% endif %}
        """,
        "style": {"backgroundColor": "black", "color": "white"}
    }

    # --- View ---
    view_state = pdk.ViewState(
        latitude=42.5,
        longitude=-123.5,
        zoom=6,
        pitch=30,
    )

    # --- Render ---
    st.pydeck_chart(
        pdk.Deck(
            layers=[river_layer, hub_layer, route_layer],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="light"
        )
    )

# ===== 8. CONDITIONS =====

st.divider()
st.subheader("Conditions")

def format_precip_text(txt: str) -> str:
    lower = txt.lower()
    if "between a tenth and a quarter of an inch" in lower or "between one tenth and one quarter of an inch" in lower:
        return '💧 Precip: 0.10–0.25" possible'
    if "between a quarter and half of an inch" in lower or "between a quarter and a half of an inch" in lower:
        return '💧 Precip: 0.25–0.50" possible'
    if "between half and three quarters of an inch" in lower or "between a half and three quarters of an inch" in lower:
        return '💧 Precip: 0.50–0.75" possible'
    if "between three quarters and one inch" in lower:
        return '💧 Precip: 0.75–1.00" possible'
    if "a quarter of an inch" in lower or "one quarter of an inch" in lower:
        return '💧 Precip: 0.25" possible'
    if "a tenth of an inch" in lower or "one tenth of an inch" in lower:
        return '💧 Precip: 0.10" possible'
    if "a half inch" in lower or "one half inch" in lower:
        return '💧 Precip: 0.50" possible'
    if "one inch possible" in lower or "around an inch" in lower:
        return '💧 Precip: ~1.00" possible'
    m = re.search(r"(amounts? (of|between) .+? (possible|expected))", lower)
    if m:
        phrase = m.group(1)
        phrase = phrase.replace("amounts of", "").replace("amounts between", "").strip()
        phrase = phrase.replace("a quarter", "0.25").replace("one quarter", "0.25")
        phrase = phrase.replace("a tenth", "0.10").replace("one tenth", "0.10")
        phrase = phrase.replace("a half", "0.5").replace("one half", "0.5")
        phrase = phrase.replace("three quarters", "0.75")
        phrase = phrase.replace("inches", '"').replace("inch", '"')
        phrase = phrase.replace("to", "–").replace("and", "–")
        phrase = phrase.replace("possible", "").replace("expected", "")
        phrase = re.sub(r'\s+', ' ', phrase).strip()
        if phrase:
            return f'💧 Precip: {phrase} possible'
    if "rain" in lower or "showers" in lower:
        return "💧 Precip: rain possible"
    if "snow" in lower:
        return "💧 Precip: snow possible"
    return "💧 Precip: none or minimal"

with st.expander("🌤️ Weather Forecast", expanded=False):
    if st.button("🔄 Load Weather"):
        with st.spinner("Fetching..."):
            t1, t2 = st.tabs(["36-Hour Detail", "5-Day Outlook"])
            locs = [
                ("Pyramid", 40.01, -119.62),
                ("Eureka", 40.80, -124.16),
                ("Crescent City", 41.75, -124.20),
                ("Brookings", 42.05, -124.27),
                ("Coos Bay", 43.36, -124.21),
                ("Forks", 47.95, -124.38)
            ]
            with t1:
                cols = st.columns(3)
                for i, (n, la, lo) in enumerate(locs):
                    p = get_nws_forecast_data(la, lo)
                    with cols[i % 3]:
                        st.markdown(f"**{n}**")
                        if p:
                            for x in p[:3]:
                                txt = x["detailedForecast"]
                                precip_clean = format_precip_text(txt)
                                st.caption(
                                    f"**{x['name']}**: {x['temperature']}°F. {x['shortForecast']}\n"
                                    f"*Wind: {x.get('windSpeed')} | {precip_clean}*"
                                )
            with t2:
                cols = st.columns(3)
                for i, (n, la, lo) in enumerate(locs):
                    p = get_nws_forecast_data(la, lo)
                    with cols[i % 3]:
                        st.markdown(f"**{n}**")
                        if p:
                            for x in p[:10:2]:
                                txt = x["detailedForecast"]
                                precip_clean = format_precip_text(txt)
                                st.caption(
                                    f"**{x['name']}**: {x['temperature']}°F. {x['shortForecast']} {precip_clean}"
                                )

with st.expander("🌊 Live River Levels", expanded=False):
    if st.button("🔄 Load Gauges"):
        with st.spinner("Fetching USGS..."):
            for reg, rivs in RIVER_SPECS.items():
                st.markdown(f"**{reg}**")
                cols = st.columns(4)
                for i, r in enumerate(rivs):
                    with cols[i % 4]:
                        series = get_usgs_series(r["ID"], r.get("P", "00060"), days=2)
                        val = series[-1][1] if series else None
                        ts = series[-1][0] if series else None
                        col = "off"; s_icon = ""
                        try:
                            mn = float(r["T"].split("-")[0])
                            mx = float(r["T"].split("-")[1].split()[0])
                            low = r.get("Low", 0)
                            if val is not None:
                                if val < low:
                                    col = "inverse"; s_icon = "⛔"
                                elif val < mn:
                                    col = "off"; s_icon = "🟡"
                                elif val > mx:
                                    col = "inverse"; s_icon = "🔴"
                                else:
                                    col = "normal"; s_icon = "🟢"
                        except:
                            pass
                        ts_display = ts.astimezone().strftime("%m-%d %H:%M") if ts else ""
                        st.metric(f"{s_icon} {r['Name']}", val if val is not None else "--", r["T"], delta_color=col)
                        if ts_display:
                            st.caption(f"{r['N']} | {ts_display}")
                        else:
                            st.caption(r["N"])

with st.expander("📉 Hydrographs", expanded=False):
    if st.button("Load Charts"):
        all_ids = []
        for reg, rivs in RIVER_SPECS.items():
            for r in rivs:
                all_ids.append((r["ID"], r.get("P", "00060"), r["Name"]))
        cols = st.columns(2)
        for i, (s, p, n) in enumerate(all_ids):
            with cols[i % 2]:
                st.write(f"**{n}**")
                st.image(
                    f"https://waterdata.usgs.gov/nwisweb/graph?agency_cd=USGS&site_no={s}&parm_cd={p}&period=7",
                    use_container_width=True
                )

# ===== 11. DEBUG PANEL =====

with st.expander("🛠️ Debug: Raw Ratings & Allocations", expanded=False):
    st.write("**Ratings:**", ratings)
    st.write("**Vetoes:**", vetoes)

    regions, op_only = detect_trip_regions(ratings, vetoes)
    st.write("**Detected Regions:**", regions)
    st.write("**OP Only:**", op_only)

    seq = build_region_sequence(vetoes, ratings)
    st.write("**Region Sequence:**", seq)

    alloc = allocate_days(total_trip_days, seq, ratings, vetoes)
    st.write("**Day Allocation:**", alloc)

    st.write("**Directional River Sequences:**")
    for reg in seq:
        if reg not in ["Pyramid", "Eagle"]:
            st.write(reg, allocate_rivers_in_region(reg, alloc.get(reg, 0), ratings, vetoes))