import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz
import plotly.express as px


# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Ground Truth",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
.stMetric {
    background-color: #f0f2f6;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# --- MOCK DATABASE (The "Backend") ---
# In a production app, this would connect to PostgreSQL/Neo4j
@st.cache_data
def load_mock_data():
    return {
        "properties": [
            {
                "apn": "060-2358-022-06",
                "address": "1225 6th St",
                "owner": "Sixth Street Industrial Partners LLC",
                "tax_mail": "500 Capitol Mall, Sacramento, CA",
                "value": 4500000,
                "violations": 0,
                "lat": 37.880,
                "lon": -122.300
            },
            {
                "apn": "045-1200-001-00",
                "address": "550 Main St",
                "owner": "550 Main St Holdings LLC",
                "tax_mail": "PO BOX 999, Chicago, IL",  # The "Shell" Link
                "value": 1200000,
                "violations": 12,
                "lat": 37.805,
                "lon": -122.270
            }
        ],
        "portfolio_map": {
            "PO BOX 999, Chicago, IL": 42,  # Owns 42 buildings
            "500 Capitol Mall, Sacramento, CA": 5   # Owns 5 buildings
        }
    }

db = load_mock_data()

# --- LOGIC ENGINE ---
def analyze_occupancy(business_name, property_address):
    # 1. Find Property
    # Simple substring match for demo purposes
    prop = next((p for p in db["properties"] if p["address"] in property_address), None)
    if not prop:
        return None
    
    # 2. Fuzzy Match Owner vs Business
    # If Business Name is very similar to Owner Name -> Owner Occupied
    ratio = fuzz.token_sort_ratio(business_name.upper(), prop["owner"].upper())
    
    # 3. Determine Status
    status = "TENANT"
    if ratio > 80:
        status = "OWNER_OCCUPIED"
    
    # 4. Get Portfolio Size
    portfolio_count = db["portfolio_map"].get(prop["tax_mail"], 1)
    
    return {
        "status": status,
        "owner_name": prop["owner"],
        "match_score": ratio,
        "portfolio_size": portfolio_count,
        "violations": prop["violations"],
        "tax_mail": prop["tax_mail"],
        "lat": prop["lat"],
        "lon": prop["lon"]
    }


# --- UI LAYOUT ---

# Sidebar
with st.sidebar:
    st.header("🔍 Intelligence Scanner")
    st.info("Prototype v0.1")
    st.markdown("---")
    st.write("Debug Tools")
    if st.checkbox("Show Raw Data"):
        st.json(db)

# Main Header
st.title("🏢 Ground Truth")
st.markdown("##### Real Estate Intelligence: Who owns the dirt?")
st.markdown("---")

# Input Section
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("Subject Property")
    # Pre-filled inputs for the demo
    business_input = st.text_input("Business Name (Tenant)", "Boichik Bagels")
    address_input = st.selectbox(
        "Property Address",
        ["1225 6th St, Berkeley", "550 Main St, Oakland (Test Case)"]
    )
    scan_button = st.button("Run Intelligence Trace", type="primary", use_container_width=True)


if scan_button:
    with st.spinner("Accessing Assessor Records..."):
        result = analyze_occupancy(business_input, address_input)
        if result:
            # --- RESULTS SECTION ---
            
            # 1. Top Level Metrics
            m1, m2, m3 = st.columns(3)
            
            # Dynamic Badge Logic
            if result["status"] == "TENANT":
                m1.metric("Occupancy Status", "🛡️ TENANT", delta="Leaseholder", delta_color="off")
            else:
                m1.metric("Occupancy Status", "👑 OWNER", delta="Asset Holder", delta_color="normal")
            
            m2.metric("Portfolio Size", f"{result['portfolio_size']} Units", "Local Holdings")
            
            violation_delta_color = "normal" if result['violations'] == 0 else "inverse"
            m3.metric("Risk Score", f"{result['violations']} Violations", "Code Enforcement", delta_color=violation_delta_color)

            st.divider()
            
            # 2. Deep Dive & Map
            row2_col1, row2_col2 = st.columns([1.2, 1])
            
            with row2_col1:
                st.subheader("🕵️ Investigation Report")
                
                # Intelligence Table
                report_df = pd.DataFrame([
                    {"Metric": "Business Name", "Details": business_input, "Analysis": "Operating Entity"},
                    {"Metric": "Property Owner", "Details": result['owner_name'], "Analysis": f"Match Score: {result['match_score']}%"},
                    {"Metric": "True Beneficiary", "Details": result['tax_mail'], "Analysis": "Taxpayer Mailing Address (Shell Link)"}
                ])
                st.table(report_df)
                
                if result['portfolio_size'] > 10:
                    st.warning(f"⚠️ **CORPORATE LANDLORD:** This property is part of a large portfolio ({result['portfolio_size']} units).")
                else:
                    st.success("✅ **INDEPENDENT LANDLORD:** This appears to be a smaller, stable owner.")

            with row2_col2:
                st.subheader("📍 Portfolio Map")
                
                # Simple Map Visualization
                map_data = pd.DataFrame({
                    'lat': [result['lat']],
                    'lon': [result['lon']],
                    'size': [1000]  # Marker size
                })
                st.map(map_data, zoom=14, color='#ff4b4b')
                st.caption("Red marker indicates subject property. (Portfolio visualization disabled in prototype)")

        else:
            st.error("Property not found in Mock DB. Try '1225 6th St' or '550 Main St'.")
