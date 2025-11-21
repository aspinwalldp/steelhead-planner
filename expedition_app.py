import streamlit as st
import pandas as pd
import io
import datetime
import requests
from datetime import timedelta

# --- CONFIGURATION ---
st.set_page_config(page_title="Steelhead Expedition Command Center", layout="wide", page_icon="🎣")

# --- 1. DATA LOADING ---
BUILDER_DB_CSV = """Current_Loc,Action_Label,New_Loc,Days_Used,Miles,Drive_Hrs,River_Region,Days_To_Return
Start,START: Drive to Drum Mtns (UT),Drum Mtns,1,470,7.5,N/A,2
Start,START: Drive to SLC (UT),SLC_Area,1,470,7.5,N/A,2
Start,START: Drive to Brookings OR,Brookings,2,750,11.0,RC_Oregon,2
Start,START: Drive to Forks WA (Long Haul),Forks,3,1000,24.0,N/A,3
Start,START: Drive to Eureka/Pepperwood,Pepperwood,2,800,12.0,RC_NorCal,2
Drum Mtns,DRIVE: Drum Mtns -> Pyramid,Pyramid,1,420,6.5,RC_Pyramid,2
Drum Mtns,RETURN: Drum Mtns -> Home,Home,1,470,7.5,N/A,0
Pyramid,FISH: Pyramid (Full Day),Pyramid,1,0,0,RC_Pyramid,2
Pyramid,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM),Eagle Lake,1,100,2.0,RC_Eagle,2
Pyramid,DRIVE: Pyramid -> Eagle Lake (No Fish),Eagle Lake,1,100,2.0,RC_Pyramid,2
Pyramid,MOVE & FISH: Pyramid -> Burney (Fish PM),Burney,1,140,2.5,RC_NorCal,2
Eagle Lake,FISH: Eagle Lake (Full Day),Eagle Lake,1,0,0,RC_Eagle,2
Eagle Lake,MOVE & FISH: Eagle -> Pepperwood (Eel),Pepperwood,1,190,4.0,RC_NorCal,2
Eagle Lake,MOVE & FISH: Eagle -> Maple Grove (Van Duzen),Maple Grove,1,180,3.5,RC_NorCal,2
Eagle Lake,MOVE & FISH: Eagle -> Hiouchi (Smith),Hiouchi,1,240,4.5,RC_NorCal,2
Eagle Lake,MOVE & FISH: Eagle -> Yreka (I-5 North),Yreka,1,150,3.0,RC_Eagle,2
Eagle Lake,MOVE & FISH: Eagle -> Grants Pass,Grants Pass,1,240,4.5,RC_Eagle,2
Eagle Lake,MOVE & FISH: Eagle -> Brookings (Long),Brookings,1,280,5.5,RC_Eagle,2
Eagle Lake,MOVE & FISH: Eagle -> Pyramid (Reverse),Pyramid,1,100,2.0,RC_Pyramid,2
Eagle Lake,MOVE: Eagle -> Yreka (I-5 North),Yreka,1,150,3.0,N/A,2
Eagle Lake,MOVE: Eagle -> Pepperwood (Eel),Pepperwood,1,190,4.0,RC_NorCal,2
Burney,FISH: Burney Area,Burney,1,20,0.5,RC_NorCal,2
Burney,MOVE & FISH: Burney -> Pepperwood,Pepperwood,1,150,3.0,RC_NorCal,2
Burney,MOVE & FISH: Burney -> Hiouchi,Hiouchi,1,190,3.5,RC_NorCal,2
Burney,MOVE & FISH: Burney -> Pyramid (Reverse),Pyramid,1,140,2.5,RC_Pyramid,2
Pepperwood,FISH: Eel River (Pepperwood),Pepperwood,1,0,0,RC_NorCal,2
Pepperwood,MOVE & FISH: Pepperwood -> Maple Grove,Maple Grove,1,35,0.5,RC_NorCal,2
Pepperwood,MOVE & FISH: Pepperwood -> Hiouchi,Hiouchi,1,90,1.5,RC_NorCal,2
Pepperwood,DRIVE: Pepperwood -> Forks (Long Haul),Forks,1,540,10.5,N/A,3
Pepperwood,MOVE & FISH: Pepperwood -> Eagle (Reverse),Eagle Lake,1,190,4.0,RC_Eagle,2
Pepperwood,MOVE & FISH: Pepperwood -> Burney (Reverse),Burney,1,150,3.0,RC_NorCal,2
Pepperwood,BAIL: Pepperwood -> Elko,Elko,1,530,9.0,N/A,2
Maple Grove,FISH: Van Duzen (Maple Grv),Maple Grove,1,0,0,RC_NorCal,2
Maple Grove,MOVE & FISH: Maple Grove -> Pepperwood,Pepperwood,1,35,0.5,RC_NorCal,2
Maple Grove,MOVE & FISH: Maple Grove -> Hiouchi,Hiouchi,1,60,1.0,RC_NorCal,2
Maple Grove,MOVE & FISH: Maple Grove -> Eagle (Reverse),Eagle Lake,1,180,3.5,RC_Eagle,2
Hiouchi,FISH: Smith River (Hiouchi),Hiouchi,1,0,0,RC_NorCal,2
Hiouchi,MOVE & FISH: Hiouchi -> Brookings,Brookings,1,25,0.5,RC_Oregon,2
Hiouchi,MOVE & FISH: Hiouchi -> Pepperwood,Pepperwood,1,90,1.5,RC_NorCal,2
Hiouchi,MOVE & FISH: Hiouchi -> Maple Grove,Maple Grove,1,60,1.0,RC_NorCal,2
Hiouchi,DRIVE: Hiouchi -> Forks (Long Haul),Forks,1,430,8.5,N/A,3
Hiouchi,MOVE & FISH: Hiouchi -> Eagle (Reverse),Eagle Lake,1,240,4.5,RC_Eagle,2
Hiouchi,MOVE & FISH: Hiouchi -> Burney (Reverse),Burney,1,190,3.5,RC_NorCal,2
Hiouchi,MOVE & FISH: Hiouchi -> Pepperwood (Reverse),Pepperwood,1,90,1.5,RC_NorCal,2
Hiouchi,MOVE & FISH: Hiouchi -> Maple Grove (Reverse),Maple Grove,1,60,1.0,RC_NorCal,2
Hiouchi,MOVE & FISH: Hiouchi -> Brookings (Reverse),Brookings,1,25,0.5,RC_Oregon,2
Yreka,DRIVE: Yreka -> Forks WA (Long Haul),Forks,1,450,8.0,N/A,3
Yreka,DRIVE: Yreka -> Brookings OR,Brookings,1,110,2.5,RC_Oregon,2
Yreka,MOVE & FISH: Yreka -> Eagle (Reverse),Eagle Lake,1,150,3.0,RC_Eagle,2
Grants Pass,DRIVE: Grants Pass -> Forks WA,Forks,1,350,6.5,N/A,3
Grants Pass,DRIVE: Grants Pass -> Brookings,Brookings,1,80,1.5,RC_Oregon,2
Grants Pass,MOVE & FISH: Grants Pass -> Eagle (Reverse),Eagle Lake,1,240,4.5,RC_Eagle,2
Brookings,FISH: Chetco River (Brookings),Brookings,1,0,0,RC_Oregon,2
Brookings,MOVE & FISH: Brookings -> Hiouchi,Hiouchi,1,25,0.5,RC_NorCal,2
Brookings,MOVE & FISH: Brookings -> Coos Bay,Coos Bay,1,100,2.0,RC_Oregon,3
Brookings,DRIVE: Brookings -> Forks (Long Haul),Forks,1,430,8.5,N/A,3
Brookings,MOVE & FISH: Brookings -> Eagle (Long/Rev),Eagle Lake,1,280,5.5,RC_Eagle,2
Brookings,BAIL: Brookings -> SLC,SLC_Area,1,750,11.0,N/A,2
Coos Bay,FISH: Umpqua (Coos Bay),Coos Bay,1,0,0,RC_Oregon,3
Coos Bay,MOVE & FISH: Coos Bay -> Brookings,Brookings,1,100,2.0,RC_Oregon,2
Coos Bay,MOVE: Coos Bay -> Forks (Long Drive),Forks,1,350,6.0,RC_OP,3
Coos Bay,MOVE & FISH: Coos Bay -> Brookings (Reverse),Brookings,1,100,2.0,RC_Oregon,2
Bend,DRIVE: Bend -> Brookings (Fish PM),Brookings,1,250,5.0,RC_Oregon,2
Bend,DRIVE: Bend -> Forks WA,Forks,1,350,6.5,RC_OP,3
Pendleton,DRIVE: Pendleton -> Forks WA (Fish PM),Forks,1,400,6.5,RC_OP,3
Forks,FISH: OP (Forks),Forks,1,0,0,RC_OP,3
Forks,RETURN: Forks -> Boise ID,Boise,1,600,10.5,N/A,2
Forks,BAIL: Forks -> Home (Long Haul),Home,3,1000,24.0,N/A,0
Forks,DRIVE: Forks -> Coos Bay (Long/Rev),Coos Bay,1,350,6.0,RC_Oregon,3
Forks,DRIVE: Forks -> Brookings (Long/Rev),Brookings,1,430,8.5,RC_Oregon,3
Forks,DRIVE: Forks -> Hiouchi (Long/Rev),Hiouchi,1,430,8.5,RC_NorCal,3
Forks,DRIVE: Forks -> Pepperwood (Long/Rev),Pepperwood,1,540,10.5,RC_NorCal,3
Forks,DRIVE: Forks -> Yreka (Long/Rev),Yreka,1,450,8.0,N/A,2
Forks,DRIVE: Forks -> Grants Pass (Rev),Grants Pass,1,350,6.5,N/A,2
Forks,DRIVE: Forks -> Bend (Rev),Bend,1,350,6.5,N/A,2
Forks,DRIVE: Forks -> Pendleton (Rev),Pendleton,1,400,6.5,N/A,2
Boise,RETURN: Boise -> Rawlins WY,Rawlins,1,550,8.0,N/A,1
Rawlins,RETURN: Rawlins -> Home,Home,1,370,7.0,N/A,0
SLC_Area,RETURN: Final Leg (SLC -> Home),Home,1,450,7.0,N/A,0
SLC_Area,DRIVE: SLC -> Bend (OR),Bend,1,600,9.5,N/A,2
SLC_Area,DRIVE: SLC -> Pendleton (OR),Pendleton,1,500,7.5,N/A,2
Any,RETURN: Begin Return Leg,SLC_Area,1,750,11.0,N/A,1
Any,BAIL: Return Home (Standard),Home,2,750,11.0,N/A,0
Elko,DRIVE: Elko -> Pepperwood (Long),Pepperwood,1,530,9.0,RC_NorCal,2
Elko,RETURN: Final Leg (SLC -> Home),Home,1,670,11.0,N/A,0
Eureka,BAIL: Eureka -> Elko,Elko,1,530,9.0,N/A,2
Home,TRIP COMPLETE,Home,0,0,0,N/A,0
Brookings,RETURN: Begin Return Leg,SLC_Area,1,750,11.0,N/A,1
Brookings,MOVE & FISH: Brookings -> Hiouchi (Reverse),Hiouchi,1,25,0.5,RC_NorCal,2
Hiouchi,MOVE & FISH: Hiouchi -> Pepperwood (Reverse),Pepperwood,1,90,1.5,RC_NorCal,2
"""

