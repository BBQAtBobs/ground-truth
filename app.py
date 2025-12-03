import streamlit as st
import pandas as pd
import plotly.express as px
from fuzzywuzzy import fuzz

# --- CONFIGURATION & ASSETS ---
st.set_page_config(
    page_title="Ground Truth",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a "SaaS" look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #2c3e50; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #fff; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- REAL DATA CONNECTORS (PLACEHOLDERS) ---

def fetch_real_property_data(address):
    """
    This is where you plug in the API Key (e.g., Regrid, Estated, ATTOM).
    Currently returns MOCK data if the API key is missing.
    """
    # REAL WORLD CODE WOULD LOOK LIKE THIS:
    # response = requests.get(f"https://api.regrid.com/v1/search?query={address}&token=YOUR_API_KEY")
    # data = response.json()
    
    # FOR PROTOTYPE: Returning refined Mock Data
    mock_db = [
        {
            "address": "1225 6th St, Berkeley, CA",
            "owner": "Sixth Street Industrial Partners LLC",
            "tax_mail": "500 Capitol Mall, Sacramento, CA",
            "market_value": 4500000,
            "sqft": 18500,
            "year_built": 1956,
            "zone": "Industrial (M-2)",
            "lat": 37.880, "lon": -122.300,
            "violations": []
        },
        {
            "address": "550 Main St, Oakland, CA",
            "owner": "550 Main St Holdings LLC",
            "tax_mail": "PO BOX 999, Chicago, IL",
            "market_value": 1200000,
            "sqft": 4200,
            "year_built": 1920,
            "zone": "Commercial (C-1)",
            "lat": 37.805, "lon": -122.270,
            "violations": ["Code 101: Unsafe Wiring (2023)", "Code 304: Mold (2022)"]
        }
    ]
    
    # Simple search simulation
    return next((item for item in mock_db if address.split(' ')[0] in item['address']), None)

# --- LOGIC ENGINE ---
def analyze_occupancy(business_name, property_data):
    if not property_data:
        return None

    # 1. Fuzzy Match (The "Owner vs Tenant" Logic)
    ratio = fuzz.token_sort_ratio(business_name.upper(), property_data["owner"].upper())
    status = "TENANT" if ratio < 75 else "OWNER_OCCUPIED"
    
    # 2. Portfolio Logic (Simulated for now)
    # In real app: Query Graph DB for this 'tax_mail'
    portfolio_size = 42 if "Chicago" in property_data["tax_mail"] else 1
    
    return {
        "status": status,
        "match_score": ratio,
        "portfolio_size": portfolio_size,
        "data": property_data
    }

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/skyscraper.png", width=60)
    st.title("Ground Truth")
    st.caption("v2.0 | Connected: **Local Mode**")
    
    st.markdown("### 🕵️ Recent Scans")
    st.code("Boichik Bagels\n> 1225 6th St")
    st.code("Joe's Pizza\n> 550 Main St")
    
    st.markdown("---")
    st.markdown("### ⚙️ Filters")
    st.checkbox("Show Distressed Only")
    st.checkbox("Highlight Corporate Owners")
    
    st.info("💡 **Tip:** Enter the Business Name exactly as it appears on the license.")

# --- MAIN INTERFACE ---

# 1. Search Hero Section
st.markdown("## 🔍 Intelligence Scanner")
c1, c2 = st.columns([2, 1])
with c1:
    business_input = st.text_input("Business Name", "Boichik Bagels", placeholder="e.g. Starbucks")
with c2:
    # In real app, this is a text_input, but a selectbox is safer for demos
    address_input = st.selectbox("Search Address", ["1225 6th St, Berkeley, CA", "550 Main St, Oakland, CA"])

if st.button("Run Trace", type="primary", use_container_width=True):
    with st.spinner("Triangulating Asset Data..."):
        
        # Run the "Engine"
        prop_data = fetch_real_property_data(address_input)
        result = analyze_occupancy(business_input, prop_data)

        if result:
            # 2. High-Level Findings (The "At a Glance" Header)
            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            
            # Badge Logic
            if result["status"] == "TENANT":
                m1.metric("Status", "🛡️ TENANT", "Leaseholder", delta_color="off")
            else:
                m1.metric("Status", "👑 OWNER", "Asset Holder", delta_color="normal")
            
            m2.metric("True Owner", result['data']['owner'][:15]+"...", "View Details below")
            m3.metric("Portfolio Est.", f"{result['portfolio_size']} Units", "Linked via Tax Addr")
            
            risk_label = "Low" if not result['data']['violations'] else "High"
            m4.metric("Risk Level", risk_label, f"{len(result['data']['violations'])} Active Flags", delta_color="inverse")

            # 3. Tabbed Deep Dive
            st.markdown("### Asset Intelligence")
            tab1, tab2, tab3 = st.tabs(["📊 Ownership Profile", "📍 The Monopoly Map", "⚠️ Risk & Violations"])

            with tab1:
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    st.markdown("#### Entity Resolution")
                    st.dataframe(pd.DataFrame({
                        "Metric": ["Business Input", "Property Owner", "Match Score", "Taxpayer Address"],
                        "Value": [business_input, result['data']['owner'], f"{result['match_score']}%", result['data']['tax_mail']]
                    }), hide_index=True, use_container_width=True)
                    
                    if result['portfolio_size'] > 10:
                        st.error(f"**Corporate Alert:** The owner uses a centralized mailing address in {result['data']['tax_mail'].split(',')[-2]}. This indicates a large holding company.")
                
                with col_b:
                    st.markdown("#### Building Data")
                    st.caption(f"Zoning: {result['data']['zone']} | Built: {result['data']['year_built']}")
                    st.metric("Assessed Value", f"${result['data']['market_value']:,}")
                    st.progress(result['match_score'], text="Name Match Confidence")

            with tab2:
                st.markdown("#### Portfolio Visualization")
                st.info("Red markers indicate other properties linked to this owner.")
                
                # Dynamic Map
                map_df = pd.DataFrame({'lat': [result['data']['lat']], 'lon': [result['data']['lon']]})
                st.map(map_df, zoom=14, color='#ff4b4b')

            with tab3:
                st.markdown("#### Code Enforcement History")
                if result['data']['violations']:
                    for v in result['data']['violations']:
                        st.warning(f"🚩 **Active:** {v}")
                else:
                    st.success("✅ No active violations found in the last 36 months.")
        
        else:
            st.error("Property data not found in current database.")
