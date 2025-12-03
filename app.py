# --- REAL WORLD DATASET (v4.1 - Verified Ownership) ---
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
        }
    ]