ITINERARY_CSV_RAW = """Option,Day,Activity
A,1,START: Drive to Drum Mtns (UT)
A,2,DRIVE: Drum Mtns -> Pyramid
A,3,FISH: Pyramid (Full Day)
A,4,FISH: Pyramid (Full Day)
A,5,FISH: Pyramid (Full Day)
A,6,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
A,7,MOVE & FISH: Eagle -> Pepperwood (Eel)
A,8,FISH: Eel River (Pepperwood)
A,9,FISH: Eel River (Pepperwood)
A,10,FISH: Eel River (Pepperwood)
A,11,MOVE & FISH: Pepperwood -> Hiouchi
A,12,MOVE & FISH: Hiouchi -> Brookings
A,13,FISH: Chetco River (Brookings)
A,14,FISH: Chetco River (Brookings)
A,15,RETURN: Begin Return Leg
A,16,RETURN: Final Leg (SLC -> Home)
B,1,START: Drive to Drum Mtns (UT)
B,2,DRIVE: Drum Mtns -> Pyramid
B,3,FISH: Pyramid (Full Day)
B,4,FISH: Pyramid (Full Day)
B,5,FISH: Pyramid (Full Day)
B,6,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
B,7,MOVE & FISH: Eagle -> Pepperwood (Eel)
B,8,FISH: Eel River (Pepperwood)
B,9,FISH: Eel River (Pepperwood)
B,10,FISH: Eel River (Pepperwood)
B,11,DRIVE: Pepperwood -> Forks (Long Haul)
B,12,FISH: OP (Forks)
B,13,FISH: OP (Forks)
B,14,FISH: OP (Forks)
B,15,FISH: OP (Forks)
B,16,RETURN: Forks -> Boise ID
B,17,RETURN: Boise -> Rawlins WY
B,18,RETURN: Rawlins -> Home
C,1,START: Drive to Drum Mtns (UT)
C,2,DRIVE: Drum Mtns -> Pyramid
C,3,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
C,4,MOVE & FISH: Eagle -> Pepperwood (Eel)
C,5,FISH: Eel River (Pepperwood)
C,6,FISH: Eel River (Pepperwood)
C,7,MOVE & FISH: Pepperwood -> Hiouchi
C,8,MOVE & FISH: Hiouchi -> Brookings
C,9,FISH: Chetco River (Brookings)
C,10,FISH: Chetco River (Brookings)
C,11,DRIVE: Brookings -> Forks (Long Haul)
C,12,FISH: OP (Forks)
C,13,FISH: OP (Forks)
C,14,FISH: OP (Forks)
C,15,RETURN: Forks -> Boise ID
C,16,RETURN: Boise -> Rawlins WY
C,17,RETURN: Rawlins -> Home
D,1,START: Drive to Drum Mtns (UT)
D,2,DRIVE: Drum Mtns -> Pyramid
D,3,FISH: Pyramid (Full Day)
D,4,FISH: Pyramid (Full Day)
D,5,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
D,6,MOVE & FISH: Eagle -> Pepperwood (Eel)
D,7,FISH: Eel River (Pepperwood)
D,8,FISH: Eel River (Pepperwood)
D,9,MOVE & FISH: Pepperwood -> Hiouchi
D,10,MOVE & FISH: Hiouchi -> Brookings
D,11,FISH: Chetco River (Brookings)
D,12,DRIVE: Brookings -> Forks (Long Haul)
D,13,FISH: OP (Forks)
D,14,FISH: OP (Forks)
D,15,RETURN: Forks -> Boise ID
D,16,RETURN: Boise -> Rawlins WY
D,17,RETURN: Rawlins -> Home
E,1,START: Drive to Drum Mtns (UT)
E,2,DRIVE: Drum Mtns -> Pyramid
E,3,FISH: Pyramid (Full Day)
E,4,FISH: Pyramid (Full Day)
E,5,FISH: Pyramid (Full Day)
E,6,FISH: Pyramid (Full Day)
E,7,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
E,8,MOVE & FISH: Eagle -> Pepperwood (Eel)
E,9,FISH: Eel River (Pepperwood)
E,10,FISH: Eel River (Pepperwood)
E,11,FISH: Eel River (Pepperwood)
E,12,FISH: Eel River (Pepperwood)
E,13,FISH: Eel River (Pepperwood)
E,14,FISH: Eel River (Pepperwood)
E,15,RETURN: Begin Return Leg
E,16,RETURN: Final Leg (SLC -> Home)
F,1,START: Drive to Drum Mtns (UT)
F,2,DRIVE: Drum Mtns -> Pyramid
F,3,FISH: Pyramid (Full Day)
F,4,FISH: Pyramid (Full Day)
F,5,FISH: Pyramid (Full Day)
F,6,FISH: Pyramid (Full Day)
F,7,FISH: Pyramid (Full Day)
F,8,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
F,9,MOVE & FISH: Eagle -> Brookings (Long)
F,10,FISH: Chetco River (Brookings)
F,11,FISH: Chetco River (Brookings)
F,12,FISH: Chetco River (Brookings)
F,13,FISH: Chetco River (Brookings)
F,14,FISH: Chetco River (Brookings)
F,15,RETURN: Begin Return Leg
F,16,RETURN: Final Leg (SLC -> Home)
G,1,START: Drive to Drum Mtns (UT)
G,2,DRIVE: Drum Mtns -> Pyramid
G,3,FISH: Pyramid (Full Day)
G,4,FISH: Pyramid (Full Day)
G,5,FISH: Pyramid (Full Day)
G,6,FISH: Pyramid (Full Day)
G,7,FISH: Pyramid (Full Day)
G,8,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
G,9,MOVE & FISH: Eagle -> Yreka (I-5 North)
G,10,DRIVE: Yreka -> Forks WA (Long Haul)
G,11,FISH: OP (Forks)
G,12,FISH: OP (Forks)
G,13,FISH: OP (Forks)
G,14,FISH: OP (Forks)
G,15,RETURN: Forks -> Boise ID
G,16,RETURN: Boise -> Rawlins WY
G,17,RETURN: Rawlins -> Home
H,1,START: Drive to Drum Mtns (UT)
H,2,DRIVE: Drum Mtns -> Pyramid
H,3,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
H,4,MOVE & FISH: Eagle -> Pepperwood (Eel)
H,5,FISH: Eel River (Pepperwood)
H,6,FISH: Eel River (Pepperwood)
H,7,FISH: Eel River (Pepperwood)
H,8,FISH: Eel River (Pepperwood)
H,9,FISH: Eel River (Pepperwood)
H,10,DRIVE: Pepperwood -> Forks (Long Haul)
H,11,FISH: OP (Forks)
H,12,FISH: OP (Forks)
H,13,FISH: OP (Forks)
H,14,FISH: OP (Forks)
H,15,RETURN: Forks -> Boise ID
H,16,RETURN: Boise -> Rawlins WY
H,17,RETURN: Rawlins -> Home
I,1,START: Drive to Drum Mtns (UT)
I,2,DRIVE: Drum Mtns -> Pyramid
I,3,FISH: Pyramid (Full Day)
I,4,FISH: Pyramid (Full Day)
I,5,FISH: Pyramid (Full Day)
I,6,FISH: Pyramid (Full Day)
I,7,FISH: Pyramid (Full Day)
I,8,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
I,9,MOVE & FISH: Eagle -> Pepperwood (Eel)
I,10,FISH: Eel River (Pepperwood)
I,11,FISH: Eel River (Pepperwood)
I,12,FISH: Eel River (Pepperwood)
I,13,FISH: Eel River (Pepperwood)
I,14,FISH: Eel River (Pepperwood)
I,15,RETURN: Begin Return Leg
I,16,RETURN: Final Leg (SLC -> Home)
J,1,START: Drive to Drum Mtns (UT)
J,2,DRIVE: Drum Mtns -> Pyramid
J,3,FISH: Pyramid (Full Day)
J,4,FISH: Pyramid (Full Day)
J,5,FISH: Pyramid (Full Day)
J,6,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
J,7,MOVE & FISH: Eagle -> Pepperwood (Eel)
J,8,FISH: Eel River (Pepperwood)
J,9,FISH: Eel River (Pepperwood)
J,10,FISH: Eel River (Pepperwood)
J,11,MOVE & FISH: Pepperwood -> Hiouchi
J,12,MOVE & FISH: Hiouchi -> Brookings
J,13,FISH: Chetco River (Brookings)
J,14,FISH: Chetco River (Brookings)
J,15,RETURN: Begin Return Leg
J,16,RETURN: Final Leg (SLC -> Home)
K,1,START: Drive to Drum Mtns (UT)
K,2,DRIVE: Drum Mtns -> Pyramid
K,3,FISH: Pyramid (Full Day)
K,4,FISH: Pyramid (Full Day)
K,5,FISH: Pyramid (Full Day)
K,6,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
K,7,MOVE & FISH: Eagle -> Pepperwood (Eel)
K,8,FISH: Eel River (Pepperwood)
K,9,MOVE & FISH: Pepperwood -> Hiouchi
K,10,DRIVE: Hiouchi -> Forks (Long Haul)
K,11,FISH: OP (Forks)
K,12,FISH: OP (Forks)
K,13,RETURN: Forks -> Boise ID
K,14,RETURN: Boise -> Rawlins WY
K,15,RETURN: Rawlins -> Home
L,1,START: Drive to Drum Mtns (UT)
L,2,DRIVE: Drum Mtns -> Pyramid
L,3,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
L,4,MOVE & FISH: Eagle -> Pepperwood (Eel)
L,5,FISH: Eel River (Pepperwood)
L,6,FISH: Eel River (Pepperwood)
L,7,FISH: Eel River (Pepperwood)
L,8,MOVE & FISH: Pepperwood -> Hiouchi
L,9,MOVE & FISH: Hiouchi -> Brookings
L,10,FISH: Chetco River (Brookings)
L,11,DRIVE: Brookings -> Forks (Long Haul)
L,12,FISH: OP (Forks)
L,13,FISH: OP (Forks)
L,14,FISH: OP (Forks)
L,15,RETURN: Forks -> Boise ID
L,16,RETURN: Boise -> Rawlins WY
L,17,RETURN: Rawlins -> Home
M,1,START: Drive to Drum Mtns (UT)
M,2,DRIVE: Drum Mtns -> Pyramid
M,3,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
M,4,MOVE & FISH: Eagle -> Pepperwood (Eel)
M,5,FISH: Eel River (Pepperwood)
M,6,FISH: Eel River (Pepperwood)
M,7,FISH: Eel River (Pepperwood)
M,8,FISH: Eel River (Pepperwood)
M,9,FISH: Eel River (Pepperwood)
M,10,FISH: Eel River (Pepperwood)
M,11,FISH: Eel River (Pepperwood)
M,12,FISH: Eel River (Pepperwood)
M,13,FISH: Eel River (Pepperwood)
M,14,FISH: Eel River (Pepperwood)
M,15,RETURN: Begin Return Leg
M,16,RETURN: Final Leg (SLC -> Home)
N,1,START: Drive to Drum Mtns (UT)
N,2,DRIVE: Drum Mtns -> Pyramid
N,3,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
N,4,MOVE & FISH: Eagle -> Brookings (Long)
N,5,FISH: Chetco River (Brookings)
N,6,FISH: Chetco River (Brookings)
N,7,FISH: Chetco River (Brookings)
N,8,FISH: Chetco River (Brookings)
N,9,FISH: Chetco River (Brookings)
N,10,FISH: Chetco River (Brookings)
N,11,FISH: Chetco River (Brookings)
N,12,FISH: Chetco River (Brookings)
N,13,FISH: Chetco River (Brookings)
N,14,BAIL: Brookings -> SLC
N,15,RETURN: Final Leg (SLC -> Home)
O,1,START: Drive to Drum Mtns (UT)
O,2,DRIVE: Drum Mtns -> Pyramid
O,3,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
O,4,MOVE & FISH: Eagle -> Grants Pass
O,5,DRIVE: Grants Pass -> Forks WA
O,6,FISH: OP (Forks)
O,7,FISH: OP (Forks)
O,8,FISH: OP (Forks)
O,9,FISH: OP (Forks)
O,10,FISH: OP (Forks)
O,11,FISH: OP (Forks)
O,12,FISH: OP (Forks)
O,13,FISH: OP (Forks)
O,14,RETURN: Forks -> Boise ID
O,15,RETURN: Boise -> Rawlins WY
O,16,RETURN: Rawlins -> Home
P,1,START: Drive to Drum Mtns (UT)
P,2,DRIVE: Drum Mtns -> Pyramid
P,3,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
P,4,MOVE & FISH: Eagle -> Pepperwood (Eel)
P,5,FISH: Eel River (Pepperwood)
P,6,FISH: Eel River (Pepperwood)
P,7,FISH: Eel River (Pepperwood)
P,8,FISH: Eel River (Pepperwood)
P,9,FISH: Eel River (Pepperwood)
P,10,FISH: Eel River (Pepperwood)
P,11,FISH: Eel River (Pepperwood)
P,12,FISH: Eel River (Pepperwood)
P,13,FISH: Eel River (Pepperwood)
P,14,RETURN: Begin Return Leg
P,15,RETURN: Final Leg (SLC -> Home)
Q,1,START: Drive to Drum Mtns (UT)
Q,2,DRIVE: Drum Mtns -> Pyramid
Q,3,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
Q,4,MOVE & FISH: Eagle -> Pepperwood (Eel)
Q,5,MOVE & FISH: Pepperwood -> Hiouchi
Q,6,MOVE & FISH: Hiouchi -> Brookings
Q,7,FISH: Chetco River (Brookings)
Q,8,FISH: Chetco River (Brookings)
Q,9,FISH: Chetco River (Brookings)
Q,10,FISH: Chetco River (Brookings)
Q,11,FISH: Chetco River (Brookings)
Q,12,FISH: Chetco River (Brookings)
Q,13,FISH: Chetco River (Brookings)
Q,14,RETURN: Begin Return Leg
Q,15,RETURN: Final Leg (SLC -> Home)
R,1,START: Drive to Drum Mtns (UT)
R,2,DRIVE: Drum Mtns -> Pyramid
R,3,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
R,4,MOVE & FISH: Eagle -> Grants Pass
R,5,DRIVE: Grants Pass -> Forks WA
R,6,FISH: OP (Forks)
R,7,FISH: OP (Forks)
R,8,FISH: OP (Forks)
R,9,FISH: OP (Forks)
R,10,FISH: OP (Forks)
R,11,FISH: OP (Forks)
R,12,FISH: OP (Forks)
R,13,FISH: OP (Forks)
R,14,RETURN: Forks -> Boise ID
R,15,RETURN: Boise -> Rawlins WY
R,16,RETURN: Rawlins -> Home
S,1,START: Drive to Drum Mtns (UT)
S,2,DRIVE: Drum Mtns -> Pyramid
S,3,FISH: Pyramid (Full Day)
S,4,FISH: Pyramid (Full Day)
S,5,FISH: Pyramid (Full Day)
S,6,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
S,7,MOVE & FISH: Eagle -> Pepperwood (Eel)
S,8,FISH: Eel River (Pepperwood)
S,9,FISH: Eel River (Pepperwood)
S,10,FISH: Eel River (Pepperwood)
S,11,FISH: Eel River (Pepperwood)
S,12,FISH: Eel River (Pepperwood)
S,13,FISH: Eel River (Pepperwood)
S,14,FISH: Eel River (Pepperwood)
S,15,RETURN: Begin Return Leg
S,16,RETURN: Final Leg (SLC -> Home)
A_r,1,START: Drive to SLC (UT)
A_r,2,DRIVE: SLC -> Bend (OR)
A_r,3,DRIVE: Bend -> Brookings (Fish PM)
A_r,4,FISH: Chetco River (Brookings)
A_r,5,FISH: Chetco River (Brookings)
A_r,6,FISH: Chetco River (Brookings)
A_r,7,MOVE & FISH: Brookings -> Hiouchi (Reverse)
A_r,8,MOVE & FISH: Hiouchi -> Pepperwood (Reverse)
A_r,9,FISH: Eel River (Pepperwood)
A_r,10,FISH: Eel River (Pepperwood)
A_r,11,FISH: Eel River (Pepperwood)
A_r,12,MOVE & FISH: Pepperwood -> Eagle (Reverse)
A_r,13,FISH: Eagle Lake (Full Day)
A_r,14,MOVE & FISH: Eagle -> Pyramid (Reverse)
A_r,15,FISH: Pyramid (Full Day)
A_r,16,FISH: Pyramid (Full Day)
A_r,17,RETURN: Drum Mtns -> Home
B_r,1,START: Drive to Forks WA (Long Haul)
B_r,2,DRIVE: SLC -> Pendleton (OR)
B_r,3,DRIVE: Pendleton -> Forks WA (Fish PM)
B_r,4,FISH: OP (Forks)
B_r,5,FISH: OP (Forks)
B_r,6,FISH: OP (Forks)
B_r,7,FISH: OP (Forks)
B_r,8,DRIVE: Forks -> Pepperwood (Long/Rev)
B_r,9,FISH: Eel River (Pepperwood)
B_r,10,FISH: Eel River (Pepperwood)
B_r,11,FISH: Eel River (Pepperwood)
B_r,12,MOVE & FISH: Pepperwood -> Eagle (Reverse)
B_r,13,FISH: Eagle Lake (Full Day)
B_r,14,MOVE & FISH: Eagle -> Pyramid (Reverse)
B_r,15,FISH: Pyramid (Full Day)
B_r,16,FISH: Pyramid (Full Day)
B_r,17,FISH: Pyramid (Full Day)
B_r,18,RETURN: Drum Mtns -> Home
C_r,1,START: Drive to Forks WA (Long Haul)
C_r,2,DRIVE: SLC -> Pendleton (OR)
C_r,3,DRIVE: Pendleton -> Forks WA (Fish PM)
C_r,4,FISH: OP (Forks)
C_r,5,FISH: OP (Forks)
C_r,6,FISH: OP (Forks)
C_r,7,DRIVE: Forks -> Reedsport (Long/Rev)
C_r,8,MOVE & FISH: Reedsport -> Brookings (Reverse)
C_r,9,FISH: Chetco River (Brookings)
C_r,10,FISH: Chetco River (Brookings)
C_r,11,MOVE & FISH: Brookings -> Hiouchi (Reverse)
C_r,12,MOVE & FISH: Hiouchi -> Pepperwood (Reverse)
C_r,13,FISH: Eel River (Pepperwood)
C_r,14,FISH: Eel River (Pepperwood)
C_r,15,MOVE & FISH: Pepperwood -> Eagle (Reverse)
C_r,16,MOVE & FISH: Eagle -> Pyramid (Reverse)
C_r,17,RETURN: Drum Mtns -> Home
D_r,1,START: Drive to Forks WA (Long Haul)
D_r,2,DRIVE: SLC -> Pendleton (OR)
D_r,3,DRIVE: Pendleton -> Forks WA (Fish PM)
D_r,4,FISH: OP (Forks)
D_r,5,FISH: OP (Forks)
D_r,6,DRIVE: Forks -> Reedsport (Long/Rev)
D_r,7,MOVE & FISH: Reedsport -> Brookings (Reverse)
D_r,8,FISH: Chetco River (Brookings)
D_r,9,FISH: Chetco River (Brookings)
D_r,10,MOVE & FISH: Brookings -> Hiouchi (Reverse)
D_r,11,MOVE & FISH: Hiouchi -> Pepperwood (Reverse)
D_r,12,FISH: Eel River (Pepperwood)
D_r,13,FISH: Eel River (Pepperwood)
D_r,14,MOVE & FISH: Pepperwood -> Eagle (Reverse)
D_r,15,MOVE & FISH: Eagle -> Pyramid (Reverse)
D_r,16,FISH: Pyramid (Full Day)
D_r,17,FISH: Pyramid (Full Day)
E_r,1,START: Drive to Elko (NV)
E_r,2,DRIVE: Elko -> Pepperwood (Long)
E_r,3,FISH: Eel River (Pepperwood)
E_r,4,FISH: Eel River (Pepperwood)
E_r,5,FISH: Eel River (Pepperwood)
E_r,6,FISH: Eel River (Pepperwood)
E_r,7,FISH: Eel River (Pepperwood)
E_r,8,FISH: Eel River (Pepperwood)
E_r,9,MOVE & FISH: Pepperwood -> Eagle (Reverse)
E_r,10,FISH: Eagle Lake (Full Day)
E_r,11,MOVE & FISH: Eagle -> Pyramid (Reverse)
E_r,12,FISH: Pyramid (Full Day)
E_r,13,FISH: Pyramid (Full Day)
E_r,14,FISH: Pyramid (Full Day)
E_r,15,FISH: Pyramid (Full Day)
E_r,16,RETURN: Drum Mtns -> Home
F_r,1,START: Drive to SLC (UT)
F_r,2,DRIVE: SLC -> Bend (OR)
F_r,3,DRIVE: Bend -> Brookings (Fish PM)
F_r,4,FISH: Chetco River (Brookings)
F_r,5,FISH: Chetco River (Brookings)
F_r,6,FISH: Chetco River (Brookings)
F_r,7,FISH: Chetco River (Brookings)
F_r,8,FISH: Chetco River (Brookings)
F_r,9,MOVE & FISH: Brookings -> Eagle (Long/Rev)
F_r,10,MOVE & FISH: Eagle -> Pyramid (Reverse)
F_r,11,FISH: Pyramid (Full Day)
F_r,12,FISH: Pyramid (Full Day)
F_r,13,FISH: Pyramid (Full Day)
F_r,14,FISH: Pyramid (Full Day)
F_r,15,FISH: Pyramid (Full Day)
F_r,16,RETURN: Drum Mtns -> Home
F_r,17,TRIP COMPLETE
G_r,1,START: Drive to Forks WA (Long Haul)
G_r,2,DRIVE: SLC -> Pendleton (OR)
G_r,3,DRIVE: Pendleton -> Forks WA (Fish PM)
G_r,4,FISH: OP (Forks)
G_r,5,FISH: OP (Forks)
G_r,6,FISH: OP (Forks)
G_r,7,FISH: OP (Forks)
G_r,8,DRIVE: Forks -> Yreka (Long/Rev)
G_r,9,MOVE & FISH: Yreka -> Eagle (Reverse)
G_r,10,MOVE & FISH: Eagle -> Pyramid (Reverse)
G_r,11,FISH: Pyramid (Full Day)
G_r,12,FISH: Pyramid (Full Day)
G_r,13,FISH: Pyramid (Full Day)
G_r,14,FISH: Pyramid (Full Day)
G_r,15,FISH: Pyramid (Full Day)
G_r,16,RETURN: Drum Mtns -> Home
H_r,1,START: Drive to Forks WA (Long Haul)
H_r,2,DRIVE: SLC -> Pendleton (OR)
H_r,3,DRIVE: Pendleton -> Forks WA (Fish PM)
H_r,4,FISH: OP (Forks)
H_r,5,FISH: OP (Forks)
H_r,6,FISH: OP (Forks)
H_r,7,FISH: OP (Forks)
H_r,8,DRIVE: Forks -> Pepperwood (Long/Rev)
H_r,9,FISH: Eel River (Pepperwood)
H_r,10,FISH: Eel River (Pepperwood)
H_r,11,FISH: Eel River (Pepperwood)
H_r,12,FISH: Eel River (Pepperwood)
H_r,13,FISH: Eel River (Pepperwood)
H_r,14,MOVE & FISH: Pepperwood -> Eagle (Reverse)
H_r,15,MOVE & FISH: Eagle -> Pyramid (Reverse)
H_r,16,FISH: Pyramid (Full Day)
H_r,17,RETURN: Drum Mtns -> Home
I_r,1,START: Drive to Elko (NV)
I_r,2,DRIVE: Elko -> Pepperwood (Long)
I_r,3,FISH: Eel River (Pepperwood)
I_r,4,FISH: Eel River (Pepperwood)
I_r,5,FISH: Eel River (Pepperwood)
I_r,6,FISH: Eel River (Pepperwood)
I_r,7,FISH: Eel River (Pepperwood)
I_r,8,MOVE & FISH: Pepperwood -> Eagle (Reverse)
I_r,9,FISH: Eagle Lake (Full Day)
I_r,10,MOVE & FISH: Eagle -> Pyramid (Reverse)
I_r,11,FISH: Pyramid (Full Day)
I_r,12,FISH: Pyramid (Full Day)
I_r,13,FISH: Pyramid (Full Day)
I_r,14,FISH: Pyramid (Full Day)
I_r,15,FISH: Pyramid (Full Day)
I_r,16,RETURN: Drum Mtns -> Home
J_r,1,START: Drive to SLC (UT)
J_r,2,DRIVE: SLC -> Bend (OR)
J_r,3,DRIVE: Bend -> Brookings (Fish PM)
J_r,4,FISH: Chetco River (Brookings)
J_r,5,FISH: Chetco River (Brookings)
J_r,6,MOVE & FISH: Brookings -> Hiouchi (Reverse)
J_r,7,MOVE & FISH: Hiouchi -> Pepperwood (Reverse)
J_r,8,FISH: Eel River (Pepperwood)
J_r,9,FISH: Eel River (Pepperwood)
J_r,10,FISH: Eel River (Pepperwood)
J_r,11,MOVE & FISH: Pepperwood -> Eagle (Reverse)
J_r,12,FISH: Eagle Lake (Full Day)
J_r,13,MOVE & FISH: Eagle -> Pyramid (Reverse)
J_r,14,FISH: Pyramid (Full Day)
J_r,15,FISH: Pyramid (Full Day)
J_r,16,FISH: Pyramid (Full Day)
J_r,17,RETURN: Drum Mtns -> Home
K_r,1,START: Drive to Forks WA (Long Haul)
K_r,2,DRIVE: SLC -> Pendleton (OR)
K_r,3,DRIVE: Pendleton -> Forks WA (Fish PM)
K_r,4,FISH: OP (Forks)
K_r,5,FISH: OP (Forks)
K_r,6,DRIVE: Forks -> Hiouchi (Long/Rev)
K_r,7,MOVE & FISH: Hiouchi -> Pepperwood (Reverse)
K_r,8,FISH: Eel River (Pepperwood)
K_r,9,FISH: Eel River (Pepperwood)
K_r,10,MOVE & FISH: Pepperwood -> Eagle (Reverse)
K_r,11,FISH: Eagle Lake (Full Day)
K_r,12,MOVE & FISH: Eagle -> Pyramid (Reverse)
K_r,13,FISH: Pyramid (Full Day)
K_r,14,FISH: Pyramid (Full Day)
K_r,15,FISH: Pyramid (Full Day)
K_r,16,RETURN: Drum Mtns -> Home
L_r,1,START: Drive to Forks WA (Long Haul)
L_r,2,DRIVE: SLC -> Pendleton (OR)
L_r,3,DRIVE: Pendleton -> Forks WA (Fish PM)
L_r,4,FISH: OP (Forks)
L_r,5,FISH: OP (Forks)
L_r,6,FISH: OP (Forks)
L_r,7,DRIVE: Forks -> Brookings (Long/Rev)
L_r,8,FISH: Chetco River (Brookings)
L_r,9,FISH: Chetco River (Brookings)
L_r,10,MOVE & FISH: Brookings -> Hiouchi (Reverse)
L_r,11,MOVE & FISH: Hiouchi -> Pepperwood (Reverse)
L_r,12,FISH: Eel River (Pepperwood)
L_r,13,FISH: Eel River (Pepperwood)
L_r,14,FISH: Eel River (Pepperwood)
L_r,15,MOVE & FISH: Pepperwood -> Eagle (Reverse)
L_r,16,MOVE & FISH: Eagle -> Pyramid (Reverse)
L_r,17,RETURN: Drum Mtns -> Home
M_r,1,START: Drive to Elko (NV)
M_r,2,DRIVE: Elko -> Pepperwood (Long)
M_r,3,FISH: Eel River (Pepperwood)
M_r,4,FISH: Eel River (Pepperwood)
M_r,5,FISH: Eel River (Pepperwood)
M_r,6,FISH: Eel River (Pepperwood)
M_r,7,FISH: Eel River (Pepperwood)
M_r,8,FISH: Eel River (Pepperwood)
M_r,9,FISH: Eel River (Pepperwood)
M_r,10,FISH: Eel River (Pepperwood)
M_r,11,FISH: Eel River (Pepperwood)
M_r,12,FISH: Eel River (Pepperwood)
M_r,13,MOVE & FISH: Pepperwood -> Eagle (Reverse)
M_r,14,MOVE & FISH: Eagle -> Pyramid (Reverse)
M_r,15,DRIVE: Drum Mtns -> Pyramid
M_r,16,RETURN: Drum Mtns -> Home
N_r,1,START: Drive to Drum Mtns (UT)
N_r,2,DRIVE: Drum Mtns -> Pyramid
N_r,3,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
N_r,4,MOVE & FISH: Eagle -> Brookings (Long)
N_r,5,FISH: Chetco River (Brookings)
N_r,6,FISH: Chetco River (Brookings)
N_r,7,FISH: Chetco River (Brookings)
N_r,8,FISH: Chetco River (Brookings)
N_r,9,FISH: Chetco River (Brookings)
N_r,10,FISH: Chetco River (Brookings)
N_r,11,FISH: Chetco River (Brookings)
N_r,12,FISH: Chetco River (Brookings)
N_r,13,FISH: Chetco River (Brookings)
N_r,14,BAIL: Brookings -> SLC
N_r,15,RETURN: Final Leg (SLC -> Home)
O_r,1,START: Drive to Drum Mtns (UT)
O_r,2,DRIVE: Drum Mtns -> Pyramid
O_r,3,MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)
O_r,4,MOVE & FISH: Eagle -> Grants Pass
O_r,5,DRIVE: Grants Pass -> Forks WA
O_r,6,FISH: OP (Forks)
O_r,7,FISH: OP (Forks)
O_r,8,FISH: OP (Forks)
O_r,9,FISH: OP (Forks)
O_r,10,FISH: OP (Forks)
O_r,11,FISH: OP (Forks)
O_r,12,FISH: OP (Forks)
O_r,13,FISH: OP (Forks)
O_r,14,RETURN: Forks -> Boise ID
O_r,15,RETURN: Boise -> Rawlins WY
O_r,16,RETURN: Rawlins -> Home
P_r,1,START: Drive to Elko (NV)
P_r,2,DRIVE: Elko -> Pepperwood (Long)
P_r,3,FISH: Eel River (Pepperwood)
P_r,4,FISH: Eel River (Pepperwood)
P_r,5,FISH: Eel River (Pepperwood)
P_r,6,FISH: Eel River (Pepperwood)
P_r,7,FISH: Eel River (Pepperwood)
P_r,8,FISH: Eel River (Pepperwood)
P_r,9,FISH: Eel River (Pepperwood)
P_r,10,FISH: Eel River (Pepperwood)
P_r,11,FISH: Eel River (Pepperwood)
P_r,12,MOVE & FISH: Pepperwood -> Eagle (Reverse)
P_r,13,MOVE & FISH: Eagle -> Pyramid (Reverse)
P_r,14,DRIVE: Drum Mtns -> Pyramid
P_r,15,RETURN: Drum Mtns -> Home
Q_r,1,START: Drive to SLC (UT)
Q_r,2,DRIVE: SLC -> Bend (OR)
Q_r,3,DRIVE: Bend -> Brookings (Fish PM)
Q_r,4,FISH: Chetco River (Brookings)
Q_r,5,FISH: Chetco River (Brookings)
Q_r,6,FISH: Chetco River (Brookings)
Q_r,7,FISH: Chetco River (Brookings)
Q_r,8,FISH: Chetco River (Brookings)
Q_r,9,FISH: Chetco River (Brookings)
Q_r,10,FISH: Chetco River (Brookings)
Q_r,11,FISH: Chetco River (Brookings)
Q_r,12,MOVE & FISH: Brookings -> Hiouchi (Reverse)
Q_r,13,MOVE & FISH: Hiouchi -> Pepperwood (Reverse)
Q_r,14,MOVE & FISH: Pepperwood -> Eagle (Reverse)
Q_r,15,MOVE & FISH: Eagle -> Pyramid (Reverse)
Q_r,16,DRIVE: Drum Mtns -> Pyramid
Q_r,17,RETURN: Drum Mtns -> Home
R_r,1,START: Drive to Forks WA (Long Haul)
R_r,2,DRIVE: SLC -> Pendleton (OR)
R_r,3,DRIVE: Pendleton -> Forks WA (Fish PM)
R_r,4,FISH: OP (Forks)
R_r,5,FISH: OP (Forks)
R_r,6,FISH: OP (Forks)
R_r,7,FISH: OP (Forks)
R_r,8,FISH: OP (Forks)
R_r,9,FISH: OP (Forks)
R_r,10,FISH: OP (Forks)
R_r,11,FISH: OP (Forks)
R_r,12,DRIVE: Forks -> Grants Pass (Rev)
R_r,13,MOVE & FISH: Grants Pass -> Eagle (Reverse)
R_r,14,MOVE & FISH: Eagle -> Pyramid (Reverse)
R_r,15,DRIVE: Drum Mtns -> Pyramid
R_r,16,RETURN: Drum Mtns -> Home
S_r,1,START: Drive to Elko (NV)
S_r,2,DRIVE: Elko -> Pepperwood (Long)
S_r,3,FISH: Eel River (Pepperwood)
S_r,4,FISH: Eel River (Pepperwood)
S_r,5,FISH: Eel River (Pepperwood)
S_r,6,FISH: Eel River (Pepperwood)
S_r,7,FISH: Eel River (Pepperwood)
S_r,8,FISH: Eel River (Pepperwood)
S_r,9,FISH: Eel River (Pepperwood)
S_r,10,MOVE & FISH: Pepperwood -> Eagle (Reverse)
S_r,11,FISH: Eagle Lake (Full Day)
S_r,12,MOVE & FISH: Eagle -> Pyramid (Reverse)
S_r,13,FISH: Pyramid (Full Day)
S_r,14,FISH: Pyramid (Full Day)
S_r,15,FISH: Pyramid (Full Day)
S_r,16,RETURN: Drum Mtns -> Home"""

