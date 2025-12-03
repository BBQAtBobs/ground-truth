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
    .element-container iframe { border-radius: 12px; border: 1px solid #e0e0e0; }
    .stMetric { background-color: #f9f9f9; padding: 10px; border-radius: 8px; border: 1px solid #eee; }
    div[data-testid="stExpander"] { border: none; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- ADVANCED DATASET (v4.0) ---
@st.cache_data
def load_data():
    return [
        # --- LANESPLITTER EMPIRE (The User's Request) ---
        {
            "id": 101,
            "name": "Lanesplitter Pizza & Pub",
            "address": "4799 Telegraph Ave, Oakland",
            "type": "Restaurant",
            "owner": "Temescal Telegraph Properties LLC",
            "status": "TENANT", # Business pays rent to the Holding Co.
            "lat": 37.8375, "lon": -122.2625,
            "risk_score": 2,
            "portfolio_group": "TEMESCAL_GRP",
            "desc": "Flagship location. The holding company owns multiple retail shells in this corridor."
        },
        {
            "id": 102,
            "name": "Former Babette / Lanesplitter",
            "address": "2033 San Pablo Ave, Berkeley",
            "type": "Retail Shell",
            "owner": "Temescal Telegraph Properties LLC", # Linked Owner
            "status": "VACANT",
            "lat": 37.8680, "lon": -122.2920,
            "risk_score": 0,
            "portfolio_group": "TEMESCAL_GRP",
            "desc": "Sister property owned by the same investment group. Currently transitioning tenants."
        },

        # --- REGENCY CENTERS (The Corporate Giant) ---
        {
            "id": 201,
            "name": "Whole Foods Market",
            "address": "3000 Telegraph Ave, Berkeley",
            "type": "Grocery Anchor",
            "owner": "Regency Centers LP",
            "status": "TENANT",
            "lat": 37.8564, "lon": -122.2598,
            "risk_score": 0,
            "portfolio_group": "REGENCY_REIT",
            "desc": "Corporate REIT asset. Profits extract to Florida HQ."
        },
        {
            "id": 202,
            "name": "Pleasant Hill Shopping Ctr",
            "address": "650 Contra Costa Blvd",
            "type": "Retail Power Center",
            "owner": "Regency Centers LP",
            "status": "TENANT",
            "lat": 37.9550, "lon": -122.0550, # Further out
            "risk_score": 0,
            "portfolio_group": "REGENCY_REIT",
            "desc": "Massive 230k sqft retail complex owned by the same REIT."
        },

        # --- TELEGRAPH PROPERTY GROUP (The Street Barons) ---
        {
            "id": 301,
            "name": "Amoeba Music",
            "address": "2455 Telegraph Ave, Berkeley",
            "type": "Cultural Icon",
            "owner": "Telegraph Property Group",
            "status": "TENANT",
            "lat": 37.8659, "lon": -122.2585,
            "risk_score": 5,
            "portfolio_group": "TELE_GRP",
            "desc": "Iconic tenant on a month-to-month leverage against a powerful local landlord."
        },
        {
            "id": 302,
            "name": "Student Housing / Retail",
            "address": "2525 Telegraph Ave, Berkeley",
            "type": "Mixed Use",
            "owner": "Telegraph Property Group",
            "status": "TENANT",
            "lat": 37.8665, "lon": -122.2588,
            "risk_score": 0,
            "portfolio_group": "TELE_GRP",
            "desc": "Another asset in the same portfolio, leveraging student housing demand."
        },

        # --- FIELDWORK / INDUSTRIAL ---
        {
            "id": 401,
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

        # --- CHEZ PANISSE (The Solo Owner) ---
        {
            "id": 501,
            "name": "Chez Panisse",
            "address": "1517 Shattuck Ave, Berkeley",
            "type": "Fine Dining",
            "owner": "Chez Panisse Corp",
            "status": "OWNER",
            "lat": 37.8796, "lon": -122.2699,
            "risk_score": 0,
            "portfolio_group": "CHEZ_SOLO",
            "desc": "Owner-Occupied. A rare stable anchor in the dataset."
        },
        
        # --- TEST CASE ---
        {
            "id": 601,
            "name": "Joe's Corner Bodega",
            "address": "550 Main St, Oakland",
            "type": "Retail Small",
            "owner": "550 Main St Holdings LLC",
            "status": "TENANT",
            "lat": 37.8050, "lon": -122.2730,
            "risk_score": 12,
            "portfolio_group": "SLUMLORD_TEST",
            "desc": "High violation count. Shell company disguised as local owner."
        }
    ]

properties = load_data()

# --- PORTFOLIO LOGIC ENGINE ---
def get_related_properties(prop_id, group_id):
    if group_id == "CHEZ_SOLO" or group_id == "SLUMLORD_TEST":
        return []
    # Find all properties with same Group ID, excluding self
    return [p for p in properties if p["portfolio_group"] == group_id and p["id"] != prop_id]

# --- MAP ENGINE ---
def create_map(center_lat, center_lon, zoom, highlight_group=None):
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles="CartoDB positron")
    
    for prop in properties:
        # VISUAL LOGIC
        is_highlighted = highlight_group and prop['portfolio_group'] == highlight_group
        
        if highlight_group and not is_highlighted:
            # Dim unrelated properties if a portfolio is selected
            opacity = 0.4
            color = "gray"
        else:
            opacity = 1.0
            color = "red" if prop["status"] == "TENANT" else "green"
            if prop["status"] == "VACANT": color = "orange"
        
        icon_type = "building"
        if prop["status"] == "OWNER": icon_type = "star"
        if prop["status"] == "VACANT": icon_type = "ban"

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
st.title("🗺️ Ground Truth")
st.caption("Intelligence Scanner: Tap a pin to reveal the owner's portfolio.")

col_map, col_details = st.columns([2, 1])

# --- SESSION STATE FOR SELECTION ---
if 'selected_id' not in st.session_state:
    st.session_state.selected_id = None

# --- MAP INTERACTION ---
with col_map:
    # Check if we need to highlight a specific portfolio
    active_group = None
    if st.session_state.selected_id:
        selected_prop = next((p for p in properties if p["id"] == st.session_state.selected_id), None)
        if selected_prop:
            active_group = selected_prop["portfolio_group"]
            
    # Draw Map
    m = create_map(37.86, -122.27, 12, highlight_group=active_group)
    map_data = st_folium(m, height=600, width="100%")

# Handle Click
if map_data and map_data.get("last_object_clicked"):
    clicked_lat = map_data["last_object_clicked"]["lat"]
    found_prop = next((p for p in properties if abs(p["lat"] - clicked_lat) < 0.0001), None)
    if found_prop:
        st.session_state.selected_id = found_prop["id"]
        st.rerun()

# --- DETAILS PANEL ---
with col_details:
    if st.session_state.selected_id:
        # Get Current Property
        prop = next((p for p in properties if p["id"] == st.session_state.selected_id), None)
        
        # Header
        st.subheader(prop["name"])
        st.caption(f"📍 {prop['address']}")
        st.divider()

        # Status Badge
        if prop["status"] == "OWNER":
            st.success("👑 **OWNER OCCUPIED**")
        elif prop["status"] == "VACANT":
            st.warning("⚠️ **VACANT ASSET**")
        else:
            st.error("🛡️ **TENANT (LEASEHOLDER)**")

        # Owner Info
        st.info(f"**Landlord:** {prop['owner']}")
        st.write(prop['desc'])

        # --- PORTFOLIO FEATURE (The New Part) ---
        related = get_related_properties(prop["id"], prop["portfolio_group"])
        
        if related:
            st.markdown("### 🏢 Portfolio Holdings")
            st.caption(f"This owner controls {len(related)} other assets in this dataset.")
            
            for rel in related:
                with st.expander(f"📍 {rel['name']}"):
                    st.write(f"**Address:** {rel['address']}")
                    st.write(f"**Status:** {rel['status']}")
                    if st.button(f"Jump to {rel['id']}", key=f"btn_{rel['id']}"):
                        st.session_state.selected_id = rel["id"]
                        st.rerun()
        else:
            st.markdown("### 🏢 Portfolio Holdings")
            st.caption("No other assets found in this dataset for this owner.")

    else:
        st.info("👈 **Select a property to start.**")
        st.markdown("#### New in v4.0")
        st.markdown("- **Portfolio Linking:** Click 'Lanesplitter' to see their other holdings.")
        st.markdown("- **Vacancy Tracking:** Added 'Former Babette' as a vacant portfolio asset.")
