import streamlit as st
import requests
import datetime as dt
import numpy as np

# NEW: Import map renderer with error handling for standalone runs
try:
    from coastal_map import render_coastal_map
except ImportError:
    def render_coastal_map(data, filters):
        st.warning("Coastal Map module not found.")

# ============================================================
# COASTAL DASHBOARD — CHUNK 1: REGION SPECS
# ============================================================

def load_coastal_region_specs():
    # 1. REGION SPECS — NORTHERN CALIFORNIA
    COASTAL_NORCAL = [
        {
            "Name": "Smith River (CA)",
            "Gauges": [
                {
                    "ID": "11532500",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Smith River near Crescent City (flow)",
                }
            ],
            "T": "1500-7500 cfs",
            "Low": 600,
            "N": "Holy Grail. Tidewater to Craigs; short sharp windows.",
            "Type": "flashy",
            "NOAA_zone": "CAC01",
        },
        {
            "Name": "Middle Fork Smith",
            "Gauges": [
                {
                    "ID": "11532600",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Middle Fork Smith near Gasquet (flow)",
                }
            ],
            "T": "600-2500 cfs",
            "Low": 350,
            "N": "Smaller, clearer than main; greens up sooner.",
            "Type": "flashy",
            "NOAA_zone": "CAC01",
        },
        {
            "Name": "Mattole",
            "Gauges": [
                {
                    "ID": "11469000",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Mattole River near Petrolia (flow)",
                }
            ],
            "T": "600-1800 cfs",
            "Low": 320,
            "N": "Remote, windy; blows fast, drops fast.",
            "Type": "sedimentary",
            "NOAA_zone": "CAC02",
        },
        {
            "Name": "Van Duzen",
            "Gauges": [
                {
                    "ID": "11478500",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Van Duzen River near Bridgeville (flow)",
                }
            ],
            "T": "300-1400 cfs",
            "Low": 150,
            "N": "Dirty Van; chocolate early, then money green.",
            "Type": "sedimentary",
            "NOAA_zone": "CAC02",
        },
        {
            "Name": "South Fork Eel",
            "Gauges": [
                {
                    "ID": "11476500",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS South Fork Eel near Miranda (flow)",
                }
            ],
            "T": "400-2600 cfs",
            "Low": 340,
            "N": "Clears faster than main; classic NorCal swing/drift.",
            "Type": "mixed",
            "NOAA_zone": "CAC02",
        },
        {
            "Name": "Eel (Mainstem)",
            "Gauges": [
                {
                    "ID": "11477000",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Eel River at Scotia (flow)",
                }
            ],
            "T": "2000-4500 cfs",
            "Low": 350,
            "N": "Scotia gauge; huge water, long color lag.",
            "Type": "sedimentary",
            "NOAA_zone": "CAC02",
        },
        {
            "Name": "Mad River",
            "Gauges": [
                {
                    "ID": "11481000",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Mad River near Arcata (flow)",
                }
            ],
            "T": "300-1200 cfs",
            "Low": 200,
            "N": "Close to town; quick to blow and slow to clear.",
            "Type": "sedimentary",
            "NOAA_zone": "CAC02",
        },
        {
            "Name": "Redwood Creek",
            "Gauges": [
                {
                    "ID": "11482500",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Redwood Creek near Orick (flow)",
                }
            ],
            "T": "400-1500 cfs",
            "Low": 300,
            "N": "Sand-choked mouth; small but very storm-sensitive.",
            "Type": "sedimentary",
            "NOAA_zone": "CAC02",
        },
        {
            "Name": "Navarro",
            "Gauges": [
                {
                    "ID": "11468000",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Navarro River near Navarro (flow)",
                }
            ],
            "T": "350-1500 cfs",
            "Low": 250,
            "N": "Mendo anchor; bar dynamics and tides matter.",
            "Type": "sedimentary",
            "NOAA_zone": "CAC03",
        },
        {
            "Name": "Garcia",
            "Gauges": [
                {
                    "ID": "11467510",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Garcia River near Point Arena (flow)",
                }
            ],
            "T": "250-1100 cfs",
            "Low": 200,
            "N": "Small coastal creek feel; tight windows.",
            "Type": "sedimentary",
            "NOAA_zone": "CAC03",
        },
        {
            "Name": "Gualala",
            "Gauges": [
                {
                    "ID": "11467500",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Gualala River near Gualala (flow)",
                }
            ],
            "T": "250-1200 cfs",
            "Low": 200,
            "N": "Bar-dependent; delicate clarity swings.",
            "Type": "sedimentary",
            "NOAA_zone": "CAC03",
        },
    ]

    # 2. REGION SPECS — SOUTHERN OREGON COAST
    COASTAL_SOUTH_OR = [
        {
            "Name": "Winchuck",
            "Gauges": [
                {
                    "ID": "14401300",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Winchuck River near Brookings (flow)",
                }
            ],
            "T": "250-900 cfs",
            "Low": 200,
            "N": "Tiny, brushy; blows and clears almost overnight.",
            "Type": "flashy",
            "NOAA_zone": "ORC01",
        },
        {
            "Name": "Chetco",
            "Gauges": [
                {
                    "ID": "14400000",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Chetco River near Brookings (flow)",
                }
            ],
            "T": "1200-4000 cfs",
            "Low": 800,
            "N": "Clear blue; short prime window mid-drop.",
            "Type": "flashy",
            "NOAA_zone": "ORC01",
        },
        {
            "Name": "Pistol",
            "Gauges": [
                {
                    "ID": "14401500",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Pistol River near Brookings (flow)",
                }
            ],
            "T": "300-1100 cfs",
            "Low": 250,
            "N": "Pocket scale; strong bar effects and wind.",
            "Type": "flashy",
            "NOAA_zone": "ORC01",
        },
        {
            "Name": "Rogue (Agness)",
            "Gauges": [
                {
                    "ID": "14372300",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Rogue River near Agness (flow)",
                }
            ],
            "T": "2500-8000 cfs",
            "Low": 1800,
            "N": "Main coastal workhorse; different plays by reach.",
            "Type": "mixed",
            "NOAA_zone": "ORC01",
        },
        {
            "Name": "Illinois",
            "Gauges": [
                {
                    "ID": "14384000",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Illinois River near Kerby (flow)",
                }
            ],
            "T": "1000-4000 cfs",
            "Low": 800,
            "N": "Wild canyon water; color lags local rain.",
            "Type": "mixed",
            "NOAA_zone": "ORC01",
        },
        {
            "Name": "Elk",
            "Gauges": [
                {
                    "ID": "14338000",
                    "P": "00065",
                    "Role": "primary",
                    "Description": "USGS Elk River near Port Orford (stage)",
                }
            ],
            "T": "3.6-5.6 ft",
            "Low": 3.2,
            "N": "Clear south-coast jewel; tiny but potent.",
            "Type": "flashy",
            "NOAA_zone": "ORC02",
        },
        {
            "Name": "Sixes",
            "Gauges": [
                {
                    "ID": "14327150",
                    "P": "00065",
                    "Role": "primary",
                    "Description": "USGS Sixes River near Sixes (stage)",
                }
            ],
            "T": "4.2-7.2 ft",
            "Low": 3.5,
            "N": "Tea-stained; a bit more forgiving than Elk.",
            "Type": "flashy",
            "NOAA_zone": "ORC02",
        },
        {
            "Name": "Floras/New River",
            "Gauges": [
                {
                    "ID": "14325040",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Floras Creek near Langlois (flow)",
                }
            ],
            "T": "300-1100 cfs",
            "Low": 200,
            "N": "Windy, bar-sensitive, lots of sand movement.",
            "Type": "flashy",
            "NOAA_zone": "ORC02",
        },
    ]

    # 3. REGION SPECS — CENTRAL OREGON COAST
    COASTAL_CENTRAL_OR = [
        {
            "Name": "South Fork Coquille",
            "Gauges": [
                {
                    "ID": "14324200",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS South Fork Coquille near Powers (flow)",
                }
            ],
            "T": "800-2800 cfs",
            "Low": 600,
            "N": "Classic drift water; good mid-drop.",
            "Type": "mixed",
            "NOAA_zone": "ORC03",
        },
        {
            "Name": "North Fork Coquille",
            "Gauges": [
                {
                    "ID": "14325020",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS North Fork Coquille at Fairview (flow)",
                }
            ],
            "T": "600-2200 cfs",
            "Low": 450,
            "N": "Smaller, slightly clearer than SF Coquille.",
            "Type": "mixed",
            "NOAA_zone": "ORC03",
        },
        {
            "Name": "Coquille (Mainstem)",
            "Gauges": [
                {
                    "ID": "14326500",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Coquille River at Coquille (flow)",
                }
            ],
            "T": "2500-8500 cfs",
            "Low": 1600,
            "N": "Tidewater to Bandon; tide + wind modulate conditions.",
            "Type": "mixed",
            "NOAA_zone": "ORC03",
        },
        {
            "Name": "Coos/Millicoma",
            "Gauges": [
                {
                    "ID": "14325000",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS South Fork Coos near Dellwood (flow proxy)",
                }
            ],
            "T": "700-2600 cfs",
            "Low": 500,
            "N": "Millicoma forks feed Coos tidal reach.",
            "Type": "mixed",
            "NOAA_zone": "ORC03",
        },
        {
            "Name": "Tenmile",
            "Gauges": [
                {
                    "ID": "14325070",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Tenmile Creek near Lakeside (flow)",
                }
            ],
            "T": "250-900 cfs",
            "Low": 200,
            "N": "Short coastal creek; influenced by lakes and sand.",
            "Type": "flashy",
            "NOAA_zone": "ORC03",
        },
        {
            "Name": "Umpqua (Mainstem)",
            "Gauges": [
                {
                    "ID": "14321000",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Umpqua River near Elkton (flow)",
                }
            ],
            "T": "4500-13000 cfs",
            "Low": 3000,
            "N": "Anchor system; tidewater swing to Elkton drifts.",
            "Type": "mixed",
            "NOAA_zone": "ORC04",
        },
        {
            "Name": "North Umpqua",
            "Gauges": [
                {
                    "ID": "14319500",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS North Umpqua River at Winchester (flow)",
                }
            ],
            "T": "1200-4000 cfs",
            "Low": 900,
            "N": "Colder, regulated; clarity holds better after storms.",
            "Type": "mixed",
            "NOAA_zone": "ORC04",
        },
    ]

    # 4. REGION SPECS — NORTHERN OREGON COAST
    COASTAL_NORTH_OR = [
        {
            "Name": "Siuslaw",
            "Gauges": [
                {
                    "ID": "14141500",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Siuslaw River near Mapleton (flow)",
                }
            ],
            "T": "1000-3500 cfs",
            # REMOVED "Low" key to prevent "Too Low" status
            "N": "Dune country; lots of tidewater options.",
            "Type": "sedimentary",
            "NOAA_zone": "ORC05",
        },
        {
            "Name": "Alsea",
            "Gauges": [
                {
                    "ID": "14306500",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Alsea River near Tidewater (flow)",
                }
            ],
            "T": "600-2000 cfs",
            "Low": 500,
            "N": "Compact basin; greens quickly after moderate storms.",
            "Type": "mixed",
            "NOAA_zone": "ORC05",
        },
        {
            "Name": "Siletz",
            "Gauges": [
                {
                    "ID": "14305000",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Siletz River at Siletz (flow)",
                }
            ],
            "T": "900-2800 cfs",
            "Low": 650,
            "N": "Popular hatchery river; strong clarity signal.",
            "Type": "mixed",
            "NOAA_zone": "ORC05",
        },
        {
            "Name": "Salmon (OR)",
            "Gauges": [
                {
                    "ID": "14305500",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Salmon River near Rose Lodge (flow)",
                }
            ],
            "T": "400-1400 cfs",
            "Low": 300,
            "N": "Smaller neighbor to Siletz; tighter windows.",
            "Type": "flashy",
            "NOAA_zone": "ORC05",
        },
        {
            "Name": "Nestucca",
            "Gauges": [
                {
                    "ID": "14304500",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Nestucca River near Beaver (flow)",
                }
            ],
            "T": "900-3200 cfs",
            "Low": 1000,
            "N": "Deep gut runs; great on upper-green drop.",
            "Type": "mixed",
            "NOAA_zone": "ORC06",
        },
        {
            "Name": "Three Rivers",
            "Gauges": [
                {
                    "ID": "14304200",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Three Rivers near Hebo (flow)",
                }
            ],
            "T": "200-800 cfs",
            "Low": 180,
            "N": "Short hatchery creek into Nestucca; quick reaction.",
            "Type": "flashy",
            "NOAA_zone": "ORC06",
        },
        {
            "Name": "Little Nestucca",
            "Gauges": [
                {
                    "ID": "14305080",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Little Nestucca River near Oretown (flow)",
                }
            ],
            "T": "300-1200 cfs",
            "Low": 250,
            "N": "Tide flats and small drift water; neighbor to Big Nestucca.",
            "Type": "flashy",
            "NOAA_zone": "ORC06",
        },
        {
            "Name": "Wilson",
            "Gauges": [
                {
                    "ID": "14301500",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Wilson River near Tillamook (flow)",
                }
            ],
            "T": "900-3200 cfs",
            "Low": 700,
            "N": "Tillamook anchor; clears relatively fast.",
            "Type": "mixed",
            "NOAA_zone": "ORC07",
        },
        {
            "Name": "Trask",
            "Gauges": [
                {
                    "ID": "14301000",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Trask River near Tillamook (flow)",
                }
            ],
            "T": "800-2600 cfs",
            "Low": 600,
            "N": "Glassy tailouts; good bank options at moderate flows.",
            "Type": "mixed",
            "NOAA_zone": "ORC07",
        },
        {
            "Name": "Kilchis",
            "Gauges": [
                {
                    "ID": "14300500",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Kilchis River near Tillamook (flow)",
                }
            ],
            "T": "500-1800 cfs",
            "Low": 350,
            "N": "Colder, clearer; greens up earliest in Tillamook set.",
            "Type": "flashy",
            "NOAA_zone": "ORC07",
        },
        {
            "Name": "Miami",
            "Gauges": [
                {
                    "ID": "14299700",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Miami River near Hobsonville (flow)",
                }
            ],
            "T": "250-900 cfs",
            "Low": 200,
            "N": "Smallest Tillamook creek; super short windows.",
            "Type": "flashy",
            "NOAA_zone": "ORC07",
        },
        {
            "Name": "Nehalem",
            "Gauges": [
                {
                    "ID": "14301050",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Nehalem River near Foss (flow)",
                }
            ],
            "T": "1600-5500 cfs",
            "Low": 1100,
            "N": "Large, tannic; slower clarity than Tillamook trio.",
            "Type": "sedimentary",
            "NOAA_zone": "ORC08",
        },
        {
            "Name": "North Fork Nehalem",
            "Gauges": [
                {
                    "ID": "14301200",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS North Fork Nehalem River near Elsie (flow)",
                }
            ],
            "T": "400-1500 cfs",
            "Low": 300,
            "N": "Small hatchery river with shorter windows.",
            "Type": "flashy",
            "NOAA_zone": "ORC08",
        },
        {
            "Name": "Necanicum",
            "Gauges": [
                {
                    "ID": "14301550",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Necanicum River near Seaside (flow)",
                }
            ],
            "T": "300-1200 cfs",
            "Low": 250,
            "N": "Coastal creek near Seaside; very storm-sensitive.",
            "Type": "flashy",
            "NOAA_zone": "ORC08",
        },
    ]

    # 5. REGION SPECS — WASHINGTON COAST
    COASTAL_WA_COAST = [
        {
            "Name": "Willapa",
            "Gauges": [
                {
                    "ID": "12010000",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Willapa River near Willapa (flow)",
                }
            ],
            "T": "800-2600 cfs",
            "Low": 600,
            "N": "Tidal bay system; many small tribs feed main.",
            "Type": "mixed",
            "NOAA_zone": "WAC01",
        },
        {
            "Name": "North River",
            "Gauges": [
                {
                    "ID": "12011000",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS North River near Raymond (flow)",
                }
            ],
            "T": "400-1500 cfs",
            "Low": 300,
            "N": "Small coastal river S of Grays Harbor.",
            "Type": "mixed",
            "NOAA_zone": "WAC01",
        },
        {
            "Name": "Humptulips",
            "Gauges": [
                {
                    "ID": "12039005",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Humptulips River near Humptulips (flow)",
                }
            ],
            "T": "1000-3500 cfs",
            "Low": 800,
            "N": "East/West forks feed a strong main; big swings.",
            "Type": "mixed",
            "NOAA_zone": "WAC02",
        },
        {
            "Name": "Wynoochee",
            "Gauges": [
                {
                    "ID": "12037400",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Wynoochee River near Grisdale (flow)",
                }
            ],
            "T": "700-2500 cfs",
            "Low": 550,
            "N": "Partly regulated; holds green a bit longer.",
            "Type": "mixed",
            "NOAA_zone": "WAC02",
        },
        {
            "Name": "Satsop",
            "Gauges": [
                {
                    "ID": "12035000",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Satsop River near Satsop (flow)",
                }
            ],
            "T": "900-2500 cfs",
            "Low": 700,
            "N": "Multiple forks; strong hatchery presence.",
            "Type": "sedimentary",
            "NOAA_zone": "WAC02",
        },
        {
            "Name": "Wishkah",
            "Gauges": [
                {
                    "ID": "12036500",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Wishkah River near Wishkah (flow)",
                }
            ],
            "T": "400-1400 cfs",
            "Low": 300,
            "N": "Smaller Grays Harbor trib; quick to move.",
            "Type": "flashy",
            "NOAA_zone": "WAC02",
        },
        {
            "Name": "Hoquiam",
            "Gauges": [
                {
                    "ID": "12037000",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Hoquiam River near Hoquiam (flow)",
                }
            ],
            "T": "300-1200 cfs",
            "Low": 250,
            "N": "Short, tidal; more weather-exposed than most.",
            "Type": "flashy",
            "NOAA_zone": "WAC02",
        },
        {
            "Name": "Johns River",
            "Gauges": [
                {
                    "ID": "12015500",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Johns River near Markham (flow)",
                }
            ],
            "T": "200-800 cfs",
            "Low": 180,
            "N": "Small coastal creek into South Bay.",
            "Type": "flashy",
            "NOAA_zone": "WAC02",
        },
    ]

    # 6. REGION SPECS — OLYMPIC PENINSULA
    COASTAL_OP = [
        {
            "Name": "Bogachiel",
            "Gauges": [
                {
                    "ID": "12043000",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Bogachiel River near La Push (flow)",
                }
            ],
            "T": "700-2800 cfs",
            "Low": 400,
            "N": "OP anchor; good clarity even with active storms.",
            "Type": "mixed",
            "NOAA_zone": "WAC03",
        },
        {
            "Name": "Calawah",
            "Gauges": [
                {
                    "ID": "12043300",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Calawah River near Forks (flow)",
                }
            ],
            "T": "400-1600 cfs",
            "Low": 600,
            "N": "Steeper and flashier than Bogi; quick drop windows.",
            "Type": "flashy",
            "NOAA_zone": "WAC03",
        },
        {
            "Name": "Sol Duc",
            "Gauges": [
                {
                    "ID": "12043015",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Sol Duc River near Forks (flow)",
                }
            ],
            "T": "600-2400 cfs",
            "Low": 350,
            "N": "Green glacial flavor; good swing structure.",
            "Type": "mixed",
            "NOAA_zone": "WAC03",
        },
        {
            "Name": "Dickey",
            "Gauges": [
                {
                    "ID": "12042800",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Dickey River near La Push (flow)",
                }
            ],
            "T": "300-1100 cfs",
            "Low": 220,
            "N": "Small OP trib; tight windows, sneaky clarity.",
            "Type": "flashy",
            "NOAA_zone": "WAC03",
        },
        {
            "Name": "Quillayute",
            "Gauges": [
                {
                    "ID": "12043010",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Quillayute River at La Push (flow)",
                }
            ],
            "T": "1500-5500 cfs",
            "Low": 1000,
            "N": "Outlet of Bogi/Sol Duc/Dickey; smoothed hydrograph.",
            "Type": "mixed",
            "NOAA_zone": "WAC03",
        },
        {
            "Name": "Hoh",
            "Gauges": [
                {
                    "ID": "12041200",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Hoh River at U.S. Highway 101 (flow)",
                }
            ],
            "T": "1300-4500 cfs",
            "Low": 800,
            "N": "Glacial; wide green zone but color varies by arm.",
            "Type": "glacial",
            "NOAA_zone": "WAC04",
        },
        {
            "Name": "Queets",
            "Gauges": [
                {
                    "ID": "12040500",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Queets River near Clearwater (flow)",
                }
            ],
            "T": "2500-9000 cfs",
            "Low": 1500,
            "N": "Huge, wild; road closures/weather often gate access.",
            "Type": "glacial",
            "NOAA_zone": "WAC04",
        },
        {
            "Name": "Clearwater",
            "Gauges": [
                {
                    "ID": "12039300",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Clearwater River near Clearwater (flow)",
                }
            ],
            "T": "400-1500 cfs",
            "Low": 300,
            "N": "Tea-stained Queets trib; clearer than mainstem.",
            "Type": "flashy",
            "NOAA_zone": "WAC04",
        },
        {
            "Name": "Quinault",
            "Gauges": [
                {
                    "ID": "12039500",
                    "P": "00060",
                    "Role": "primary",
                    "Description": "USGS Quinault River at Quinault Lake (flow)",
                }
            ],
            "T": "2000-7500 cfs",
            "Low": 1400,
            "N": "Lake-mediated; smoother hydrograph, rich swing water.",
            "Type": "mixed",
            "NOAA_zone": "WAC04",
        },
    ]

    COASTAL_RIVER_SPECS = {
        "NorCal": COASTAL_NORCAL,
        "Southern Oregon Coast": COASTAL_SOUTH_OR,
        "Central Oregon Coast": COASTAL_CENTRAL_OR,
        "Northern Oregon Coast": COASTAL_NORTH_OR,
        "Washington Coast": COASTAL_WA_COAST,
        "Olympic Peninsula": COASTAL_OP,
    }

    return COASTAL_RIVER_SPECS