def get_next_best_move(current_loc, ratings, days_remaining):
    """Auto-pilot logic with full node coverage."""
    r_pyr = ratings['Pyramid']
    r_norcal = ratings['NorCal']
    r_ore = ratings['Oregon']
    r_op = ratings['OP']
    
    # Safety: Return Buffers
    # (Nodes with 0 = Safe to end here)
    return_days = {
        "Forks": 3, "Coos Bay": 2, "Brookings": 2, "Hiouchi": 2, 
        "Pepperwood": 2, "Maple Grove": 2, "Burney": 2, 
        "Pyramid": 2, "Eagle Lake": 2, 
        "Drum Mtns": 0, "Boise": 1, "Rawlins": 0, "Elko": 1, "SLC_Area": 1,
        "Bend": 2, "Pendleton": 2, "Yreka": 2, "Grants Pass": 2
    }
    needed = return_days.get(current_loc, 1)
    
    # --- RETURN LOGIC ---
    if days_remaining <= needed:
        if current_loc == "Forks": return "RETURN: Forks -> Boise ID"
        if current_loc == "Brookings": return "BAIL: Brookings -> SLC"
        if current_loc in ["Pepperwood", "Eureka"]: return "BAIL: Pepperwood -> Elko"
        if current_loc == "Boise": return "RETURN: Boise -> Rawlins WY"
        if current_loc == "Rawlins": return "RETURN: Rawlins -> Home"
        if current_loc == "SLC_Area": return "RETURN: Final Leg (SLC -> Home)"
        if current_loc == "Elko": return "RETURN: Final Leg (SLC -> Home)"
        if current_loc == "Bend": return "DRIVE: Bend -> Brookings (Fish PM)" # Catchup
        if current_loc == "Pendleton": return "DRIVE: Pendleton -> Forks WA (Fish PM)" # Catchup
        return "BAIL: Return Home (Standard)"

    # --- FORWARD LOGIC (The Compass) ---
    
    # Start
    if current_loc == "Start": return "START: Drive to Drum Mtns (UT)"
    if current_loc == "Drum Mtns": return "DRIVE: Drum Mtns -> Pyramid"
    
    # Pyramid / High Desert
    if current_loc == "Pyramid":
        if r_pyr >= 3.5: return "FISH: Pyramid (Full Day)"
        return "MOVE & FISH: Pyramid -> Eagle Lake (Fish PM)"
    
    # NorCal Nodes
    if current_loc == "Eagle Lake":
        if r_pyr >= 3.5: return "FISH: Eagle Lake (Full Day)" 
        return "MOVE & FISH: Eagle -> Pepperwood (Eel)"
        
    if current_loc == "Burney":
        if r_norcal >= 3.5: return "FISH: Burney Area"
        return "MOVE & FISH: Burney -> Pepperwood"

    if current_loc in ["Pepperwood", "Eureka"]: # Handle Alias
        if r_norcal >= 3.5: return "FISH: Eel River (Pepperwood)"
        return "MOVE & FISH: Pepperwood -> Hiouchi"

    if current_loc == "Maple Grove":
        if r_norcal >= 3.5: return "FISH: Van Duzen (Maple Grv)"
        return "MOVE & FISH: Maple Grove -> Pepperwood"

    if current_loc == "Hiouchi":
        if r_norcal >= 3.5: return "FISH: Smith River (Hiouchi)"
        return "MOVE & FISH: Hiouchi -> Brookings"
    
    # Transit Hubs (No Fish -> Move West/North)
    if current_loc == "Yreka":
        return "DRIVE: Yreka -> Forks WA (Long Haul)"
    if current_loc == "Grants Pass":
        return "DRIVE: Grants Pass -> Forks WA"
    if current_loc == "Bend":
        return "DRIVE: Bend -> Brookings (Fish PM)"
    if current_loc == "Pendleton":
        return "DRIVE: Pendleton -> Forks WA (Fish PM)"
    if current_loc == "Elko":
        return "DRIVE: Elko -> Pepperwood (Long)"
    if current_loc == "SLC_Area":
        return "DRIVE: SLC -> Pendleton (OR)" # Default North/West

    # Oregon
    if current_loc == "Brookings":
        if r_ore >= 3.0: return "FISH: Chetco River (Brookings)"
        return "MOVE & FISH: Brookings -> Coos Bay"
        
    if current_loc in ["Coos Bay", "Reedsport"]:
        if r_ore >= 3.0: return "FISH: Umpqua (Coos Bay)"
        return "MOVE: Coos Bay -> Forks (Long Drive)"

    # Washington / OP
    if current_loc == "Forks":
        if r_op >= 3.0: return "FISH: OP (Forks)"
        return "RETURN: Forks -> Boise ID"
    
    if current_loc == "Home": return "TRIP COMPLETE"

    return "Stay / Fish Local" 


