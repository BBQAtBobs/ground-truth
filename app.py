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
    </style>
    """, unsafe_allow_html=True)

# --- REAL WORLD DATASET (The 6 Cases) ---
@st.cache_data
def load_data():
    return [
        {
            "id": 1,
            "name": "Lanesplitter Pizza & Pub",
            "address": "4799 Telegraph Ave, Oakland, CA",
            "type": "Restaurant / Pub",
            "owner": "Temescal Telegraph Properties LLC", 
            "status": "TENANT", 
            "lat": 37.8375, 
            "lon": -122.2625,
            "risk_score": 2, 
            "desc": "Long-standing local favorite. Building is owned by a local holding company, not the business itself."
        },
        {
            "id": 2,
            "name": "Chez Panisse",
            "address": "1517 Shattuck Ave, Berkeley, CA",
            "type": "Fine Dining",
            "owner": "Chez Panisse Corporation",
            "status": "OWNER",
            "lat": 37.8796, 
            "lon": -122.2699,
            "risk_score": 0,
            "desc": "The birthplace of California Cuisine. Alice Waters (and partners) control the asset. A perfect example of a Community Stakeholder."
        },
        {
            "id": 3,
            "name": "Fieldwork Brewing Co.",
            "address": "1160 6th St, Berkeley, CA",
            "type": "Industrial Taproom",
            "owner": "Sixth Street Industrial Partners LLC",
            "status": "TENANT",
            "lat": 37.8813, 
            "lon": -122.3021,
            "risk_score": 0,
            "desc": "Located in the Gilman District. The building is part of a larger industrial portfolio."
        },
        {
            "id": 4,
            "name": "Whole Foods Market",
            "address": "3000 Telegraph Ave, Berkeley, CA",
            "type": "Grocery Anchor",
            "owner": "Regency Centers LP", 
            "status": "TENANT",
            "lat": 37.8564, 
            "lon": -122.2598,
            "risk_score": 0,
            "desc": "Owned by a publicly traded Real Estate Investment Trust (REIT). Rent profits leave the local economy."
        },
        {
            "id": 5,
            "name": "Amoeba Music",
            "address": "2455 Telegraph Ave, Berkeley, CA",
            "type": "Retail Legacy",
            "owner": "Telegraph Property Group", 
            "status": "TENANT",
            "lat": 37.8659, 
            "lon": -122.2585,
            "risk_score": 5, 
            "desc": "Iconic record store. While a cultural anchor, they do not own the dirt, making them vulnerable to future redevelopment."
        },
        {
            "id": 6,
            "name": "Joe's Corner Bodega (TEST)",
            "address": "550 Main St, Oakland, CA",
            "type": "Retail Small",
            "owner": "550 Main St Holdings LLC",
            "status": "TENANT",
            "lat": 37.8050, 
            "lon": -122.2730,
            "risk_score": 12, 
            "desc": "Test case for distress signals. High violation count and out-of-state tax mailing address."
        }
    ]

properties = load_data()

# --- MAP ENGINE ---
def create_map(center_lat, center_lon, zoom):
    # Base Map: Light simplistic theme
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles="CartoDB positron")
    
    for prop in properties:
        # VISUAL LOGIC
        # Green = Owner Occupied (Good)
        # Red = Tenant (Risk/Extraction)
        color = "red" if prop["status"] == "TENANT" else "green"
        icon_type = "building" if prop["status"] == "TENANT" else "star"
        
        # POPUP HTML (Hover Card)
        html = f"""
        <div style='font-family: sans-serif; width: 180px;'>
            <strong style='font-size: 14px;'>{prop['name']}</strong><br>
            <span style='color: #666; font-size: 11px;'>{prop['address']}</span><br>
            <hr style='margin: 4px 0; border: 0; border-top: 1px solid #eee;'>
            Status: <b>{prop['status']}</b><br>
        </div>
        """
        
        folium.Marker(
            [prop['lat'], prop['lon']],
            popup=folium.Popup(html, max_width=250),
            tooltip=prop["name"],
            icon=folium.Icon(color=color, icon=icon_type, prefix='fa')
        ).add_to(m)
    
    return m

# --- APP LAYOUT ---

st.title("🗺️ Ground Truth")
st.caption("Intelligence Scanner: Tap a pin to reveal ownership.")

col_map, col_details = st.columns([2, 1])

with col_map:
    # 1. Render Map (Centered on Berkeley/Oakland border)
    m = create_map(37.84, -122.28, 12)
    
    # 2. Capture User Click
    # This function returns a dict containing info about what was clicked
    map_data = st_folium(m, height=600, width="100%")

# --- CLICK LOGIC ---
clicked_prop = None

if map_data and map_data.get("last_object_clicked"):
    clicked_lat = map_data["last_object_clicked"]["lat"]
    # Find matching property by latitude (simple lookup)
    clicked_prop = next((p for p in properties if abs(p["lat"] - clicked_lat) < 0.0001), None)

# --- DETAIL PANEL (Right Side) ---
with col_details:
    if clicked_prop:
        # Header
        st.subheader(clicked_prop["name"])
        st.caption(f"📍 {clicked_prop['address']}")
        
        st.divider()
        
        # Status Banner
        if clicked_prop["status"] == "OWNER":
            st.success("👑 **OWNER OCCUPIED**")
            st.caption("This business owns their building. They are a stable community stakeholder.")
        else:
            st.error("🛡️ **TENANT (LEASEHOLDER)**")
            st.caption("This business pays rent to a landlord. They do not control the property.")

        # Metrics Grid
        c1, c2 = st.columns(2)
        c1.metric("Landlord", "See Desc", help=clicked_prop['owner'])
        
        # Risk Logic
        if clicked_prop['risk_score'] > 0:
            c2.metric("Risk Flags", clicked_prop['risk_score'], "Violations", delta_color="inverse")
        else:
            c2.metric("Risk Flags", "Clean", "No Violations")

        # Deep Dive Text
        st.markdown("#### 🕵️ Intelligence Brief")
        st.info(f"**Owner of Record:** {clicked_prop['owner']}")
        st.write(clicked_prop['desc'])
        
        st.button("📄 Open Full Dossier", use_container_width=True)

    else:
        # Empty State
        st.markdown("###")
        st.markdown("###")
        st.info("👈 **Select a location on the map.**")
        
        st.markdown("#### Legend")
        st.markdown("🟢 **Owner-Occupied:** (e.g. Chez Panisse)")
        st.markdown("🔴 **Tenant:** (e.g. Whole Foods, Lanesplitter)")