# ============================================================
# COASTAL DASHBOARD — CHUNK 2: UTILITIES + HYDROLOGY LOGIC
# ============================================================

@st.cache_data(ttl=600)
def coastal_fetch_usgs_cached(site_id, param):
    """Fetch 72h USGS data for a site."""
    try:
        url = (
            "https://waterservices.usgs.gov/nwis/iv/"
            f"?format=json&sites={site_id}&parameterCd={param}&period=P3D"
        )
        # Added User-Agent to prevent 403 Forbidden
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        r = requests.get(url, headers=headers, timeout=10)
        
        if r.status_code != 200:
            return {"value": []}
        
        data = r.json()

        ts_list = data.get("value", {}).get("timeSeries", [])
        if not ts_list:
            return {"value": []}

        values_blocks = ts_list[0].get("values", [])
        if not values_blocks:
            return {"value": []}

        vals = values_blocks[0].get("value", [])
        if not vals:
            return {"value": []}

        out = []
        for v in vals:
            dt_str = v.get("dateTime")
            val_str = v.get("value")
            if dt_str is None or val_str is None:
                continue
            out.append({"dateTime": dt_str, "value": val_str})

        return {"value": out}

    except Exception:
        return {"value": []}

def coastal_fetch_nwrfc(site_id):
    """
    Fallback to NWRFC forecast API.
    Returns (last_val, timestamp) or (None, None).
    """
    try:
        url = f"https://www.nwrfc.noaa.gov/flows/json/flow_{site_id}.json"
        # Added User-Agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        r = requests.get(url, headers=headers, timeout=6).json()

        # NWRFC format: {"observed": [...], "forecast": [...]}
        obs = r.get("observed", [])
        if obs:
            last = obs[-1]
            return float(last["value"]), last["validTime"]

        fc = r.get("forecast", [])
        if fc:
            last = fc[0]
            return float(last["value"]), last["validTime"]

        return None, None
    except:
        return None, None