# --- 2. LIVE INTEL FUNCTIONS ---

@st.cache_data(ttl=3600)
def get_nws_forecast_data(lat, lon):
    try:
        headers = {"User-Agent": "(my-expedition-app)"}
        lat, lon = round(lat, 4), round(lon, 4)
        point_url = f"https://api.weather.gov/points/{lat},{lon}"
        r = requests.get(point_url, headers=headers)
        if r.status_code != 200: return None
        grid_data = r.json()
        forecast_url = grid_data['properties']['forecast']
        r2 = requests.get(forecast_url, headers=headers)
        if r2.status_code != 200: return None
        return r2.json()['properties']['periods']
    except:
        return None

@st.cache_data(ttl=600) 
def get_usgs_simple(site_id, param_code='00060'):
    try:
        # P2D window for reliability
        url = f"https://waterservices.usgs.gov/nwis/iv/?format=json&sites={site_id}&parameterCd={param_code}&period=P2D"
        r = requests.get(url).json()
        ts_data = r['value']['timeSeries'][0]['values'][0]['value']
        if not ts_data: return None
        return float(ts_data[-1]['value'])
    except:
        return None

# --- 3. MAIN APP LOGIC ---
try:
    df_db = pd.read_csv(io.StringIO(BUILDER_DB_CSV))
    df_itin = pd.read_csv(io.StringIO(ITINERARY_CSV_RAW))
    df_db['Miles'] = pd.to_numeric(df_db['Miles'], errors='coerce').fillna(0).astype(int)
    df_db['Drive_Hrs'] = pd.to_numeric(df_db['Drive_Hrs'], errors='coerce').fillna(0).round(1)
