import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from supabase import create_client
import re
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Socio-Economic Field Assessment Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 1.2rem;
        border-radius: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-title {
        color: #64748b;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .metric-value {
        color: #0f172a;
        font-size: 1.75rem;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar: Configuration & Filters ---
st.sidebar.title("⚙️ Dashboard Controls")

# Credentials: Read from secrets, environment variables, or sidebar inputs
default_url = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL", ""))
default_key = st.secrets.get("SUPABASE_ANON_KEY", os.environ.get("SUPABASE_ANON_KEY", ""))

with st.sidebar.expander("Supabase Connection", expanded=(not default_url or not default_key)):
    supabase_url = st.text_input("Project URL", value=default_url, placeholder="https://xyz.supabase.co")
    supabase_key = st.text_input("Anon API Key", value=default_key, type="password", placeholder="eyJhbGciOi...")
    st.caption("Tip: On Streamlit Cloud, add these to **App Settings ➔ Secrets**.")

# --- Supabase Data Fetching ---
@st.cache_data(ttl=30)
def fetch_survey_data(url: str, key: str):
    if not url or not key:
        return pd.DataFrame()
    try:
        supabase = create_client(url, key)
        res = supabase.table("survey_responses").select("*").order("created_at", desc=True).execute()
        df = pd.DataFrame(res.data)
        return df
    except Exception as e:
        st.sidebar.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()

# Load Data
df = fetch_survey_data(supabase_url, supabase_key)

# Fallback Demo Data Generator if Supabase is not yet populated
def get_demo_data():
    return pd.DataFrame([
        {
            "id": "DEMO-001",
            "created_at": "2026-09-20T10:00:00Z",
            "full_name": "Sanket Jadhav",
            "email": "sanket@example.com",
            "gender": "Male",
            "age": 28,
            "locality": "Sector 4, Greenfield Ward",
            "household_members": "3 to 4",
            "highest_qualification": "Undergraduate",
            "members_studying": "1",
            "distance_to_education": "1 to 3 km",
            "education_difficulties": ["Transportation"],
            "employment_status": "Employed",
            "primary_occupation": "Private job",
            "earning_members": "2",
            "monthly_income": "30,000 to 50,000 INR",
            "house_type": "Apartment or Flat",
            "available_rooms": "3",
            "has_electricity": "Yes",
            "drinking_water_source": "Tap water",
            "water_available_year_round": "Yes",
            "toilet_access": "Private toilet",
            "primary_cooking_fuel": "LPG",
            "waste_disposal": "Municipal or local collection",
            "has_internet": "Yes",
            "internet_devices": ["Smartphone", "Laptop"],
            "rating_education": 4,
            "rating_healthcare": 4,
            "rating_transportation": 3,
            "rating_banking": 5,
            "rating_markets": 4,
            "biggest_problems": ["Waste management"],
            "highest_priority_improvement": ["Roads and transport"],
            "photo_urls": ["https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=600&q=80"],
            "surveyor_notes": "[GPS: 19.076090, 72.877426] Good infrastructure, road maintenance requested."
        },
        {
            "id": "DEMO-002",
            "created_at": "2026-09-20T11:15:00Z",
            "full_name": "Anita Patil",
            "email": "anita@example.com",
            "gender": "Female",
            "age": 42,
            "locality": "Old Colony, Ward 12",
            "household_members": "5 to 6",
            "highest_qualification": "Secondary",
            "members_studying": "2",
            "distance_to_education": "3 to 5 km",
            "education_difficulties": ["Financial problems", "Distance"],
            "employment_status": "Self-employed",
            "primary_occupation": "Business",
            "earning_members": "1",
            "monthly_income": "20,000 to 30,000 INR",
            "house_type": "Concrete House / Brick House",
            "available_rooms": "2",
            "has_electricity": "Yes",
            "drinking_water_source": "Borewell",
            "water_available_year_round": "Sometimes",
            "toilet_access": "Shared toilet",
            "primary_cooking_fuel": "LPG",
            "waste_disposal": "Community collection point",
            "has_internet": "Yes",
            "internet_devices": ["Smartphone"],
            "rating_education": 3,
            "rating_healthcare": 2,
            "rating_transportation": 2,
            "rating_banking": 3,
            "rating_markets": 3,
            "biggest_problems": ["Drinking water", "Sanitation"],
            "highest_priority_improvement": ["Drinking water", "Sanitation"],
            "photo_urls": ["https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=600&q=80"],
            "surveyor_notes": "[GPS: 19.082500, 72.884200] Water tanker dependency during summers."
        }
    ])

is_demo = False
if df.empty:
    st.sidebar.warning("⚡ Showing Demo Household Records. Connect your Supabase credentials to view live field records.")
    df = get_demo_data()
    is_demo = True
else:
    st.sidebar.success(f" Connected to Supabase ({len(df)} records synced)")

# --- Sidebar Filters ---
st.sidebar.subheader("Filter Data")
localities = ["All"] + sorted(list(df['locality'].dropna().unique()))
selected_locality = st.sidebar.selectbox("Filter by Locality", localities)

if selected_locality != "All":
    df_filtered = df[df['locality'] == selected_locality]
else:
    df_filtered = df.copy()

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# --- Main Dashboard Header ---
st.title("🏡 Socio-Economic Community Assessment")
st.markdown("Field Survey Operations, Multi-Dimensional Indicators, and GIS Ground-Truth Mapping")

if is_demo:
    st.info("💡 Displaying preview records. Submissions from the surveyor web app will automatically populate here in real-time.")

# --- Top Key Metrics ---
m1, m2, m3, m4, m5 = st.columns(5)

total_households = len(df_filtered)
total_photos = sum([len(p) for p in df_filtered['photo_urls'] if isinstance(p, list)])

# Percentages
elec_pct = (df_filtered['has_electricity'] == 'Yes').mean() * 100 if total_households > 0 else 0
water_pct = (df_filtered['drinking_water_source'] == 'Tap water').mean() * 100 if total_households > 0 else 0
toilet_pct = (df_filtered['toilet_access'] == 'Private toilet').mean() * 100 if total_households > 0 else 0

m1.metric("Households Surveyed", total_households)
m2.metric("Photos Uploaded", total_photos)
m3.metric("Electricity Access", f"{elec_pct:.1f}%")
m4.metric("Piped Water Access", f"{water_pct:.1f}%")
m5.metric("Private Sanitation", f"{toilet_pct:.1f}%")

st.markdown("---")

# --- Tabs: Analytics, GIS Map, Photo Evidence, Raw Submissions ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Socio-Economic Indicators",
    "🗺️ Geospatial / GIS Mapping",
    "📸 Household Photo Evidence",
    "📋 Field Records Table"
])