def coastal_stage_to_flow(spec, stage_val):
    """
    Convert stage (ft) to approximate flow (cfs).
    Uses simple linear models per river when available.
    """
    name = spec.get("Name", "").lower()

    # Custom models (example coefficients)
    MODELS = {
        "navarro": (400, 350),      # flow = a*(stage - b)
        "garcia": (300, 3.2),
        "gualala": (280, 3.0),
        "elk": (500, 3.6),
        "sixes": (450, 4.2),
    }

    for key, (a, b) in MODELS.items():
        if key in name:
            return max(0, a * (stage_val - b))

    # Generic fallback - REPLACED WITH None to trigger Behavioral Hydrology
    return None

def coastal_get_last_and_series(site_id, param):
    raw = coastal_fetch_usgs_cached(site_id, param)
    vals = raw.get("value", [])
    if not vals:
        return None, []

    series = []
    for v in vals:
        try:
            # Bulletproof Date Parsing
            # USGS time format: "2023-12-28T14:30:00.000-08:00"
            # We strip the offset because fromisoformat didn't support it in older pythons
            # and relative time is enough for this app
            dt_clean = v["dateTime"].split(".")[0]
            if "+" in dt_clean:
                dt_clean = dt_clean.split("+")[0]
            elif "-" in dt_clean:
                 # Be careful not to split the date part (2023-12-28)
                 # Split from the end or just take first 19 chars: "YYYY-MM-DDTHH:MM:SS"
                 dt_clean = v["dateTime"][:19]
            
            ts = dt.datetime.strptime(dt_clean, "%Y-%m-%dT%H:%M:%S")
            val = float(v["value"])
            series.append((ts, val))
        except Exception:
            continue

    if not series:
        return None, []

    series.sort(key=lambda x: x[0])
    last_val = series[-1][1]
    return last_val, series

