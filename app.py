import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from fuzzywuzzy import fuzz

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Ground Truth Map",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed" # Hide sidebar to give map more space
)

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    /* Make the map container tighter */
    .element-container iframe { border-radius: 12px; border: 2px solid #e0e0e0; }
    /* Style the metrics to look like cards */
    .stMetric { background-color: white; padding: 10px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- MOCK DATA (With GPS) ---
@st.cache_data
def load_data():
    return [
        {
            "id": 1,
            "name": "Boichik Bagels Factory",
            "address": "1225 6th St, Berkeley",
            "type": "Industrial Bakery",
            "owner": "Sixth Street Industrial Partners LLC",
            "status": "TENANT", # The "Truth"
            "lat": 37.8805,
            "lon": -122.3005,
            "risk_score": 0,
            "desc": "Large industrial warehouse converted to bagel factory."
        },
        {
            "id": 2,
            "name": "Joe's Corner Store",
            "address": "550 Main St, Oakland",
            "type": "Retail",
            "owner": "550 Main St Holdings LLC",
            "status": "TENANT",
            "lat": 37.8050,
            "lon": -122.2730,
            "risk_score": 12, # High violations
            "desc": "Corner bodega with active code violations."
        },
        {
            "id": 3,
            "name": "Oakland Hardware",
            "address": "400 20th St, Oakland",
            "type": "Retail",
            "owner": "Oakland Hardware Inc",
            "status": "OWNER",
            "lat": 37.8080,
            "lon": -122.2680,
            "risk_score": 0,
            "desc": "Family owned since 1980. Low displacement risk."
        }
    ]

properties = load_data()

# --- HELPER: MAP GENERATOR ---
def create_map(center_lat, center_lon, zoom):
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles="CartoDB positron")
    
    for prop in properties:
        # Color Logic
        color = "red" if prop["status"] == "TENANT" else "green"
        icon = "building" if prop["status"] == "TENANT" else "star"
        
        # HTML Popup (The "Hover" summary)
        html = f"""
        <div style='font-family: sans-serif; width: 200px;'>
            <b>{prop['name']}</b><br>
            <span style='color: grey; font-size: 12px;'>{prop['address']}</span><br>
            <hr style='margin: 5px 0;'>
            Status: <b>{prop['status']}</b><br>
            Owner: {prop['owner']}
        </div>
        """
        
        folium.Marker(
            [prop['lat'], prop['lon']],
            popup=folium.Popup(html, max_width=300),
            tooltip=prop["name"],
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        ).add_to(m)
    
    return m

# --- MAIN APP LAYOUT ---

st.title("🗺️ Ground Truth: Neighborhood Explorer")
st.markdown("Click any pin to see who really owns the property.")

col_map, col_details = st.columns([2, 1])

with col_map:
    # Render the Map
    # We use a default center between Berkeley and Oakland
    m = create_map(37.84, -122.28, 12)
    
    # st_folium allows bidirectional communication (we know what you clicked)
    map_data = st_folium(m, height=600, width="100%")

# --- INTERACTION LOGIC ---
# If a user clicks a marker, 'last_object_clicked' will contain the Lat/Lon
clicked_prop = None

if map_data and map_data.get("last_object_clicked"):
    clicked_lat = map_data["last_object_clicked"]["lat"]
    # Find the property in our DB that matches this location
    # (In real life we use IDs, but Lat/Lon works for this demo)
    clicked_prop = next((p for p in properties if abs(p["lat"] - clicked_lat) < 0.0001), None)

# --- THE DETAILS PANEL (Overlay) ---
with col_details:
    if clicked_prop:
        # HEADER
        st.header(clicked_prop["name"])
        st.caption(clicked_prop["address"])
        
        # TAGS
        if clicked_prop["status"] == "OWNER":
            st.success("👑 **Owner-Occupied** (Community Stakeholder)")
        else:
            st.error("🛡️ **Tenant Business** (Leaseholder)")
            
        st.markdown("---")
        
        # KEY INTEL
        st.markdown("#### 🕵️ Intelligence Brief")
        st.info(f"**True Owner:** {clicked_prop['owner']}")
        st.write(f"**Description:** {clicked_prop['desc']}")
        
        # METRICS
        c1, c2 = st.columns(2)
        c1.metric("Building Type", clicked_prop["type"])
        
        risk_color = "normal" if clicked_prop['risk_score'] == 0 else "inverse"
        c2.metric("Violations", clicked_prop['risk_score'], delta_color=risk_color)
        
        # ACTION
        st.markdown("###")
        if st.button("📄 View Full Dossier", type="primary", use_container_width=True):
            st.toast("Opening full report database...", icon="📂")
            # This is where you would route to a new page
            
    else:
        # Default State (No Selection)
        st.info("👈 **Select a property on the map** to reveal ownership details.")
        
        st.markdown("### Legend")
        st.markdown("🟢 **Owner-Occupied:** The business owns the building.")
        st.markdown("🔴 **Tenant:** The business pays rent to a landlord.")
        
        st.markdown("---")
        st.caption("Map centered on East Bay, CA. Data is for demonstration purposes.")