except Exception as e:
    st.error(f"Data Error: {e}")
    st.stop()

OPTION_NAMES = {
    'A': "NorCal + Oregon (Standard)",
    'B': "NorCal + OP (Standard)",
    'C': "Oregon + OP (Reduced NorCal)",
    'D': "Grand Tour (All Regions)",
    'E': "NorCal Focus (Extended Pyr)",
    'F': "Pyramid + Oregon (Focus)",
    'G': "Pyramid + OP (Focus)",
    'H': "NorCal + OP (Extended NorCal)",
    'I': "Pyramid + NorCal (Local Loop)",
    'J': "Pyramid + NorCal + Oregon",
    'K': "Pyramid + NorCal + OP",
    'L': "NorCal + Oregon + OP (Skip Pyr)",
    'M': "NorCal Max (Skip Pyramid)",
    'N': "Oregon Max (Northern Route)",
    'O': "OP Max (Northern Route)",
    'P': "NorCal (Reduced Pyramid)",
    'Q': "Oregon (Reduced Pyramid)",
    'R': "OP (Reduced Pyramid)",
    'S': "NorCal Focus (Standard Pyr)"
}

if 'current_location_override' not in st.session_state:
    st.session_state['current_location_override'] = None
if 'day_override' not in st.session_state:
    st.session_state['day_override'] = 1

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar.expander("Conditions", expanded=False):
    rc_pyr = st.slider("Pyramid Lake", 0.0, 5.0, 3.5, 0.5)
    rc_norcal = st.slider("NorCal Coast", 0.0, 5.0, 3.5, 0.5)
    rc_ore = st.slider("Oregon Coast", 0.0, 5.0, 2.0, 0.5)
    rc_op = st.slider("Olympic Peninsula", 0.0, 5.0, 2.0, 0.5)
