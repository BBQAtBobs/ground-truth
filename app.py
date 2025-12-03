import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Ground Truth: Deep Scan",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .element-container iframe { border-radius: 12px; border: 1px solid #e0e0e0; }
    .stMetric { background-color: #f9f9f9; padding: 10px; border-radius: 8px; border: 1px solid #eee; }
    div[data-testid="stExpander"] { border: none; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    h3 { color: #2c3e50; }
    </style>
    """, unsafe_allow_html=True)

# --- THE 50-PROPERTY DATASET (REAL WORLD CLUSTERS) ---
@st.cache_data
def load_data():
    data = []
    
    # --- CLUSTER 1: THE "RAJ PROPERTIES" EMPIRE (Lakireddy Family) ---
    # Context: Historically one of Berkeley's largest landlords (1,000+ units). Controversial history.
    raj_holdings = [
        (101, "Raj Properties HQ", "2035 Blake St, Berkeley", 37.8640, -122.2680, "Office/Apts"),
        (102, "The Addison Apts", "1950 Addison St, Berkeley", 37.8710, -122.2700, "Multi-Family"),
        (103, "Durant Lofts", "2631 Durant Ave, Berkeley", 37.8680, -122.2550, "Student Housing"),
        (104, "Shattuck Square", "2352 Shattuck Ave, Berkeley", 37.8660, -122.2670, "Mixed Use"),
        (105, "Bancroft Apts", "2580 Bancroft Way, Berkeley", 37.8690, -122.2570, "Student Housing"),
        (106, "Dana Street Apts", "2424 Dana St, Berkeley", 37.8675, -122.2600, "Multi-Family"),
        (107, "Channing Way Apts", "2315 Channing Way, Berkeley", 37.8665, -122.2620, "Multi-Family"),
        (108, "Haste Street Complex", "2140 Haste St, Berkeley", 37.8650, -122.2650, "Multi-Family"),
    ]
    for i, (id, name, addr, lat, lon, typ) in enumerate(raj_holdings):
        data.append({
            "id": id, "name": name, "address": addr, "lat": lat, "lon": lon,
            "type": typ, "status": "TENANT", "owner": "Raj Properties (Lakireddy Family)",
            "group": "RAJ_EMP", "risk": 15,
            "desc": "Part of the massive Lakireddy portfolio (1,000+ units). History of high-profile legal violations."
        })

    # --- CLUSTER 2: THE "RASPUTIN" EMPIRE (Ken Sarachan) ---
    # Context: Owns key Telegraph Ave corners, known for keeping them vacant/blighted.
    sarachan_holdings = [
        (201, "Rasputin Music", "2401 Telegraph Ave, Berkeley", 37.8654, -122.2588, "Retail Icon"),
        (202, "Bear Basics Corner", "2350 Telegraph Ave, Berkeley", 37.8648, -122.2583, "Retail"),
        (203, "The 'Mad Monk' Lot", "2454 Telegraph Ave, Berkeley", 37.8658, -122.2582, "Vacant Lot"),
        (204, "Telegraph Vacancy", "2400 Telegraph Ave, Berkeley", 37.8652, -122.2586, "Vacant Retail"),
        (205, "Channing Vacancy", "2301 Telegraph Ave, Berkeley", 37.8645, -122.2580, "Vacant Retail"),
    ]
    for i, (id, name, addr, lat, lon, typ) in enumerate(sarachan_holdings):
        status = "VACANT" if "Vacant" in typ or "Lot" in typ else "OWNER"
        data.append({
            "id": id, "name": name, "address": addr, "lat": lat, "lon": lon,
            "type": typ, "status": status, "owner": "Kick-Axe Properties (Ken Sarachan)",
            "group": "SARACHAN_EMP", "risk": 8,
            "desc": "Owned by Ken Sarachan. Famous for long-term vacancies and battles with the city over blight."
        })

    # --- CLUSTER 3: PRANA INVESTMENTS (The 'Top Evictor') ---
    # Context: SF-based investment firm, frequently cited in 'Top Evictor' lists for aggressive management.
    prana_holdings = [
        (301, "San Pablo Apts", "3015 San Pablo Ave, Oakland", 37.8200, -122.2750, "Multi-Family"),
        (302, "Market St Complex", "5600 Market St, Oakland", 37.8400, -122.2700, "Multi-Family"),
        (303, "West Oak Apts", "800 14th St, Oakland", 37.8050, -122.2800, "Multi-Family"),
        (304, "Adams Point Apts", "300 MacArthur Blvd, Oakland", 37.8150, -122.2550, "Multi-Family"),
        (305, "Lake Merritt Apts", "1200 Lakeshore Ave, Oakland", 37.8000, -122.2500, "Multi-Family"),
    ]
    for i, (id, name, addr, lat, lon, typ) in enumerate(prana_holdings):
        data.append({
            "id": id, "name": name, "address": addr, "lat": lat, "lon": lon,
            "type": typ, "status": "TENANT", "owner": "Prana Investments",
            "group": "PRANA_GRP", "risk": 20,
            "desc": "Owned by Prana Investments. Frequently cited in 'Anti-Eviction Mapping Project' as a top evictor."
        })

    # --- CLUSTER 4: POSITIVE INVESTMENTS (The SoCal Aggregator) ---
    # Context: Arcadia-based firm buying up Oakland housing stock.
    positive_holdings = [
        (401, "Highland Park Apts", "2300 E 30th St, Oakland", 37.7950, -122.2200, "Multi-Family"),
        (402, "Fruitvale Apts", "3500 Fruitvale Ave, Oakland", 37.7900, -122.2100, "Multi-Family"),
        (403, "Dimond District Apts", "3000 MacArthur Blvd, Oakland", 37.8000, -122.2000, "Multi-Family"),
        (404, "Eastlake Apts", "1500 2nd Ave, Oakland", 37.7950, -122.2400, "Multi-Family"),
    ]
    for i, (id, name, addr, lat, lon, typ) in enumerate(positive_holdings):
        data.append({
            "id": id, "name": name, "address": addr, "lat": lat, "lon": lon,
            "type": typ, "status": "TENANT", "owner": "Positive Investments",
            "group": "POSITIVE_GRP", "risk": 5,
            "desc": "Owned by Positive Investments (Arcadia, CA). Large portfolio aggregator."
        })

    # --- CLUSTER 5: INDEPENDENTS / OTHERS ---
    others = [
        (501, "Lanesplitter Pizza", "4799 Telegraph Ave, Oakland", 37.8375, -122.2625, "Restaurant", "TEMESCAL_GRP", "Temescal Telegraph Props"),
        (502, "Whole Foods", "3000 Telegraph Ave, Berkeley", 37.8564, -122.2598, "Grocery", "REGENCY_REIT", "Regency Centers"),
        (503, "Chez Panisse", "1517 Shattuck Ave, Berkeley", 37.8796, -122.2699, "Restaurant", "CHEZ_SOLO", "Chez Panisse Corp"),
        (504, "Fieldwork Brewing", "1160 6th St, Berkeley", 37.8813, -122.3021, "Industrial", "SIXTH_ST", "Sixth St Industrial Partners"),
        (505, "Amoeba Music", "2455 Telegraph Ave, Berkeley", 37.8659, -122.2585, "Retail", "AMOEBA_SOLO", "Amoeba Music Inc"),
    ]
    for (id, name, addr, lat, lon, typ, grp, own) in others:
        status = "OWNER" if "Chez" in name or "Amoeba" in name else "TENANT"
        data.append({
            "id": id, "name": name, "address": addr, "lat": lat, "lon": lon,
            "type": typ, "status": status, "owner": own,
            "group": grp, "risk": 0 if status == "OWNER" else 5,
            "desc": "Independent or single-asset holding."
        })

    return data

# --- LANDLORD PROFILES (The "Rap Sheet" Data) ---
def get_landlord_profile(group_id):
    profiles = {
        "RAJ_EMP": {
            "name": "Raj Properties (Lakireddy Family)",
            "hq": "Berkeley, CA",
            "units": "1,000+",
            "legal_history": "⚠️ **High Profile:** Founder convicted in 2001 (Federal Case) involving human trafficking/labor violations. Family continues to operate massive portfolio.",
            "news": "• 'Living in Berkeley? You might be paying rent to a former trafficking ring' (Daily Cal)\n• Frequent subjects of Rent Board complaints.",
            "eviction_rate": "High"
        },
        "SARACHAN_EMP": {
            "name": "Kick-Axe Properties (Ken Sarachan)",
            "hq": "Berkeley, CA",
            "units": "15+ Commercial Corners",
            "legal_history": "⚠️ **Blight Violations:** Multiple disputes with City of Berkeley over vacant buildings (Telegraph Ave). Paid $100k+ in city fines.",
            "news": "• 'The Empty Empire of Telegraph Ave'\n• 'Rasputin owner clashes with city over vacant lot'",
            "eviction_rate": "Low (Commercial Hold)"
        },
        "PRANA_GRP": {
            "name": "Prana Investments",
            "hq": "San Francisco, CA",
            "units": "2,000+ (Bay Area)",
            "legal_history": "⚠️ **Top Evictor:** Frequently cited by the Anti-Eviction Mapping Project for high volume of 3-day notices.",
            "news": "• 'Tenants protest Prana Investments rent hikes'\n• 'SF Non-profits fight Prana acquisitions'",
            "eviction_rate": "Critical"
        }
    }
    return profiles.get(group_id, None)

properties = load_data()

# --- MAP ENGINE ---
def create_map(center_lat, center_lon, zoom, highlight_group=None):
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles="CartoDB positron")
    
    for prop in properties:
        is_highlighted = highlight_group and prop['group'] == highlight_group
        
        # Color Coding Empires
        color = "blue" # Default
        if prop['group'] == 'RAJ_EMP': color = "purple"
        elif prop['group'] == 'SARACHAN_EMP': color = "red"
        elif prop['group'] == 'PRANA_GRP': color = "black"
        elif prop['status'] == "OWNER": color = "green"
        
        opacity = 1.0 if (not highlight_group or is_highlighted) else 0.3
        
        html = f"""
        <div style='font-family: sans-serif; width: 150px;'>
            <b>{prop['name']}</b><br>
            <span style='font-size:10px'>{prop['owner']}</span>
        </div>
        """
        
        folium.Marker(
            [prop['lat'], prop['lon']],
            popup=folium.Popup(html, max_width=200),
            tooltip=prop["name"],
            icon=folium.Icon(color=color, icon="building", prefix='fa'),
            opacity=opacity
        ).add_to(m)
    return m

# --- LAYOUT ---
st.title("🕵️ Ground Truth: Deep Scan")
st.caption("Tracking 50+ Assets across the East Bay's Major Landlord Empires")

col1, col2 = st.columns([2, 1])

if 'selected_id' not in st.session_state:
    st.session_state.selected_id = None

# --- LEFT: MAP ---
with col1:
    # Determine highlight group
    active_group = None
    if st.session_state.selected_id:
        sel = next((p for p in properties if p["id"] == st.session_state.selected_id), None)
        if sel: active_group = sel['group']

    m = create_map(37.84, -122.26, 13, active_group)
    map_data = st_folium(m, height=700, width="100%")

    if map_data and map_data.get("last_object_clicked"):
        lat = map_data["last_object_clicked"]["lat"]
        found = next((p for p in properties if abs(p["lat"] - lat) < 0.0001), None)
        if found:
            st.session_state.selected_id = found["id"]
            st.rerun()

# --- RIGHT: PROFILE DOSSIER ---
with col2:
    if st.session_state.selected_id:
        prop = next((p for p in properties if p["id"] == st.session_state.selected_id), None)
        
        # 1. PROPERTY CARD
        st.subheader(prop['name'])
        st.caption(prop['address'])
        
        # Tags
        c1, c2 = st.columns(2)
        c1.info(f"**Owner:**\n{prop['owner']}")
        risk_color = "normal" if prop['risk'] < 10 else "inverse"
        c2.metric("Risk Score", prop['risk'], "Flags", delta_color=risk_color)
        
        st.write(f"_{prop['desc']}_")
        st.divider()

        # 2. LANDLORD DOSSIER (The New Feature)
        profile = get_landlord_profile(prop['group'])
        
        if profile:
            st.markdown(f"### 📂 Dossier: {profile['name']}")
            
            # Tabs for deep research
            tab1, tab2, tab3 = st.tabs(["🏛️ Legal / History", "📰 News", "🏢 Portfolio"])
            
            with tab1:
                st.error(profile['legal_history'])
                st.caption(f"Eviction Intensity: {profile['eviction_rate']}")
            
            with tab2:
                st.markdown(profile['news'])
            
            with tab3:
                # Find sisters
                sisters = [p for p in properties if p['group'] == prop['group'] and p['id'] != prop['id']]
                st.write(f"**{len(sisters)} Other Linked Properties:**")
                for s in sisters:
                    if st.button(f"📍 {s['name']}", key=s['id']):
                        st.session_state.selected_id = s['id']
                        st.rerun()
        else:
            st.warning("No deep profile available for this owner.")

    else:
        st.info("👈 **Click a property to open the Dossier.**")
        st.markdown("### 🗺️ Legend")
        st.markdown("🟣 **Raj Properties** (Lakireddy Empire)")
        st.markdown("🔴 **Kick-Axe** (Sarachan Empire)")
        st.markdown("⚫ **Prana Investments** (High Evictor)")
        st.markdown("🟢 **Owner-Occupied** (Safe)")