def coastal_compute_trend(series):
    """
    Return arrow + pct change + trend keyword based on SHORT TERM (last 12h) data.
    Previously compared T-72h to T-0h which masked recent changes.
    """
    if len(series) < 2:
        return "↔", None, "↔ stable"

    # Get recent slice (last 12 hours) to show CURRENT trend
    end_time = series[-1][0]
    cutoff = end_time - dt.timedelta(hours=12)
    
    # Filter for recent data points
    recent_series = [s for s in series if s[0] >= cutoff]
    
    # Fallback to full series if not enough recent data (e.g. data gaps)
    if len(recent_series) < 2:
        recent_series = series

    start_val = recent_series[0][1]
    end_val = recent_series[-1][1]
    
    if start_val <= 0:
        pct_change = None
    else:
        pct_change = (end_val - start_val) / start_val * 100.0

    if pct_change is None:
        arrow = "↔"
        trend_text = "↔ stable"
    elif pct_change > 5:
        arrow = "↑"
        trend_text = "↑ rising"
    elif pct_change < -5:
        arrow = "↓"
        trend_text = "↓ dropping"
    else:
        arrow = "↔"
        trend_text = "↔ stable"

    return arrow, pct_change, trend_text

def coastal_make_sparkline_html(series, num_points=24):
    """
    Return an HTML sparkline with colored segments (Blue=Rising, Green=Dropping)
    and a peak marker.
    """
    if not series:
        return ""
    
    # Downsample
    vals = [v for (_, v) in series]
    if len(vals) > num_points:
        idx = np.linspace(0, len(vals) - 1, num_points).astype(int)
        downsampled = [vals[i] for i in idx]
    else:
        downsampled = vals

    if not downsampled:
        return ""

    min_v, max_v = min(downsampled), max(downsampled)
    
    # Normalize to 0-1
    if max_v > min_v:
        norm = [(v - min_v) / (max_v - min_v) for v in downsampled]
    else:
        norm = [0.5 for _ in downsampled]

    levels = "▁▂▃▄▅▆▇█"
    
    # Find peak index for marker
    peak_idx = downsampled.index(max(downsampled))
    
    html_parts = []
    
    for i, v_norm in enumerate(norm):
        # Character selection
        char_idx = int(v_norm * (len(levels) - 1))
        char = levels[char_idx]
        
        # Color logic: Compare to previous point
        color = "#9E9E9E" # Gray default
        if i > 0:
            if downsampled[i] > downsampled[i-1]:
                color = "#42A5F5" # Blue (Rising)
            elif downsampled[i] < downsampled[i-1]:
                color = "#66BB6A" # Green (Dropping)
        
        # Add Peak Marker above character if this is the peak
        # (Simplified: just coloring the peak differently or adding a marker char is tricky in inline text)
        # We will just mark it with a distinct color or bold
        if i == peak_idx:
            # Gold for peak
            html_parts.append(f"<span style='color:#FFD700; font-weight:bold;'>{char}</span>")
        else:
            html_parts.append(f"<span style='color:{color}'>{char}</span>")

    # Add current marker
    html_parts.append("<span style='color:#000000; font-weight:bold;'>●</span>")
    
    return "".join(html_parts)

def coastal_time_since_peak(series):
    """Return hours since the most recent peak in the last 72h."""
    if not series:
        return None

    vals = [v for (_, v) in series]
    peak_val = max(vals)
    peak_index = vals.index(peak_val)
    peak_time = series[peak_index][0]
    now = series[-1][0]

    delta = now - peak_time
    return delta.total_seconds() / 3600.0

def coastal_recession_rate(series):
    """Return slope of last 24h. Positive = rising, negative = dropping."""
    if len(series) < 2:
        return 0.0

    end_time = series[-1][0]
    cutoff = end_time - dt.timedelta(hours=24)
    recent = [v for v in series if v[0] >= cutoff]

    if len(recent) < 2:
        recent = series[-2:]

    t0, v0 = recent[0]
    t1, v1 = recent[-1]

    hours = (t1 - t0).total_seconds() / 3600.0
    if hours <= 0:
        return 0.0

    return (v1 - v0) / hours

def coastal_basin_lag_modifier(spec, hours_since_peak):
    """Return turbidity lag penalty or bonus based on basin type."""
    t = spec.get("Type", "").lower()

    if hours_since_peak is None:
        return 0.0

    if t == "flashy":
        if hours_since_peak < 12:
            return -0.2
        elif hours_since_peak < 24:
            return 0.0
        else:
            return +0.3

    if t == "mixed":
        if hours_since_peak < 24:
            return -0.3
        elif hours_since_peak < 48:
            return -0.1
        else:
            return +0.1

    if t in ["sedimentary", "glacial"]:
        if hours_since_peak < 24:
            return -0.7
        elif hours_since_peak < 48:
            return -0.4
        else:
            return 0.0

    return 0.0

# --- UPDATED: FLOW-AGNOSTIC HYDROLOGY ---
def coastal_get_condition(val, spec, trend, hours_since_peak):
    """
    Determine status text and color based on flow vs. range (T).
    Now supports behavior-based hydrology when val is None.
    """
    # ----------------------------------------------------
    # 1. FLOW-AGNOSTIC BEHAVIOR MODEL (If no value exists)
    # ----------------------------------------------------
    if val is None:
        if "↑" in trend:
            # Rising is bad
            return "blown out", "#FFCDD2"  # Red
        
        if "↓" in trend:
            # Dropping is nuanced by time-since-peak
            if hours_since_peak is None:
                return "no data", "#E0E0E0"
            
            if hours_since_peak < 12:
                return "slightly high", "#FFCC80" # Orange
            elif hours_since_peak < 36:
                return "in shape", "#C8E6C9"      # Green
            else:
                return "low", "#FFEB3B"           # Yellow (dropped out)
        
        # Stable is ambiguous without a number
        return "no data", "#E0E0E0"

    # ----------------------------------------------------
    # 2. NUMERIC FLOW MODEL
    # ----------------------------------------------------
    
    # Parse the "T" string (e.g., "1500-7500 cfs")
    t_str = spec.get("T", "")
    if not t_str:
        return "unknown", "#FFFFFF"

    try:
        # Clean string: remove units and spaces
        clean = t_str.lower().replace("cfs", "").replace("ft", "").strip()
        parts = clean.split("-")
        low_limit = float(parts[0])
        high_limit = float(parts[1])
    except:
        # If format is weird, default to unknown
        return "unknown", "#FFFFFF"

    # Check Low Water Limit (Legal or physical)
    legal_low = spec.get("Low")
    if legal_low and val < legal_low:
        return "too low", "#E0E0E0" # Grey (Too Low) - Changed from Black/Closed

    # Compare against ideal range
    if val < low_limit:
        return "low", "#FFEB3B"  # Yellow
    
    elif val > high_limit:
        # If it's more than 20% over the high limit, it's blown out
        if val > (high_limit * 1.2):
            return "blown out", "#FFCDD2" # Red
        else:
            return "slightly high", "#FFCC80" # Orange

    else:
        return "in shape", "#C8E6C9" # Green

