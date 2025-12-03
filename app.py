import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Ground Truth Map",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    /* Clean up the map border */
    .element-container iframe { border-radius: 12px; border: 1px solid #e0e0e0; }
    /* Card styling for metrics */
    .stMetric { background-color: #f9f9f9; padding: 10px; border-radius: 8px; border: 1px solid #eee; }
    /* Remove padding from expanders */
    div[data-testid="stExpander"] { border: none; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- REAL WORLD DATASET (v4.1) ---
@st.cache_data
def load_data():
    return [
        # --- THE "RASPUTIN" EMPIRE (Ken Sarachan) ---
        # He owns multiple key corners, some famous for being long-term vacancies.
        {
            "id": 101,
            "name": "Rasputin Music (Flagship)",
            "address": "2401 Telegraph Ave, Berkeley",
            "type": "Retail Icon",
            "owner": "Ken Sarachan (Kick-Axe Properties)",
            "status": "OWNER", # He owns the business AND the building
            "lat": 37.8654, "lon": -122.2588,
            "risk_score": 5,
            "portfolio_group": "SARACHAN_EMP",
            "desc": "The headquarters of the Rasputin empire. Sarachan is the largest independent landlord on the avenue."
        },
        {
            "id": 102,
            "name": "Bear Basics / Anastasia's",
            "address": "2350 Telegraph Ave, Berkeley",
            "type": "Retail / Mixed Use",
            "owner": "Ken Sarachan (Kick-Axe Properties)",
            "status": "OWNER",
            "lat": 37.8648, "lon": -122.2583,
            "risk_score": 0,
            "portfolio_group": "SARACHAN_EMP",
            "desc": "Another corner owned by Sarachan. Currently proposed for housing redevelopment."
        },
        {
            "id": 103,
            "name": "The 'Mad Monk' Lot",
            "address": "2454 Telegraph Ave, Berkeley",
            "type": "Vacant Lot (Historic)",
            "owner": "Ken Sarachan (Kick-Axe Properties)",
            "status": "VACANT",
            "lat": 37.8658, "lon": -122.2582,
            "risk_score": 15, # High blight score
            "portfolio_group": "SARACHAN_EMP",
            "desc": "Infamous vacant lot. Burned down in the 90s, held as a vacant lot by Sarachan for decades."
        },

        # --- LANESPLITTER (The Temescal Cluster) ---
        {
            "id": 201,
            "name": "Lanesplitter Pizza & Pub",
            "address": "4799 Telegraph Ave, Oakland",
            "type": "Restaurant",
            "owner": "Temescal Telegraph Properties LLC",
            "status": "TENANT", 
            "lat": 37.8375, "lon": -122.2625,
            "risk_score": 2,
            "portfolio_group": "TEMESCAL_GRP",
            "desc": "The business is a tenant. The landlord (Temescal Telegraph Props) owns other shells in this corridor."
        },
        {
            "id": 202,
            "name": "Former Babette (2033 San Pablo)",
            "address": "2033 San Pablo Ave, Berkeley",
            "type": "Retail Shell",
            "owner": "Temescal Telegraph Properties LLC",
            "status": "VACANT",
            "lat": 37.8680, "lon": -122.2920,
            "risk_score": 0,
            "portfolio_group": "TEMESCAL_GRP",
            "desc": "Sister property to Lanesplitter. Currently vacant/transitioning."
        },

        # --- THE CORRECTED "TELEGRAPH" OWNERS ---
        {
            "id": 301,
            "name": "Amoeba Music",
            "address": "2455 Telegraph Ave, Berkeley",
            "type": "Cultural Icon",
            "owner": "Amoeba Music Inc. (Prinz/Weinstein)", # CORRECTED OWNER
            "status": "OWNER",
            "lat": 37.8659, "lon": -122.2585,
            "risk_score": 0,
            "portfolio_group": "AMOEBA_SOLO",
            "desc": "Owners Dave Prinz and Marc Weinstein own the dirt. They are currently planning to build housing on top."
        },
        {
            "id": 302,
            "name": "Student Housing (2525)",
            "address": "2525 Telegraph Ave, Berkeley",
            "type": "Student Housing",
            "owner": "Ali Eslami (Private Investor)", # CORRECTED OWNER
            "status": "TENANT",
            "lat": 37.8665, "lon": -122.2588,
            "risk_score": 0,
            "portfolio_group": "ESLAMI_GRP",
            "desc": "Privately held student housing block. Distinct from the Amoeba ownership."
        },

        # --- REGENCY (The REIT) ---
        {
            "id": 401,
            "name": "Whole Foods Market",
            "address": "3000 Telegraph Ave, Berkeley",
            "type": "Grocery Anchor",
            "owner": "Regency Centers LP",
            "status": "TENANT",
            "lat": 37.8564, "lon": -122.2598,
            "risk_score": 0,
            "portfolio_group": "REGENCY_REIT",
            "desc": "Owned by a Florida-based REIT. Part of a national portfolio of grocery-anchored centers."
        },
        
        # --- FIELDWORK (Industrial) ---
        {
            "id": 501,
            "name": "Fieldwork Brewing Co.",
            "address": "1160 6th St, Berkeley",
            "type": "Industrial Taproom",
            "owner": "Sixth Street Industrial Partners",
            "status": "TENANT",
            "lat": 37.8813, "lon": -122.3021,
            "risk_score": 0,
            "portfolio_group": "SIXTH_ST",
            "desc": "Part of the Gilman Industrial District portfolio."
        },
        
        # --- CHEZ PANISSE (Control) ---
        {
            "id": 601,
            "name": "Chez Panisse",
            "address": "1517 Shattuck Ave, Berkeley",
            "type": "Fine Dining",
            "owner": "Chez Panisse Corp",
            "status": "OWNER",
            "lat": 37.8796, "lon": -122.2699,
            "risk_score": 0,
            "portfolio_group": "CHEZ_SOLO",
            "desc": "Owner-Occupied. A rare stable anchor in the dataset."
        }
    ]

properties = load_data()

# --- PORTFOLIO LOGIC ENGINE ---
def get_related_properties(prop_id, group_id):
    # Filter for same Group ID, but exclude the property currently selected
    return [p for p in properties if p["portfolio_group"] == group_id and p["id"] != prop_id]

# --- MAP ENGINE ---
def create_map(center_lat, center_lon, zoom, highlight_group=None):
    # Base Map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles="CartoDB positron")
    
    for prop in properties:
        # VISUAL HIGHLIGHT LOGIC
        is_highlighted = highlight_group and prop['portfolio_group'] == highlight_group
        
        # Determine Visual Style
        if highlight_group and not is_highlighted:
            # Dim unrelated properties
            opacity = 0.3
            color = "gray"
        else:
            # Normal visibility
            opacity = 1.0
            color = "red" if prop["status"] == "TENANT" else "green"
            if prop["status"] == "VACANT": color = "orange" # Orange for vacancy
        
        # Icons
        icon_type = "building"
        if prop["status"] == "OWNER": icon_type = "star"
        if prop["status"] == "VACANT": icon_type = "ban"

        # Popup HTML
        html = f"""
        <div style='font-family: sans-serif; width: 180px;'>
            <strong style='font-size: 14px;'>{prop['name']}</strong><br>
            <span style='color: #666; font-size: 11px;'>{prop['address']}</span><br>
            <hr style='margin: 4px 0; border: 0; border-top: 1px solid #eee;'>
            Status: <b>{prop['status']}</b>
        </div>
        """
        
        folium.Marker(
            [prop['lat'], prop['lon']],
            popup=folium.Popup(html, max_width=250),
            tooltip=prop["name"],
            icon=folium.Icon(color=color, icon=icon_type, prefix='fa'),
            opacity=opacity
        ).add_to(m)
    
    return m

# --- APP LAYOUT ---
st.