# ================= TAB 1: Analytics =================
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Monthly Household Income Distribution")
        income_order = [
            "Below 10,000 INR", "10,000 to 20,000 INR", "20,000 to 30,000 INR",
            "30,000 to 50,000 INR", "50,000 to 75,000 INR", "Above 75,000 INR", "Prefer not to say"
        ]
        inc_counts = df_filtered['monthly_income'].value_counts().reindex(income_order).dropna().reset_index()
        inc_counts.columns = ['Income Bracket', 'Households']
        fig_inc = px.bar(inc_counts, x='Income Bracket', y='Households', color='Households', color_continuous_scale='Blues')
        fig_inc.update_layout(xaxis_tickangle=-30, margin=dict(t=20, b=50, l=20, r=20))
        st.plotly_chart(fig_inc, use_container_width=True)

    with c2:
        st.subheader("House Structural Types")
        house_counts = df_filtered['house_type'].value_counts().reset_index()
        house_counts.columns = ['House Type', 'Count']
        fig_house = px.pie(house_counts, names='House Type', values='Count', hole=0.45, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_house.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_house, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Primary Occupations")
        occ_counts = df_filtered['primary_occupation'].value_counts().reset_index()
        occ_counts.columns = ['Occupation', 'Count']
        fig_occ = px.bar(occ_counts, x='Count', y='Occupation', orientation='h', color='Count', color_continuous_scale='Teal')
        fig_occ.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_occ, use_container_width=True)

    with c4:
        st.subheader("Public Services Quality Ratings (1: Poor ➔ 5: Good)")
        services = {
            'rating_education': 'Education',
            'rating_healthcare': 'Healthcare',
            'rating_transportation': 'Transport',
            'rating_banking': 'Banking',
            'rating_markets': 'Markets'
        }
        avg_ratings = []
        for col_name, srv_label in services.items():
            if col_name in df_filtered.columns:
                avg_val = pd.to_numeric(df_filtered[col_name], errors='coerce').mean()
                avg_ratings.append({"Service": srv_label, "Avg Rating": round(avg_val, 2)})
        
        df_srv = pd.DataFrame(avg_ratings)
        fig_srv = px.bar(df_srv, x='Service', y='Avg Rating', range_y=[0, 5], color='Avg Rating', color_continuous_scale='Viridis', text='Avg Rating')
        fig_srv.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_srv, use_container_width=True)