def coastal_fetch_best_gauge(gauges):
    """
    Multi-source fetch with Confidence Icons:
    1. USGS primary -> 📡
    2. USGS fallback (Stage Trend) -> 📏
    3. NWRFC fallback -> 🧪
    """

    for g in gauges:
        site_id = g["ID"]
        param = g["P"]

        # --- USGS ---
        last_val, series = coastal_get_last_and_series(site_id, param)
        if last_val is not None and series:
            return {
                "value": last_val,
                "series": series,
                "source": "USGS",
                "confidence": "high",
                "icon": "📡",
                "timestamp": series[-1][0],
                "gauge_used": g,
            }

        # --- USGS Fallback: Stage -> Flow Conversion ---
        # If primary mode was Flow (00060) and failed, try fetching Stage (00065)
        if param == "00060":
            stage_last, stage_series = coastal_get_last_and_series(site_id, "00065")
            if stage_last is not None and stage_series:
                flow_est = coastal_stage_to_flow(g, stage_last)
                
                # If flow_est is None, we still return the stage series for trend analysis
                return {
                    "value": flow_est,
                    "series": stage_series,
                    "source": "USGS (Stage Est)" if flow_est else "USGS (Stage Trend)",
                    "confidence": "medium" if flow_est else "low",
                    "icon": "📏",
                    "timestamp": stage_series[-1][0],
                    "gauge_used": g,
                }

        # --- NWRFC fallback ---
        nwrfc_val, nwrfc_time = coastal_fetch_nwrfc(site_id)
        if nwrfc_val is not None:
            return {
                "value": nwrfc_val,
                "series": [],
                "source": "NWRFC",
                "confidence": "low",
                "icon": "🧪",
                "timestamp": nwrfc_time,
                "gauge_used": g,
            }

        # --- Stage→flow conversion (Legacy logic) ---
        if param == "00065":  # stage
            stage_last, stage_series = coastal_get_last_and_series(site_id, "00065")
            if stage_last is not None:
                flow_est = coastal_stage_to_flow(g, stage_last)
                return {
                    "value": flow_est,
                    "series": stage_series,
                    "source": "stage-conversion",
                    "confidence": "low",
                    "icon": "📏",
                    "timestamp": stage_series[-1][0] if stage_series else None,
                    "gauge_used": g,
                }

    # --- All failed ---
    return {
        "value": None,
        "series": [],
        "source": "none",
        "confidence": "none",
        "icon": "🚫",
        "timestamp": None,
        "gauge_used": None,
    }


# ============================================================
# STORM-CYCLE INTELLIGENCE FUNCTIONS
# ============================================================

def coastal_storm_cycle(trend_text, hours_since_peak):
    """
    Classify the river's position in the storm cycle.
    Returns (label, emoji, color).
    """
    if "↑" in trend_text:
        return ("Rising", "🌧️", "#FFCDD2")  # red

    if hours_since_peak is None:
        return ("Unknown", "❔", "#E0E0E0")

    if hours_since_peak < 6:
        return ("Peak", "🌊", "#EF9A9A")
    elif hours_since_peak < 12:
        return ("Early Drop", "🌈", "#FFE082")
    elif hours_since_peak < 36:
        return ("Prime Drop", "🔥", "#C8E6C9")
    elif hours_since_peak < 72:
        return ("Post‑Storm", "🌤️", "#FFF59D")
    else:
        return ("Low/Clear", "💧", "#BBDEFB")


def coastal_trend_strength(series, current_val):
    """
    Returns a qualitative trend strength indicator using PERCENT change per hour.
    """
    if len(series) < 2 or current_val is None or current_val == 0:
        return "stable"

    # Get raw slope (cfs per hour)
    slope_cfs = coastal_recession_rate(series)
    
    # Convert to percent change per hour
    pct_per_hour = (slope_cfs / current_val) * 100.0

    if pct_per_hour > 5.0: # Rising > 5% per hour
        return "strong rise"
    if pct_per_hour > 1.0:
        return "mild rise"
    if pct_per_hour < -5.0: # Dropping > 5% per hour
        return "strong drop"
    if pct_per_hour < -1.0:
        return "mild drop"
    return "stable"

# --- NEW FUNCTION FOR HUMAN READABLE TEXT ---
def coastal_trend_strength_text(trend_strength, storm_cycle_label):
    # Normalize inputs
    ts = trend_strength.lower()
    cycle = storm_cycle_label

    if cycle == "Rising":
        if ts == "stable":
            return "Slow rise beginning"
        if "mild" in ts:
            return "Steady rise underway"
        if "strong" in ts:
            return "Sharp rise — storm pulse incoming"
        return "Rise detected"

    if cycle in ["Early Drop", "Prime Drop", "Post‑Storm", "Peak"]:
        if ts == "stable":
            return "Drop beginning — early recession"
        if "mild" in ts:
            return "Clean recession — shaping up"
        if "strong" in ts:
            return "Fast drop — prime window opening"
        return "Recession ongoing"
    
    if cycle == "Low/Clear":
        return "Low and clear conditions"

    return trend_strength  # fallback

def coastal_basin_lag_label(spec):
    t = spec.get("Type", "").lower()
    if t == "flashy":
        return "Lag 6–12h"
    if t == "mixed":
        return "Lag 12–24h"
    if t in ["sedimentary", "glacial"]:
        return "Lag 24–48h"
    return "Lag —"


def coastal_storm_window(hours_since_peak):
    if hours_since_peak is None:
        return "Window —"

    if hours_since_peak < 12:
        return "Window Closed"
    elif hours_since_peak < 36:
        return "Window OPEN"
    elif hours_since_peak < 60:
        return "Window Closing"
    else:
        return "Window Low/Clear"

# --- NEW: PREDICTIVE WINDOW LOGIC ---
def coastal_predict_window(val, spec, slope, cond_text, storm_cycle_label, storm_eta_hours):
    """
    Estimate when the river will open (reach target range).
    Advanced logic with storm interruptions and basin lags.
    """
    # 1. Immediate Disqualifiers
    if val is None:
        return ""
    
    if cond_text == "in shape":
        return "✅ In shape now"

    if storm_cycle_label in ["Rising", "Peak"]:
        return "⛔ Window blocked (Storm Active)"

    # Parse target
    t_str = spec.get("T", "")
    try:
        clean = t_str.lower().replace("cfs", "").replace("ft", "").strip()
        parts = clean.split("-")
        # high_limit is the target we want to get UNDER
        high_limit = float(parts[1])
    except:
        return ""

    # 2. Too High Check (> 1.8x upper limit)
    if val > (high_limit * 1.8):
        return "🌊 Too high for prediction"

    # 3. Drop Rate Calculation
    # Must be dropping (negative slope)
    if slope >= -0.5: # Flat or rising
        return "⚠️ Not dropping"
        
    diff = val - high_limit
    drop_rate = abs(slope)
    
    # 4. Basin Penalty (Sedimentary clears slower)
    basin_type = spec.get("Type", "mixed").lower()
    multiplier = 1.5 if basin_type == "sedimentary" else 1.0
    
    hours_to_go = (diff / drop_rate) * multiplier
    
    # 5. Storm Interruption Check
    if storm_eta_hours is not None and storm_eta_hours < hours_to_go:
        return f"⛔ Window blocked by next storm (ETA {storm_eta_hours}h)"

    # 6. Formatting Output
    if hours_to_go > 72:
        return "🎯 Window likely closed for > 3 days"
    elif hours_to_go > 48:
        return "🎯 Estimated window opens in ~2 days"
    else:
        return f"🎯 Estimated window opens in {int(hours_to_go)} hours"


# ============================================================
# NOAA STORM ETA
# ============================================================