ratings = {"Pyramid": rc_pyr, "NorCal": rc_norcal, "Oregon": rc_ore, "OP": rc_op}

with st.sidebar.expander("Other Variables", expanded=False):
    energy_score = st.slider("Personal Energy", 0, 5, 4)
    variety_pref = st.slider("Variety Preference", 0, 5, 5)
    road_risk = st.slider("Weather/Road Risk", 0, 5, 5)

with st.sidebar.expander("Fuel Costs", expanded=False):
    fuel_price_low = st.number_input("Fuel Price (Low)", 3.00)
    fuel_price_high = st.number_input("Fuel Price (High)", 3.75)

with st.sidebar.expander("Veto Options", expanded=False):
    veto_pyr = st.checkbox("Veto Pyramid?", False)
    veto_eagle = st.checkbox("Veto Eagle?", False)
    veto_norcal = st.checkbox("Veto NorCal?", False)
    veto_ore = st.checkbox("Veto Oregon?", False)
    veto_op = st.checkbox("Veto OP?", False)

st.sidebar.divider()
st.sidebar.markdown("### 🔗 Quick Links")
st.sidebar.markdown("""
* **NorCal:** [Fishing the North Coast](https://fishingthenorthcoast.com/) | [The Fly Shop](https://www.theflyshop.com/stream-report) | [NOAA River Forecast](https://www.cnrfc.noaa.gov/)
* **Pyramid:** [Pyramid Fly Co](https://pyramidflyco.com/fishing-report/) | [Windy.com](https://www.windy.com/39.950/-119.600)
* **Oregon:** [NOAA NW River Forecast](https://www.nwrfc.noaa.gov/rfc/) | [Ashland Fly Shop](https://www.ashlandflyshop.com/blogs/fishing-reports)
* **OP:** [Waters West](https://waterswest.com/fishing-report/)
""")

