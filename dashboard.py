import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import urllib.request
import json
import time
import re
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Socio-Economic Community Survey & Analytics",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.25rem;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #64748b;
        margin-bottom: 1.25rem;
    }
    .section-header {
        background: linear-gradient(90deg, #eff6ff 0%, #ffffff 100%);
        border-left: 4px solid #2563eb;
        padding: 0.5rem 0.75rem;
        font-weight: 700;
        font-size: 1rem;
        color: #1e3a8a;
        margin-top: 1rem;
        margin-bottom: 0.75rem;
        border-radius: 0 0.375rem 0.375rem 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Supabase Credentials ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL", "https://tsfzjhapftoacachqute.supabase.co"))
SUPABASE_KEY = st.secrets.get("SUPABASE_ANON_KEY", os.environ.get("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRzZnpqaGFwZnRvYWNhY2hxdXRlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk4OTE4NTQsImV4cCI6MjEwNTQ2Nzg1NH0.60yo8hh51yQvdoGfYdEy8PF0XVLUyePwfuuK-pndJ6o"))

# Session State for Household Counter
if "household_count" not in st.session_state:
    st.session_state.household_count = 1

# --- Supabase Helper Functions ---
def upload_photo_to_supabase(file_bytes, filename):
    timestamp = int(time.time() * 1000)
    sanitized_name = re.sub(r'[^a-zA-Z0-9.-]', '_', filename)
    storage_path = f"households/{timestamp}_{sanitized_name}"
    
    url = f"{SUPABASE_URL}/storage/v1/object/survey-photos/{storage_path}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg"
    }
    
    req = urllib.request.Request(url, data=file_bytes, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 200:
                public_url = f"{SUPABASE_URL}/storage/v1/object/public/survey-photos/{storage_path}"
                return public_url
    except Exception as e:
        st.error(f"Photo upload warning: {e}")
    return None

def insert_survey_record(record_data):
    url = f"{SUPABASE_URL}/rest/v1/survey_responses"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    data = json.dumps([record_data]).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

@st.cache_data(ttl=15)
def fetch_all_responses():
    url = f"{SUPABASE_URL}/rest/v1/survey_responses?select=*&order=created_at.desc"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return pd.DataFrame(data)
    except Exception as e:
        return pd.DataFrame()

# Load Existing Records
df_records = fetch_all_responses()

# --- App Navigation Tabs ---
st.markdown('<div class="main-title">🏡 Socio-Economic Community Survey Portal</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Field Data Collection, Cloud Evidence Storage, and Real-Time GIS Analytics</div>', unsafe_allow_html=True)

nav_tab1, nav_tab2, nav_tab3, nav_tab4, nav_tab5 = st.tabs([
    "📝 Fill Household Survey",
    "📊 Analytics & Indicators",
    "🗺️ Geospatial / GIS Mapping",
    "📸 Photo Evidence Gallery",
    "📋 Submissions Table & Export"
])

# ==============================================================================
# TAB 1: FILL HOUSEHOLD SURVEY (ALL QUESTIONS ON ONE PAGE)
# ==============================================================================
with nav_tab1:
    st.info(f"📍 **Currently Visiting Household #{st.session_state.household_count}** — Fill in the responses below and tap Save at the bottom.")
    
    with st.form(f"survey_form_h{st.session_state.household_count}", clear_on_submit=True):
        
        # --- SECTION 1: Respondent Details ---
        st.markdown('<div class="section-header">Section 1: Respondent Information</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name *", placeholder="e.g. Ramesh Kumar")
            gender = st.radio("Gender *", ["Male", "Female", "Prefer not to say"], horizontal=True)
        with col2:
            email = st.text_input("Email Address *", placeholder="e.g. ramesh@example.com")
            age = st.number_input("Age (Years) *", min_value=1, max_value=120, value=30)
            
        # --- SECTION 2: Location and Household ---
        st.markdown('<div class="section-header">Section 2: Location & Household</div>', unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        with col3:
            locality = st.text_input("Which area or locality do you belong to? *", placeholder="e.g. Ward 4, Azad Nagar")
            gps_tag = st.text_input("GPS Coordinates (Optional)", placeholder="e.g. 19.0760, 72.8777")
        with col4:
            household_members = st.radio("How many members are there in your household? *", 
                                         ["1 to 2", "3 to 4", "5 to 6", "7 to 8", "More than 8"], horizontal=True)

        # --- SECTION 3: Education ---
        st.markdown('<div class="section-header">Section 3: Education</div>', unsafe_allow_html=True)
        highest_qualification = st.selectbox(
            "What is your highest educational qualification? *",
            ["Undergraduate", "Higher Secondary", "Secondary", "Primary", "Diploma", "Postgraduate", "No formal education", "Other"]
        )
        highest_qualification_other = ""
        if highest_qualification == "Other":
            highest_qualification_other = st.text_input("Specify other qualification:")

        col5, col6 = st.columns(2)
        with col5:
            members_studying = st.radio("How many members are currently studying? *", ["0", "1", "2", "3", "4+"], horizontal=True)
        with col6:
            distance_to_education = st.radio("Distance to nearest educational institution? *", 
                                            ["Less than 1 km", "1 to 3 km", "3 to 5 km", "More than 5 km"], horizontal=True)

        education_difficulties = st.multiselect(
            "What is the biggest difficulty in accessing education? (Multi-select) *",
            ["Financial problems", "Distance", "Transportation", "Lack of facilities", "Family responsibilities", "No major difficulty", "Other"],
            default=["No major difficulty"]
        )
        education_difficulties_other = ""
        if "Other" in education_difficulties:
            education_difficulties_other = st.text_input("Specify other education difficulty:")

        # --- SECTION 4: Employment & Income ---
        st.markdown('<div class="section-header">Section 4: Employment & Income</div>', unsafe_allow_html=True)
        col7, col8 = st.columns(2)
        with col7:
            employment_status = st.selectbox("What is your current employment status? *", 
                                            ["Employed", "Self-employed", "Student", "Homemaker", "Unemployed", "Retired", "Other"])
            employment_status_other = ""
            if employment_status == "Other":
                employment_status_other = st.text_input("Specify other employment status:")
                
            primary_occupation = st.selectbox("What is your primary occupation? *", 
                                             ["Private job", "Business", "Government job", "Agriculture", "Daily wage", "Professional", "Other"])
            primary_occupation_other = ""
            if primary_occupation == "Other":
                primary_occupation_other = st.text_input("Specify other occupation:")

        with col8:
            earning_members = st.radio("How many earning members are in household? *", ["0", "1", "2", "3", "4+"], horizontal=True)
            monthly_income = st.selectbox(
                "What is your approximate monthly household income? *",
                ["Below 10,000 INR", "10,000 to 20,000 INR", "20,000 to 30,000 INR", "30,000 to 50,000 INR", "50,000 to 75,000 INR", "Above 75,000 INR", "Prefer not to say"],
                index=2
            )

        # --- SECTION 5: Housing, Water & Basic Amenities ---
        st.markdown('<div class="section-header">Section 5: Housing & Basic Living Conditions</div>', unsafe_allow_html=True)
        col9, col10 = st.columns(2)
        with col9:
            house_type = st.selectbox("What type of house do you live in? *",
                                     ["Concrete House / Brick House", "Apartment or Flat", "Tiled Roof House / Sheet Roof House", "Mud House / Thatched House", "Other"])
            house_type_other = ""
            if house_type == "Other":
                house_type_other = st.text_input("Specify other house type:")

            available_rooms = st.radio("How many rooms are available? *", ["1", "2", "3", "4", "5+"], horizontal=True)
            has_electricity = st.radio("Does household have electricity? *", ["Yes", "No"], horizontal=True)
            toilet_access = st.radio("Access to toilet? *", ["Private toilet", "Shared toilet", "No toilet"], horizontal=True)

        with col10:
            drinking_water_source = st.selectbox("Primary source of drinking water? *",
                                                ["Tap water", "Borewell", "Well", "Tanker", "River or stream", "Other"])
            drinking_water_source_other = ""
            if drinking_water_source == "Other":
                drinking_water_source_other = st.text_input("Specify other water source:")

            water_available_year_round = st.radio("Is water available throughout the year? *", ["Yes", "No", "Sometimes"], horizontal=True)
            primary_cooking_fuel = st.selectbox("Primary cooking fuel? *", ["LPG", "Electricity", "Firewood", "Kerosene", "Other"])
            primary_cooking_fuel_other = ""
            if primary_cooking_fuel == "Other":
                primary_cooking_fuel_other = st.text_input("Specify other cooking fuel:")

            waste_disposal = st.selectbox("Household waste disposal? *",
                                         ["Municipal or local collection", "Community collection point", "Open dumping", "Burning", "Other"])
            waste_disposal_other = ""
            if waste_disposal == "Other":
                waste_disposal_other = st.text_input("Specify other waste disposal method:")

        # --- SECTION 6: Digital Access ---
        st.markdown('<div class="section-header">Section 6: Digital Access</div>', unsafe_allow_html=True)
        col11, col12 = st.columns(2)
        with col11:
            has_internet = st.radio("Does household have internet access? *", ["Yes", "No"], horizontal=True)
        with col12:
            internet_devices = st.multiselect(
                "Primary devices used to access internet? (Multi-select) *",
                ["Smartphone", "Laptop", "Desktop", "Tablet", "Other", "No internet"],
                default=["Smartphone"]
            )
            internet_devices_other = ""
            if "Other" in internet_devices:
                internet_devices_other = st.text_input("Specify other internet device:")

        # --- SECTION 7: Essential Services Rating & Local Problems ---
        st.markdown('<div class="section-header">Section 7: Community Problems & Service Ratings</div>', unsafe_allow_html=True)
        st.write("Rate access to essential services in your area from **1 (Very Poor)** to **5 (Very Good)**:")
        
        r_cols = st.columns(5)
        with r_cols[0]:
            r_edu = st.slider("Education", min_value=1, max_value=5, value=3)
        with r_cols[1]:
            r_health = st.slider("Healthcare", min_value=1, max_value=5, value=3)
        with r_cols[2]:
            r_trans = st.slider("Transport", min_value=1, max_value=5, value=3)
        with r_cols[3]:
            r_bank = st.slider("Banking", min_value=1, max_value=5, value=3)
        with r_cols[4]:
            r_market = st.slider("Markets", min_value=1, max_value=5, value=3)

        biggest_problems = st.multiselect(
            "What is the biggest socio-economic problem in your area? (Multi-select) *",
            ["Unemployment", "Low income", "Education", "Healthcare", "Drinking water", "Sanitation", "Transportation", "Housing", "Waste management", "Digital connectivity", "Other"],
            default=["Waste management"]
        )
        biggest_problems_other = ""
        if "Other" in biggest_problems:
            biggest_problems_other = st.text_input("Specify other problem:")

        highest_priority = st.multiselect(
            "What improvement should be given highest priority? (Multi-select) *",
            ["Education", "Employment", "Healthcare", "Roads and transport", "Drinking water", "Sanitation", "Housing", "Digital connectivity", "Waste management", "Other"],
            default=["Roads and transport"]
        )
        highest_priority_other = ""
        if "Other" in highest_priority:
            highest_priority_other = st.text_input("Specify other priority:")

        # --- SECTION 8: Photo Evidence & Field Notes ---
        st.markdown('<div class="section-header">Section 8: Photo Evidence & Field Notes</div>', unsafe_allow_html=True)
        st.caption("Capture photos using your smartphone camera or upload gallery files. They will be stored directly into your Supabase Storage bucket (`survey-photos`).")
        
        cam_photo = st.camera_input("📷 Take Photo with Smartphone Camera")
        file_photos = st.file_uploader("🖼️ Or Upload Existing Photos from Device", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
        surveyor_notes = st.text_area("Surveyor Observation Notes (Optional)", placeholder="e.g. Verified with neighbor, roof repairs needed, etc.")

        st.markdown("---")
        # Submit Button
        submitted = st.form_submit_button("💾 Save Household Record & Next House", type="primary", use_container_width=True)

        if submitted:
            if not full_name.strip():
                st.error("⚠️ Please enter the respondent's full name.")
            elif not locality.strip():
                st.error("⚠️ Please enter the locality/area name.")
            else:
                with st.spinner("Saving household record and uploading photos to Supabase..."):
                    uploaded_photo_urls = []
                    
                    # Upload camera photo if taken
                    if cam_photo is not None:
                        cam_bytes = cam_photo.getvalue()
                        cam_url = upload_photo_to_supabase(cam_bytes, f"camera_house_{st.session_state.household_count}.jpg")
                        if cam_url:
                            uploaded_photo_urls.append(cam_url)
                            
                    # Upload file photos if attached
                    if file_photos:
                        for f in file_photos:
                            f_bytes = f.getvalue()
                            f_url = upload_photo_to_supabase(f_bytes, f.name)
                            if f_url:
                                uploaded_photo_urls.append(f_url)

                    # Build notes with GPS if entered
                    final_notes = surveyor_notes.strip() if surveyor_notes else ""
                    if gps_tag.strip():
                        final_notes = f"[GPS: {gps_tag.strip()}] {final_notes}".strip()

                    # Construct Record
                    record = {
                        "full_name": full_name.strip(),
                        "email": email.strip() if email.strip() else "not_provided@survey.com",
                        "gender": gender,
                        "age": int(age),
                        "locality": locality.strip(),
                        "household_members": household_members,
                        "highest_qualification": highest_qualification,
                        "highest_qualification_other": highest_qualification_other if highest_qualification_other else None,
                        "members_studying": members_studying,
                        "distance_to_education": distance_to_education,
                        "education_difficulties": education_difficulties,
                        "education_difficulties_other": education_difficulties_other if education_difficulties_other else None,
                        "employment_status": employment_status,
                        "employment_status_other": employment_status_other if employment_status_other else None,
                        "primary_occupation": primary_occupation,
                        "primary_occupation_other": primary_occupation_other if primary_occupation_other else None,
                        "earning_members": earning_members,
                        "monthly_income": monthly_income,
                        "house_type": house_type,
                        "house_type_other": house_type_other if house_type_other else None,
                        "available_rooms": available_rooms,
                        "has_electricity": has_electricity,
                        "drinking_water_source": drinking_water_source,
                        "drinking_water_source_other": drinking_water_source_other if drinking_water_source_other else None,
                        "water_available_year_round": water_available_year_round,
                        "toilet_access": toilet_access,
                        "primary_cooking_fuel": primary_cooking_fuel,
                        "primary_cooking_fuel_other": primary_cooking_fuel_other if primary_cooking_fuel_other else None,
                        "waste_disposal": waste_disposal,
                        "waste_disposal_other": waste_disposal_other if waste_disposal_other else None,
                        "has_internet": has_internet,
                        "internet_devices": internet_devices,
                        "internet_devices_other": internet_devices_other if internet_devices_other else None,
                        "rating_education": int(r_edu),
                        "rating_healthcare": int(r_health),
                        "rating_transportation": int(r_trans),
                        "rating_banking": int(r_bank),
                        "rating_markets": int(r_market),
                        "biggest_problems": biggest_problems,
                        "biggest_problems_other": biggest_problems_other if biggest_problems_other else None,
                        "highest_priority_improvement": highest_priority,
                        "highest_priority_improvement_other": highest_priority_other if highest_priority_other else None,
                        "photo_urls": uploaded_photo_urls,
                        "surveyor_notes": final_notes if final_notes else None
                    }

                    try:
                        insert_survey_record(record)
                        st.success(f"🎉 Household #{st.session_state.household_count} ({full_name}) successfully saved to Supabase with {len(uploaded_photo_urls)} photo(s)!")
                        st.session_state.household_count += 1
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as err:
                        st.error(f"Failed to insert into Supabase: {err}")

# ==============================================================================
# TAB 2: COMMUNITY ANALYTICS & SOCIO-ECONOMIC INDICATORS
# ==============================================================================
with nav_tab2:
    if df_records.empty:
        st.info("ℹ️ No records found in Supabase yet. Fill out the survey form in Tab 1 to populate analytics.")
    else:
        st.subheader("Community Socio-Economic Profile")
        
        # Top Metrics
        tot_hh = len(df_records)
        tot_photos = sum([len(p) for p in df_records['photo_urls'] if isinstance(p, list)])
        elec_rate = (df_records['has_electricity'] == 'Yes').mean() * 100 if tot_hh > 0 else 0
        water_rate = (df_records['drinking_water_source'] == 'Tap water').mean() * 100 if tot_hh > 0 else 0
        toilet_rate = (df_records['toilet_access'] == 'Private toilet').mean() * 100 if tot_hh > 0 else 0

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Households Surveyed", tot_hh)
        m2.metric("Photos Uploaded", tot_photos)
        m3.metric("Electricity Access", f"{elec_rate:.1f}%")
        m4.metric("Piped Water Access", f"{water_rate:.1f}%")
        m5.metric("Private Sanitation", f"{toilet_rate:.1f}%")

        st.divider()

        ca1, ca2 = st.columns(2)
        with ca1:
            st.subheader("Monthly Household Income Distribution")
            inc_counts = df_records['monthly_income'].value_counts().reset_index()
            inc_counts.columns = ['Income Bracket', 'Households']
            fig_inc = px.bar(inc_counts, x='Income Bracket', y='Households', color='Households', color_continuous_scale='Blues')
            fig_inc.update_layout(xaxis_tickangle=-30)
            st.plotly_chart(fig_inc, use_container_width=True)

        with ca2:
            st.subheader("House Structural Types")
            house_counts = df_records['house_type'].value_counts().reset_index()
            house_counts.columns = ['House Type', 'Count']
            fig_house = px.pie(house_counts, names='House Type', values='Count', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_house, use_container_width=True)

        ca3, ca4 = st.columns(2)
        with ca3:
            st.subheader("Primary Occupations")
            occ_counts = df_records['primary_occupation'].value_counts().reset_index()
            occ_counts.columns = ['Occupation', 'Count']
            fig_occ = px.bar(occ_counts, x='Count', y='Occupation', orientation='h', color='Count', color_continuous_scale='Teal')
            st.plotly_chart(fig_occ, use_container_width=True)

        with ca4:
            st.subheader("Public Services Quality Ratings (1 to 5)")
            services = {
                'rating_education': 'Education',
                'rating_healthcare': 'Healthcare',
                'rating_transportation': 'Transport',
                'rating_banking': 'Banking',
                'rating_markets': 'Markets'
            }
            avg_ratings = []
            for col_name, srv_label in services.items():
                if col_name in df_records.columns:
                    val = pd.to_numeric(df_records[col_name], errors='coerce').mean()
                    avg_ratings.append({"Service": srv_label, "Avg Rating": round(val, 2)})
            df_srv = pd.DataFrame(avg_ratings)
            fig_srv = px.bar(df_srv, x='Service', y='Avg Rating', range_y=[0, 5], color='Avg Rating', color_continuous_scale='Viridis', text='Avg Rating')
            st.plotly_chart(fig_srv, use_container_width=True)

# ==============================================================================
# TAB 3: GEOSPATIAL / GIS MAPPING
# ==============================================================================
with nav_tab3:
    st.subheader("Geospatial Household Ground-Truth Map")
    st.caption("Households tagged with GPS coordinates appear as interactive pins with on-site details.")

    def parse_gps(notes):
        if not isinstance(notes, str):
            return None, None
        match = re.search(r'\[GPS:\s*([+-]?\d+\.?\d*),\s*([+-]?\d+\.?\d*)\]', notes)
        if match:
            return float(match.group(1)), float(match.group(2))
        return None, None

    if not df_records.empty:
        gps_coords = [parse_gps(n) for n in df_records['surveyor_notes']]
        valid_coords = [(lat, lon, df_records.iloc[i]) for i, (lat, lon) in enumerate(gps_coords) if lat is not None and lon is not None]

        if valid_coords:
            center_lat = sum([c[0] for c in valid_coords]) / len(valid_coords)
            center_lon = sum([c[1] for c in valid_coords]) / len(valid_coords)
            m = folium.Map(location=[center_lat, center_lon], zoom_start=14, tiles="CartoDB positron")

            for lat, lon, row in valid_coords:
                popup_html = f"""
                <div style="font-family: sans-serif; font-size: 12px; width: 200px;">
                    <b style="color: #2563eb;">{row['full_name']}</b><br>
                    <span>{row['locality']}</span><hr style="margin: 4px 0;">
                    <b>House:</b> {row['house_type']}<br>
                    <b>Income:</b> {row['monthly_income']}<br>
                    <b>Water:</b> {row['drinking_water_source']}<br>
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
            st.info("ℹ️ No GPS coordinates found in existing records. Enter GPS coordinates in the survey form to display map pins.")
    else:
        st.info("No records to map yet.")

# ==============================================================================
# TAB 4: PHOTO EVIDENCE GALLERY
# ==============================================================================
with nav_tab4:
    st.subheader("Household & Field Evidence Photos")
    st.caption("Photos saved in your Supabase Storage bucket (`survey-photos`).")

    if not df_records.empty:
        records_with_photos = df_records[df_records['photo_urls'].apply(lambda x: isinstance(x, list) and len(x) > 0)]
        if records_with_photos.empty:
            st.info("No photos uploaded yet.")
        else:
            for idx, row in records_with_photos.iterrows():
                with st.expander(f"📷 {row['full_name']} — {row['locality']} ({len(row['photo_urls'])} photos)", expanded=True):
                    cols = st.columns(min(len(row['photo_urls']), 4))
                    for i, p_url in enumerate(row['photo_urls']):
                        with cols[i % 4]:
                            st.image(p_url, caption=f"Photo {i+1}", use_container_width=True)
                    st.caption(f"**House Type:** {row['house_type']} | **Water Source:** {row['drinking_water_source']} | **Notes:** {row.get('surveyor_notes', 'None')}")
    else:
        st.info("No records found.")

# ==============================================================================
# TAB 5: SUBMISSIONS TABLE & EXPORT
# ==============================================================================
with nav_tab5:
    st.subheader("All Household Survey Records")
    if not df_records.empty:
        st.dataframe(df_records, use_container_width=True)
        csv_data = df_records.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download All Records as CSV",
            data=csv_data,
            file_name="household_survey_records.csv",
            mime="text/csv"
        )
    else:
        st.info("No records recorded yet.")