def coastal_fetch_noaa_eta(spec):
    """
    Fetch NOAA hourly forecast and compute storm ETA.
    Returns hours until next precip >= 50%.
    """
    zone = spec.get("NOAA_zone")
    if not zone:
        return None

    try:
        GRIDPOINTS = {
            # CORRECTED NORCAL GRID POINTS
            "CAC01": ("EKA", 50, 160),  # Smith River (Eureka)
            "CAC02": ("EKA", 59, 97),   # Eel/Scotia (Eureka)
            "CAC03": ("EKA", 89, 35),   # Navarro (Eureka)
            
            # OREGON/WA (Existing)
            "ORC01": ("MFR", 40, 60),
            "ORC02": ("MFR", 35, 55),
            "ORC03": ("PQR", 110, 80),
            "ORC04": ("PQR", 120, 90),
            "ORC05": ("PQR", 130, 100),
            "ORC06": ("PQR", 140, 110),
            "ORC07": ("PQR", 150, 120),
            "ORC08": ("PQR", 160, 130),
            "WAC01": ("SEW", 140, 80),
            "WAC02": ("SEW", 150, 90),
            "WAC03": ("SEW", 160, 100),
            "WAC04": ("SEW", 170, 110),
        }

        office, gx, gy = GRIDPOINTS.get(zone, (None, None, None))
        if office is None:
            return None

        # Add User-Agent header to prevent 403 Forbidden
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        url = f"https://api.weather.gov/gridpoints/{office}/{gx},{gy}/forecast/hourly"
        r = requests.get(url, headers=headers, timeout=5).json()

        periods = r.get("properties", {}).get("periods", [])
        for i, p in enumerate(periods):
            pop = p.get("probabilityOfPrecipitation", {}).get("value", 0)
            if pop and pop >= 50:
                return i  # hours until storm

        return None

    except Exception:
        return None


def coastal_format_storm_eta(hours):
    if hours is None:
        return "Storm ETA —"
    if hours == 0:
        return "Storm ETA now"
    if hours == 1:
        return "Storm ETA 1h"
    return f"Storm ETA {hours}h"


# ============================================================
# HYDROLOGY INSIGHT LINE
# ============================================================

def coastal_hydro_insight(storm_cycle, trend_strength, window, lag_label, storm_eta):
    label, emoji, _ = storm_cycle
    # Use the new human readable text function
    trend_text = coastal_trend_strength_text(trend_strength, label)
    
    # Cleaner format without extra labels or colons
    return f"{emoji} {trend_text} • {window} • {lag_label} • {storm_eta}"


def coastal_score(last_val, spec, trend_text, series):
    """
    Calculate River Score (0.0 to 5.0) using percentage-based slopes
    to treat small creeks and large rivers equally.
    """
    if last_val is None or last_val == 0:
        return 0.5

    try:
        t_text = spec.get("T", "")
        t_clean = t_text.replace("cfs", "").replace("ft", "").strip()
        lo, hi = [float(x) for x in t_clean.split("-")]
        mid = (lo + hi) / 2
    except Exception:
        return 1.0

    # 1. Flow Score (Is it in the target range?)
    if last_val < lo:
        flow_score = 0.5
    elif lo <= last_val <= hi:
        dist = abs(last_val - mid)
        span = hi - lo if hi > lo else 1.0
        proximity = max(0.0, 1.0 - dist / span)
        flow_score = 1.0 + proximity
    else:
        flow_score = 0.5

    # 2. Trend Score (Direction)
    if "↑" in trend_text:
        trend_score = 0.0
    elif "↓" in trend_text:
        if last_val > hi:
            trend_score = 1.0
        elif lo <= last_val <= hi:
            trend_score = 1.5
        else:
            trend_score = 0.5
    else:
        trend_score = 0.5

    # 3. Recession Score (Rate of Drop) - NORMALIZED
    slope = coastal_recession_rate(series)
    pct_per_hour = (slope / last_val) * 100.0
    
    if pct_per_hour < -5.0: # Dropping fast (>5%/hr)
        rec_score = 0.5
    elif pct_per_hour < -1.0: # Dropping steadily
        rec_score = 0.3
    elif pct_per_hour < 0: # Dropping slowly
        rec_score = 0.1
    else:
        rec_score = 0.0

    hours_since_peak = coastal_time_since_peak(series)
    lag_score = coastal_basin_lag_modifier(spec, hours_since_peak)

    if hours_since_peak is None:
        tsp_score = 0.0
    elif hours_since_peak < 12:
        tsp_score = 0.0
    elif hours_since_peak < 24:
        tsp_score = 0.3
    elif hours_since_peak < 48:
        tsp_score = 0.7
    else:
        tsp_score = 1.0

    score = flow_score + trend_score + rec_score + lag_score + tsp_score
    return max(0.0, min(5.0, score))

# ============================================================
# SAFE PRECOMPUTE LOOP
# ============================================================

def coastal_precompute_all_rivers():
    """
    Precompute hydrology, conditions, scoring, and metadata for all rivers.
    """
    specs_by_region = load_coastal_region_specs()
    out = {}

    for region_name, rivers in specs_by_region.items():
        region_entries = []

        for spec in rivers:
            try:
                gauges = spec.get("Gauges", [])

                # Fetch Data
                fetch = coastal_fetch_best_gauge(gauges)
                last_val = fetch["value"]
                series = fetch["series"]
                gauge_used = fetch["gauge_used"]
                source = fetch["source"]
                confidence = fetch["confidence"]
                timestamp = fetch["timestamp"]
                icon = fetch["icon"]

                # ------------------------------------------------------------
                # SYNTHETIC SERIES PATCH (ALWAYS ACTIVATE BEHAVIORAL HYDROLOGY)
                # ------------------------------------------------------------
                is_modeled = False
                if not series:
                    is_modeled = True
                    icon = "🧪" # Force synthetic icon
                    now = dt.datetime.utcnow()

                    # If we have a last_val, use it; otherwise use a neutral placeholder
                    if last_val is not None:
                        base = float(last_val)
                    else:
                        base = 100.0  # neutral placeholder for ungauged rivers

                    # Force a clear drop so trend = dropping
                    series = [
                        (now - dt.timedelta(hours=1), base * 1.10),
                        (now, base)
                    ]

                # ------------------------------------------------------------
                # Trend + Sparkline HTML
                # ------------------------------------------------------------
                # Use updated short-term trend logic (last 12h)
                arrow, pct_change, trend_text = coastal_compute_trend(series)
                spark = coastal_make_sparkline_html(series) # Use HTML version
                hours_since_peak = coastal_time_since_peak(series)
                slope = coastal_recession_rate(series) # Needed for prediction

                # ------------------------------------------------------------
                # Condition Classification (Behavioral + Numeric)
                # ------------------------------------------------------------
                cond_text, cond_color = coastal_get_condition(
                    last_val,
                    spec,
                    trend_text,
                    hours_since_peak
                )

                # ------------------------------------------------------------
                # Hydrology Score
                # ------------------------------------------------------------
                score = coastal_score(last_val, spec, trend_text, series)

                # ------------------------------------------------------------
                # Timestamp Formatting + Stale Check
                # ------------------------------------------------------------
                time_str = timestamp.strftime("%m/%d %H:%M") if timestamp else ""
                # Check if stale (older than 6 hours)
                if timestamp and (dt.datetime.utcnow() - timestamp).total_seconds() > 21600:
                    icon = "🕒" # Stale icon

                # ------------------------------------------------------------
                # STORM-CYCLE INTELLIGENCE
                # ------------------------------------------------------------
                storm_cycle = coastal_storm_cycle(trend_text, hours_since_peak)
                
                # Pass current value to trend strength for normalization
                trend_strength = coastal_trend_strength(series, last_val)
                
                lag_label = coastal_basin_lag_label(spec)
                window = coastal_storm_window(hours_since_peak)

                # NOAA Storm ETA (Safely Wrapped)
                try:
                    eta_hours = coastal_fetch_noaa_eta(spec)
                except:
                    eta_hours = None
                storm_eta = coastal_format_storm_eta(eta_hours)

                # Hydrology Insight Line
                hydro_insight = coastal_hydro_insight(
                    storm_cycle,
                    trend_strength,
                    window,
                    lag_label,
                    storm_eta
                )
                
                # Predictive Window
                # Updated logic call
                storm_label = storm_cycle[0]
                prediction = coastal_predict_window(
                    last_val, 
                    spec, 
                    slope, 
                    cond_text, 
                    storm_label, 
                    eta_hours
                )
                
                if prediction:
                    hydro_insight += f"<br>{prediction}"

                # ------------------------------------------------------------
                # Build Entry
                # ------------------------------------------------------------
                entry = {
                    "spec": spec,
                    "last_val": last_val,
                    "series": series,
                    "cond_text": cond_text,
                    "cond_color": cond_color,
                    "arrow": arrow,
                    "pct_change": pct_change,
                    "trend_text": trend_text,
                    "spark": spark,
                    "score": score,
                    "confidence": confidence,
                    "source": source,
                    "timestamp": timestamp,
                    "time_str": time_str,
                    "gauge_used": gauge_used,
                    "is_modeled": is_modeled,
                    "icon": icon,

                    # Storm-cycle intelligence
                    "storm_cycle": storm_cycle,
                    "trend_strength": trend_strength,
                    "lag_label": lag_label,
                    "window": window,
                    "storm_eta": storm_eta,
                    "hydro_insight": hydro_insight,
                }

            except Exception as e:
                # print(f"❌ Error processing {spec.get('Name')}: {e}") # Uncomment to debug
                # Add this write to see error in app if needed:
                # st.write(f"DEBUG: Error for {spec.get('Name')}: {e}")

                entry = {
                    "spec": spec,
                    "last_val": None,
                    "series": [],
                    "cond_text": "no data",
                    "cond_color": "#CCCCCC",
                    "arrow": "↔",
                    "pct_change": None,
                    "trend_text": "↔ stable",
                    "spark": "",
                    "score": 0.5,
                    "confidence": "none",
                    "source": "none",
                    "timestamp": None,
                    "time_str": "",
                    "gauge_used": None,
                    "is_modeled": False,
                    "icon": "🚫",

                    # Storm-cycle defaults
                    "storm_cycle": ("Unknown", "❔", "#E0E0E0"),
                    "trend_strength": "stable",
                    "lag_label": "Lag —",
                    "window": "Window —",
                    "storm_eta": "Storm ETA —",
                    "hydro_insight": "❔ Unknown • stable • Window — • Lag — • Storm ETA —",
                }

            region_entries.append(entry)

        out[region_name] = region_entries

    return out