# --- 5. RANKING DASHBOARD ---
st.title("Steelhead Expedition Command Center")

ranked_data = []
for code, name in OPTION_NAMES.items():
    steps = df_itin[df_itin['Option'] == code]
    t_miles = 0
    t_fish = 0
    r_counts = {"Pyramid":0, "Eagle":0, "NorCal":0, "Oregon":0, "OP":0}
    regional_score = 0
    
    for _, row in steps.iterrows():
        db_row = df_db[df_db['Action_Label'] == row['Activity']]
        if not db_row.empty:
            t_miles += db_row.iloc[0]['Miles']
            reg = db_row.iloc[0]['River_Region']
            
            if "FISH" in row['Activity'].upper() and isinstance(reg, str) and reg.startswith("RC_"):
                t_fish += 1
                rk = reg.replace("RC_", "")
                if rk in r_counts: r_counts[rk] += 1
                elif rk == "Eagle": r_counts['Eagle'] += 1 
                
                if rk == "Pyramid": regional_score += rc_pyr
                elif rk == "Eagle": regional_score += rc_pyr
                elif rk == "NorCal": regional_score += rc_norcal
                elif rk == "Oregon": regional_score += rc_ore
                elif rk == "OP": regional_score += rc_op

    max_possible = t_fish * 5
    q_norm = regional_score / max_possible if max_possible > 0 else 0
    eff = (5000 - t_miles) / 5000
    var_score = len([k for k,v in r_counts.items() if v > 0]) / 4
    
    is_vetoed = False
    if veto_pyr and r_counts['Pyramid'] > 0: is_vetoed = True
    if veto_eagle and r_counts['Eagle'] > 0: is_vetoed = True
    if veto_norcal and r_counts['NorCal'] > 0: is_vetoed = True
    if veto_ore and r_counts['Oregon'] > 0: is_vetoed = True
    if veto_op and r_counts['OP'] > 0: is_vetoed = True
    
    final_score = ((50 * q_norm) + (1 * var_score * variety_pref) + (5 * eff) + (5 * (energy_score/5))) if not is_vetoed else 0
    
    ranked_data.append({
        "Option": code,
        "Summary": name,
        "Pyramid": r_counts['Pyramid'], "Eagle": r_counts['Eagle'],
        "NorCal": r_counts['NorCal'], "Oregon": r_counts['Oregon'], "OP": r_counts['OP'],
        "Fish Days": int(t_fish), "Miles": int(t_miles),
        "DriveHrs": round(t_miles/55, 1), 
        "Fuel": f"${int((t_miles/23)*fuel_price_low)} - ${int((t_miles/23)*fuel_price_high)}",
        "Score": round(final_score, 2)
    })

df_rank = pd.DataFrame(ranked_data).sort_values(by="Score", ascending=False)
winner = df_rank.iloc[0]

st.info(f"**Current Winner:** Option {winner['Option']} - {winner['Summary']}")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Pyramid Days", winner['Pyramid'])
c2.metric("Eagle Days", winner['Eagle'])
c3.metric("NorCal Days", winner['NorCal'])
c4.metric("Oregon Days", winner['Oregon'])
c5.metric("OP Days", winner['OP'])

c_a, c_b, c_c, c_d = st.columns(4)
c_a.metric("Total Fish Days", winner['Fish Days'])
c_b.metric("Total Miles", winner['Miles'])
c_c.metric("Drive Hrs", winner['DriveHrs'])
c_d.metric("Fuel Est", winner['Fuel'])

with st.expander("📊 View Full Ranking Matrix", expanded=False):
    cols_order = ["Option", "Summary", "Pyramid", "Eagle", "NorCal", "Oregon", "OP", "Fish Days", "Miles", "DriveHrs", "Fuel"]
    st.dataframe(df_rank[cols_order], hide_index=True, use_container_width=True)

# --- 6. TRIP BUILDER ---
st.divider()
start_date = st.date_input("Departure Date", datetime.date(2026, 1, 1))
st.subheader("🗓️ Trip Itinerary")

c_plan, c_rev = st.columns([3, 1])
with c_plan:
    formatted_opts = [f"{r['Option']} - {r['Summary']}" for i, r in df_rank.iterrows()]
    win_str = f"{winner['Option']} - {winner['Summary']}"
    def_idx = formatted_opts.index(win_str) if win_str in formatted_opts else 0
    sel_str = st.selectbox("Select Base Plan", formatted_opts, index=def_idx)
    sel_code = sel_str.split(" - ")[0]

with c_rev:
    rev_mode = st.toggle("Reverse Route?")

# Manual Override
with st.expander("🛠️ Live Reroute / Manual Override", expanded=False):
    c_day, c_loc = st.columns(2)
    ovr_day = c_day.number_input("Current Day #", 1, 18, 1)
    all_locs = sorted(df_db['Current_Loc'].unique())
    
    # FORCE RESET: If session state is None, reset widget
    if st.session_state['current_location_override'] is None:
        ovr_idx = 0 # Default (On Plan)
    else:
        try:
            ovr_idx = ["(On Plan)"] + all_locs
            ovr_idx = ovr_idx.index(st.session_state['current_location_override'])
        except:
            ovr_idx = 0

    ovr_loc_selection = c_loc.selectbox("Current Location", ["(On Plan)"] + all_locs, index=ovr_idx)
    
    # Logic: Only update session state if changed by user interaction
    if ovr_loc_selection == "(On Plan)":
        st.session_state['current_location_override'] = None
    else:
        st.session_state['current_location_override'] = ovr_loc_selection
        st.session_state['day_override'] = ovr_day
        st.warning(f"Rerouting from Day {ovr_day} at {ovr_loc_selection}...")
    
    if st.button("Reset to Base Plan"):
        st.session_state['current_location_override'] = None
        st.rerun()