# ================= TAB 2: GIS Mapping =================
with tab2:
    st.subheader("Geospatial Household Ground-Truth Map")
    st.caption("Pins show households tagged with GPS coordinates during door-to-door field visits.")

    # Parse GPS from surveyor_notes (format: [GPS: lat, lon])
    def parse_gps(notes):
        if not isinstance(notes, str):
            return None, None
        match = re.search(r'\[GPS:\s*([+-]?\d+\.?\d*),\s*([+-]?\d+\.?\d*)\]', notes)
        if match:
            return float(match.group(1)), float(match.group(2))
        return None, None

    gps_coords = [parse_gps(n) for n in df_filtered['surveyor_notes']]
    valid_coords = [(lat, lon, df_filtered.iloc[i]) for i, (lat, lon) in enumerate(gps_coords) if lat is not None and lon is not None]

    if valid_coords:
        center_lat = sum([c[0] for c in valid_coords]) / len(valid_coords)
        center_lon = sum([c[1] for c in valid_coords]) / len(valid_coords)
        m = folium.Map(location=[center_lat, center_lon], zoom_start=14, tiles="CartoDB positron")

        for lat, lon, row in valid_coords:
            popup_html = f"""
            <div style="font-family: sans-serif; font-size: 12px; width: 220px;">
                <b style="color: #1e40af; font-size: 13px;">{row['full_name']}</b><br>
                <span>{row['locality']}</span><hr style="margin: 4px 0;">
                <b>House Type:</b> {row['house_type']}<br>
                <b>Monthly Income:</b> {row['monthly_income']}<br>
                <b>Water Source:</b> {row['drinking_water_source']}<br>
                <b>Toilet:</b> {row['toilet_access']}<br>
            </div>
            """
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{row['full_name']} ({row['locality']})",
                icon=folium.Icon(color="blue", icon="home", prefix="fa")
            ).add_to(m)

        st_folium(m, width="100%", height=500)
    else:
        st.info("ℹ️ No GPS coordinates found in the filtered records yet. Tag GPS coordinates on the surveyor web app to display map pins.")

# ================= TAB 3: Photo Evidence Gallery =================
with tab3:
    st.subheader("Household & Living Condition Evidence")
    st.caption("Photos uploaded directly to your Supabase Storage bucket (survey-photos).")

    records_with_photos = df_filtered[df_filtered['photo_urls'].apply(lambda x: isinstance(x, list) and len(x) > 0)]

    if records_with_photos.empty:
        st.info("No photos uploaded yet for the selected records.")
    else:
        for idx, row in records_with_photos.iterrows():
            with st.expander(f"📷 {row['full_name']} — {row['locality']} ({len(row['photo_urls'])} photos)", expanded=True):
                cols = st.columns(min(len(row['photo_urls']), 4))
                for i, photo_url in enumerate(row['photo_urls']):
                    with cols[i % 4]:
                        st.image(photo_url, caption=f"Evidence {i+1}", use_container_width=True)
                st.caption(f"**House Type:** {row['house_type']} | **Water Source:** {row['drinking_water_source']} | **Notes:** {row.get('surveyor_notes', 'None')}")

# ================= TAB 4: Raw Submissions =================
with tab4:
    st.subheader("Field Submissions Records")
    st.dataframe(df_filtered, use_container_width=True)

    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Submissions as CSV",
        data=csv_data,
        file_name="socio_economic_survey_data.csv",
        mime="text/csv"
    )