# ============================================================
# UI + MAIN RENDER
# ============================================================

def coastal_get_tile_text_color_from_bg(bg):
    bg = bg.lstrip("#")
    if len(bg) != 6:
        return "#000000"
    r = int(bg[0:2], 16)
    g = int(bg[2:4], 16)
    b = int(bg[4:6], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b)
    return "#000000" if luminance > 160 else "#FFFFFF"

def coastal_tile(name, flow_str, range_str, status_str, time_str, spark, trend_line, meta_line, hydro_insight, bg, fg, icon, is_modeled=False):
    # Font style logic
    style = f"background-color:{bg}; color:{fg}; padding:6px 8px; border-radius:5px; margin-bottom:4px; font-size:0.80rem; line-height:1.35;"
    if is_modeled:
        style += " font-style: italic;"

    # Use standard f-string but ensure no leading whitespace that Markdown might interpret as code
    html = f"""
<div style="{style}">
    <div style="display:flex; justify-content:flex-start; align-items:center;">
        <span style="font-weight:700; font-size:0.9rem; margin-right: 10px;">{name} {icon}</span>
        <span style="font-weight:700; font-size:0.9rem;">{flow_str}</span>
    </div>
    <div style="opacity:0.9;">{range_str} • {status_str}</div>
    <div style="display:flex; justify-content:space-between; margin-top:2px;">
        <span>{spark} {trend_line}</span>
    </div>
    <div style="font-size:0.70rem; opacity:0.8; margin-top:4px;">
        {meta_line} • {time_str}<br>
        {hydro_insight}
    </div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)

def coastal_render_filters():
    st.subheader("Filters")

    cols = st.columns(9)

    with cols[0]:
        show_in_shape = st.checkbox("✅ In", value=True)
    with cols[1]:
        show_low = st.checkbox("🟡 Low", value=True)
    with cols[2]:
        show_slightly_high = st.checkbox("🟠 High", value=True)
    with cols[3]:
        show_blown_out = st.checkbox("🟥 Out", value=True)
    with cols[4]:
        show_below_legal = st.checkbox("⛔ Legal", value=True)
    with cols[5]:
        show_no_data = st.checkbox("⚠️ ND", value=True)
    with cols[6]:
        show_rising = st.checkbox("↑ Rise", value=True)
    with cols[7]:
        show_dropping = st.checkbox("↓ Drop", value=True)
    with cols[8]:
        show_stable = st.checkbox("↔ Stable", value=True)

    return {
        "in_shape": show_in_shape,
        "low": show_low,
        "slightly_high": show_slightly_high,
        "blown_out": show_blown_out,
        "below_legal": show_below_legal,
        "no_data": show_no_data,
        "rising": show_rising,
        "dropping": show_dropping,
        "stable": show_stable,
    }

def coastal_render_region_summary(coastal_data):
    st.subheader("Region Summary")

    regions = list(coastal_data.items())
    cols = st.columns(3)

    for i, (region_name, entries) in enumerate(regions):
        with cols[i % 3]:
            # Counts
            total = len(entries)
            measured = sum(1 for e in entries if not e.get("is_modeled", False))
            estimated = total - measured
            
            # Storm Cycle Phase Counts
            rising = sum(1 for e in entries if "Rising" in e.get("storm_cycle", [""])[0])
            peaking = sum(1 for e in entries if "Peak" in e.get("storm_cycle", [""])[0])
            # Group Dropping and Post-Storm together for brevity
            dropping = sum(1 for e in entries if "Drop" in e.get("storm_cycle", [""])[0] or "Post" in e.get("storm_cycle", [""])[0])
            
            # Window Coverage
            in_window = sum(1 for e in entries if "OPEN" in e.get("window", ""))
            
            # Badge Logic
            pct_window = (in_window / total * 100) if total > 0 else 0
            if pct_window >= 40:
                badge = "🔥 Hot"
                badge_bg = "#FEE2E2" # Light red/orange
                badge_col = "#991B1B"
            elif pct_window >= 15:
                badge = "🟡 Mixed"
                badge_bg = "#FEF3C7"
                badge_col = "#92400E"
            elif sum(1 for e in entries if e["cond_text"] == "blown out") > (total * 0.4):
                badge = "🟥 Blown"
                badge_bg = "#FEE2E2"
                badge_col = "#B91C1C"
            else:
                badge = "❄️ Cold"
                badge_bg = "#EFF6FF"
                badge_col = "#1E40AF"

            # HTML Card
            tile_html = f"""
            <div style='background-color:#FFFFFF; padding:12px; border-radius:8px; margin-bottom:12px; border:1px solid #E5E7EB; box-shadow: 0 1px 2px rgba(0,0,0,0.05);'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;'>
                    <span style='font-weight:700; font-size:1rem; color:#111827;'>{region_name}</span>
                    <span style='font-size:0.75rem; background-color:{badge_bg}; color:{badge_col}; padding:2px 8px; border-radius:12px; font-weight:600;'>{badge}</span>
                </div>
                <div style='font-size:0.8rem; color:#4B5563; line-height:1.5;'>
                    <div style='display:flex; justify-content:space-between;'>
                        <span>📡 <b>{measured}</b> Meas.</span>
                        <span>🧪 <b>{estimated}</b> Est.</span>
                    </div>
                    <div style='margin-top:4px; border-top:1px solid #F3F4F6; padding-top:4px;'>
                        <span title='Rising'>🌧️ {rising}</span> &nbsp; 
                        <span title='Peaking'>🌊 {peaking}</span> &nbsp; 
                        <span title='Dropping/Post'>📉 {dropping}</span>
                    </div>
                    <div style='margin-top:4px; font-weight:500; color:#059669;'>
                        🎯 {in_window} Rivers Fishable ({pct_window:.0f}%)
                    </div>
                </div>
            </div>
            """
            st.markdown(tile_html, unsafe_allow_html=True)

def coastal_filter_entry(e, filters):
    cond = e["cond_text"]
    trend = e["trend_text"]

    cond_ok = (
        (cond == "in shape" and filters["in_shape"]) or
        (cond == "low" and filters["low"]) or
        (cond == "slightly high" and filters["slightly_high"]) or
        (cond == "blown out" and filters["blown_out"]) or
        (cond == "below legal" and filters["below_legal"]) or
        (cond == "too low" and filters["low"]) or
        (cond == "no data" and filters["no_data"])
    )

    trend_ok = (
        ("↑" in trend and filters["rising"]) or
        ("↓" in trend and filters["dropping"]) or
        ("↔" in trend and filters["stable"])
    )

    return cond_ok and trend_ok

def coastal_render_top3(coastal_data, filters):
    st.subheader("🔥 Top 3 Right Now")

    filtered_rivers = []
    for region_name, entries in coastal_data.items():
        for e in entries:
            if coastal_filter_entry(e, filters):
                filtered_rivers.append((region_name, e))

    def sort_key(item):
        region, e = item
        score = e["score"]
        pct = e["pct_change"] or 0
        last = e["last_val"] or 999999
        spec = e["spec"]
        try:
            t_text = spec.get("T", "")
            t_clean = t_text.replace("cfs", "").replace("ft", "").strip()
            lo, hi = [float(x) for x in t_clean.split("-")]
            mid = (lo + hi) / 2
            dist = abs(last - mid)
        except Exception:
            dist = 999999
        return (-score, -pct, dist)

    top3 = sorted(filtered_rivers, key=sort_key)[:3]

    if not top3:
        st.write("No rivers match filters.")
        return

    for region_name, entry in top3:
        spec = entry["spec"]
        name = f"{spec.get('Name')} ({region_name})"

        last_val = entry["last_val"]
        t_range = spec.get("T", "")
        cond_text = entry["cond_text"]

        gauge = entry.get("gauge_used") or {}
        param = gauge.get("P", "")
        unit = "ft" if param == "00065" else "cfs"
        
        # Check if estimated logic applies
        is_modeled = entry.get("is_modeled", False)

        if last_val is None:
            flow_str = "—"
            if is_modeled:
                flow_str = "— Predicted Hydrology"
            
            range_str = t_range or "—"
            if cond_text != "no data":
                status_map = {
                    "blown out": "🟥 Blown out",
                    "slightly high": "🟠 Slightly high",
                    "in shape": "✅ In range",
                    "low": "🟡 Low",
                }
                status_str = status_map.get(cond_text, cond_text)
            else:
                status_str = "⚠️ No data"
        else:
            status_map = {
                "below legal": "⛔ Below legal",
                "too low": "Too Low",
                "blown out": "🟥 Blown out",
                "low": "🟡 Low",
                "slightly high": "🟠 Slightly high",
                "in shape": "✅ In range",
            }
            status_str = status_map.get(cond_text, cond_text)
            flow_str = f"{last_val:.0f} {unit}"
            range_str = f"Target: {t_range}"

        spark = entry["spark"]
        arrow = entry["arrow"]
        pct = entry["pct_change"]
        pct_str = f"{pct:+.1f}%" if pct is not None else "—"
        trend_line = f"{arrow} {pct_str}"

        bg = entry["cond_color"]
        fg = coastal_get_tile_text_color_from_bg(bg)

        # ⭐ NEW: storm-cycle + hydrology insight
        hydro_insight = entry.get("hydro_insight", "")
        icon = entry.get("icon", "🚫")

        coastal_tile(
            name=name,
            flow_str=flow_str,
            range_str=range_str,
            status_str=status_str,
            time_str=entry.get("time_str", ""),
            spark=spark,
            trend_line=trend_line,
            meta_line=f"{entry.get('source', '?')} ({entry.get('confidence', '?')})",
            hydro_insight=hydro_insight,
            bg=bg,
            fg=fg,
            icon=icon,
            is_modeled=is_modeled
        )

def coastal_render_regions(coastal_data, filters):
    st.subheader("📍 Coastal Regions")

    for region_name, entries in coastal_data.items():
        with st.expander(region_name, expanded=False):

            filtered = [e for e in entries if coastal_filter_entry(e, filters)]

            if not filtered:
                st.write("No rivers match filters.")
                continue

            filtered.sort(key=lambda x: x["score"], reverse=True)

            for entry in filtered:
                spec = entry["spec"]
                name = spec.get("Name", "Unknown")

                last_val = entry["last_val"]
                t_range = spec.get("T", "")
                cond_text = entry["cond_text"]

                gauge = entry.get("gauge_used") or {}
                param = gauge.get("P", "")
                unit = "ft" if "ft" in t_range else "cfs"
                
                # Check if estimated logic applies
                is_modeled = entry.get("is_modeled", False)

                if last_val is None:
                    flow_str = "—"
                    if is_modeled:
                        flow_str = "— Predicted Hydrology"
                        
                    range_str = t_range or "—"
                    if cond_text != "no data":
                        status_map = {
                            "blown out": "🟥 Blown out",
                            "slightly high": "🟠 Slightly high",
                            "in shape": "✅ In range",
                            "low": "🟡 Low",
                        }
                        status_str = status_map.get(cond_text, cond_text)
                    else:
                        status_str = "⚠️ No data"
                else:
                    status_map = {
                        "below legal": "⛔ Below legal",
                        "too low": "Too Low",
                        "blown out": "🟥 Blown Out",
                        "low": "🟡 Low",
                        "slightly high": "🟠 Slightly High",
                        "in shape": "✅ In Range",
                    }
                    status_str = status_map.get(cond_text, cond_text)
                    flow_str = f"{last_val:.2f} {unit}" if unit == "ft" else f"{last_val:.0f} {unit}"
                    range_str = f"Target: {t_range}"

                spark = entry["spark"]
                arrow = entry["arrow"]
                pct = entry["pct_change"]
                pct_str = f"{pct:+.1f}%" if pct is not None else "—"
                trend_line = f"{arrow} {pct_str}"

                bg = entry["cond_color"]
                fg = coastal_get_tile_text_color_from_bg(bg)

                # ⭐ NEW: storm-cycle + hydrology insight
                hydro_insight = entry.get("hydro_insight", "")
                icon = entry.get("icon", "🚫")

                coastal_tile(
                    name=name,
                    flow_str=flow_str,
                    range_str=range_str,
                    status_str=status_str,
                    time_str=entry.get("time_str", ""),
                    spark=spark,
                    trend_line=trend_line,
                    meta_line=f"{entry.get('source', '?')} ({entry.get('confidence', '?')})",
                    hydro_insight=hydro_insight,
                    bg=bg,
                    fg=fg,
                    icon=icon,
                    is_modeled=is_modeled
                )

# ============================================================
# EXPORTED CONTEXT FUNCTION (FOR MAP)
# ============================================================
def get_dashboard_context():
    """
    Returns the raw precomputed data and a default set of filters.
    Used by external modules (like map or planner) to access dashboard logic.
    """
    data = coastal_precompute_all_rivers()
    
    # Default filters (Everything ON)
    filters = {
        "in_shape": True,
        "low": True,
        "slightly_high": True,
        "blown_out": True,
        "below_legal": True,
        "no_data": True,
        "rising": True,
        "dropping": True,
        "stable": True,
    }
    return data, filters

# ============================================================
# MAIN DASHBOARD RENDER
# ============================================================
def render_coastal_dashboard():
    st.title("🌊 Coastal Conditions Dashboard")

    # PRECOMPUTE ONCE AT LOAD TIME
    COASTAL_PRECOMPUTED = coastal_precompute_all_rivers()

    filters = coastal_render_filters()

    coastal_render_region_summary(COASTAL_PRECOMPUTED)
    coastal_render_top3(COASTAL_PRECOMPUTED, filters)
    coastal_render_regions(COASTAL_PRECOMPUTED, filters)

    with st.expander("🛠 Debug: Gauge Diagnostics", expanded=False):
        for region, entries in COASTAL_PRECOMPUTED.items():
            st.markdown(f"### {region}")
            for e in entries:
                spec = e["spec"]
                name = spec["Name"]
                st.write({
                    "river": name,
                    "value": e["last_val"],
                    "source": e.get("source", "?"),
                    "confidence": e.get("confidence", "?"),
                    "timestamp": e.get("timestamp", None),
                    "gauge_used": e.get("gauge_used", None),
                })

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    st.set_page_config(page_title="Coastal Dashboard", layout="wide")
    render_coastal_dashboard()