# Build Table Logic
final_code = f"{sel_code}_r" if rev_mode else sel_code
base_steps = df_itin[df_itin['Option'] == final_code]
ovr_active = st.session_state['current_location_override'] is not None
ovr_d = st.session_state['day_override']
ovr_l = st.session_state['current_location_override']

final_itinerary = []
current_loc = "Start"

if not base_steps.empty:
    for _, row in base_steps.iterrows():
        day_num = row['Day']
        if ovr_active and day_num >= ovr_d: break 
        db_match = df_db[df_db['Action_Label'] == row['Activity']]
        miles = db_match.iloc[0]['Miles'] if not db_match.empty else 0
        hrs = db_match.iloc[0]['Drive_Hrs'] if not db_match.empty else 0
        new_loc_std = db_match.iloc[0]['New_Loc'] if not db_match.empty else current_loc
        
        final_itinerary.append({
            "Day": day_num, "Activity": row['Activity'], "Miles": miles, "Hrs": hrs, "Region": db_match.iloc[0]['River_Region'] if not db_match.empty else ""
        })
        current_loc = new_loc_std

    if ovr_active:
        curr_sim_loc = ovr_l
        for d in range(ovr_d, 18): 
            action = get_next_best_move(curr_sim_loc, ratings, 18-d)
            db_match = df_db[df_db['Action_Label'] == action]
            miles = db_match.iloc[0]['Miles'] if not db_match.empty else 0
            hrs = db_match.iloc[0]['Drive_Hrs'] if not db_match.empty else 0
            new_loc_sim = db_match.iloc[0]['New_Loc'] if not db_match.empty else curr_sim_loc
            region = db_match.iloc[0]['River_Region'] if not db_match.empty else ""
            
            final_itinerary.append({
                "Day": d, "Activity": action, "Miles": miles, "Hrs": hrs, "Region": region
            })
            curr_sim_loc = new_loc_sim
            if curr_sim_loc == "Home": break

display_df = pd.DataFrame(final_itinerary)
if not display_df.empty:
    display_df['Date'] = display_df.apply(lambda x: (start_date + timedelta(days=x['Day']-1)).strftime("%a %b %d"), axis=1)
    st.dataframe(display_df[['Day', 'Date', 'Activity', 'Miles', 'Hrs', 'Region']], hide_index=True, use_container_width=True, height=(len(display_df) + 1) * 35 + 3)


# --- 7. CONDITIONS ---
st.divider()
st.subheader("Conditions")

if st.button("🔄 Refresh Live Data"):
    with st.spinner("Contacting Satellites..."):
        
        # Weather
        tab1, tab2 = st.tabs(["36-Hour Detail", "5-Day Outlook"])
        locs = [("Pyramid (Nixon)", 39.8302, -119.3614), ("Eureka", 40.8021, -124.1637),
                ("Crescent City", 41.7558, -124.2026), ("Brookings", 42.0526, -124.2720),
                ("Coos Bay", 43.3665, -124.2179), ("Forks", 47.9504, -124.3855)]
        
        with tab1:
            cols = st.columns(3)
            for i, (name, lat, lon) in enumerate(locs):
                p = get_nws_forecast_data(lat, lon)
                with cols[i%3]:
                    st.markdown(f"**{name}**")
                    if p:
                        for x in p[:3]:
                            precip_prob = x.get('probabilityOfPrecipitation', {}).get('value', 0)
                            wind = x.get('windSpeed', 'N/A')
                            forecast_text = x['detailedForecast']
                            accum_text = ""
                            if "precipitation" in forecast_text or "rainfall" in forecast_text:
                                sentences = forecast_text.split('.')
                                for s in sentences:
                                    if "amounts" in s or "accumulation" in s:
                                        accum_text += f"💧 {s.strip()}. "
                            
                            st.caption(f"**{x['name']}**: {x['temperature']}°F. {x['shortForecast']}\n*Rain: {precip_prob}% | Wind: {wind}*\n*{accum_text}*")

        with tab2:
            cols = st.columns(3)
            for i, (name, lat, lon) in enumerate(locs):
                p = get_nws_forecast_data(lat, lon)
                with cols[i%3]:
                    st.markdown(f"**{name}**")
                    if p:
                        for x in p[:10:2]: 
                             st.caption(f"**{x['name']}**: {x['temperature']}°F, {x['shortForecast']}")

        # River Gauges
        st.markdown("### 🌊 Live River Gauges")
        
        REGIONS = {
            "NorCal": [
                {"Name": "Smith R nr Crescent City", "ID": "11532500", "Source": "USGS", "Target": "7.0-11.0 ft", "P": "00065", "Note": "The Holy Grail. Drops fast. < 6ft is too low."},
                {"Name": "Eel R a Scotia", "ID": "11477000", "Source": "USGS", "Target": "1500-4500 cfs", "P": "00060", "Note": "Takes forever to clear. Check Turbidity."},
                {"Name": "SF Eel nr Miranda", "ID": "11476500", "Source": "USGS", "Target": "300-1800 cfs", "P": "00060", "Note": "Clears much faster than the main stem."},
                {"Name": "Van Duzen R nr Bridgeville", "ID": "11478500", "Source": "USGS", "Target": "200-1200 cfs", "P": "00060", "Note": "\"The Dirty Van.\" Muddy easily."}
            ],
            "Oregon": [
                {"Name": "Chetco R nr Brookings", "ID": "14400000", "Source": "USGS", "Target": "1200-4000 cfs", "P": "00060", "Note": "2,000 is magic. > 4,000 is tough wading."},
                {"Name": "Elk R abv Hatchery", "ID": "14338000", "Source": "USGS", "Target": "3.5-5.5 ft", "P": "00065", "Note": "Tiny system. Clears in 24 hours."},
                {"Name": "Sixes R at Hwy 101", "ID": "14327150", "Source": "USGS", "Target": "4.0-7.0 ft", "P": "00065", "Note": "Dark tannin water. Fishable higher than you think."},
                {"Name": "Rogue R nr Agness", "ID": "14372300", "Source": "USGS", "Target": "2000-6000 cfs", "P": "00060", "Note": "Big water. Safe bet when small streams blow out."},
                {"Name": "N Umpqua a Winchester", "ID": "14319500", "Source": "USGS", "Target": "1500-4000 cfs", "P": "00060", "Note": "The famous \"Fly Only\" water is upstream."},
                {"Name": "Umpqua R nr Elkton", "ID": "14321000", "Source": "USGS", "Target": "4000-10000 cfs", "P": "00060", "Note": "Big water swinging."}
            ],
            "OP": [
                {"Name": "Bogachiel R nr La Push", "ID": "12043000", "Source": "USGS", "Target": "500-2500 cfs", "P": "00060", "Note": "The local favorite. Gets crowded."},
                {"Name": "Calawah R nr Forks", "ID": "12043300", "Source": "USGS", "Target": "300-1500 cfs", "P": "00060", "Note": "Steep and fast. Clears quickly."},
                {"Name": "Hoh R at US 101", "ID": "12041200", "Source": "USGS", "Target": "1000-4000 cfs", "P": "00060", "Note": "Glacial grey color is normal (\"Hoh Grey\")."},
                {"Name": "Queets R nr Clearwater", "ID": "12040500", "Source": "USGS", "Target": "2000-7000 cfs", "P": "00060", "Note": "Wild, remote, big water."}
            ]
        }
        
        for region, river_list in REGIONS.items():
            st.markdown(f"#### {region}")
            g_cols = st.columns(4)
            for i, r in enumerate(river_list):
                with g_cols[i % 4]:
                    val = get_usgs_simple(r['ID'], r['P'])
                    
                    color = "off"
                    status_icon = ""
                    try:
                        t_str = r['Target'].split(' ')[0]
                        t_min = float(t_str.split('-')[0])
                        t_max = float(t_str.split('-')[1])
                        
                        if val:
                            if val < t_min:
                                color = "off" # Yellow
                                status_icon = "🟡 LOW"
                            elif val > t_max:
                                color = "inverse" # Red
                                status_icon = "🔴 HIGH"
                            else:
                                color = "normal" # Green
                                status_icon = "🟢 GO"
                    except: pass

                    unit = "ft" if "ft" in r['Target'] else "cfs"
                    url = f"https://waterdata.usgs.gov/nwis/uv?site_no={r['ID']}"
                    st.markdown(f"[{r['Name']}]({url})")
                    
                    st.metric(
                        label=status_icon,
                        value=f"{val} {unit}" if val else "--",
                        delta=r['Target'],
                        delta_color=color
                    )
                    st.caption(r['Note'])