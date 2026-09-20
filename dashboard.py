import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import urllib.request
import urllib.error
import json
import time
import re
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Socio-Economic Community Survey Portal",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
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
        margin-bottom: 1rem;
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
    .login-container {
        max-width: 440px;
        margin: 2rem auto;
        padding: 2rem;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 1rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08);
    }
</style>
""", unsafe_allow_html=True)

# --- Supabase Credentials ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL", "https://tsfzjhapftoacachqute.supabase.co"))
SUPABASE_KEY = st.secrets.get("SUPABASE_ANON_KEY", os.environ.get("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRzZnpqaGFwZnRvYWNhY2hxdXRlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk4OTE4NTQsImV4cCI6MjEwNTQ2Nzg1NH0.60yo8hh51yQvdoGfYdEy8PF0XVLUyePwfuuK-pndJ6o"))

# Service Key for admin user auto-confirmation (bypasses email confirmation requirement)
SERVICE_ROLE_KEY = st.secrets.get("SUPABASE_SERVICE_KEY", os.environ.get("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRzZnpqaGFwZnRvYWNhY2hxdXRlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4OTg5MTg1NCwiZXhwIjoyMTA1NDY3ODU0fQ.f33c7b4GnWDhZexB3lZiwmZvwTbX3hMkKrot6hZTrnc"))

# Session State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "household_count" not in st.session_state:
    st.session_state.household_count = 1

# ==============================================================================
# SUPABASE AUTH & API HELPERS
# ==============================================================================
def auto_confirm_user_by_email(email):
    """Helper to auto-confirm user email so no email verification link is required."""
    try:
        url = f"{SUPABASE_URL}/auth/v1/admin/users"
        headers = {"apikey": SERVICE_ROLE_KEY, "Authorization": f"Bearer {SERVICE_ROLE_KEY}"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            users_list = json.loads(resp.read().decode("utf-8")).get("users", [])
            for u in users_list:
                if u.get("email", "").lower() == email.strip().lower():
                    uid = u.get("id")
                    up_url = f"{SUPABASE_URL}/auth/v1/admin/users/{uid}"
                    up_headers = {
                        "apikey": SERVICE_ROLE_KEY,
                        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
                        "Content-Type": "application/json"
                    }
                    up_payload = json.dumps({"email_confirm": True}).encode("utf-8")
                    up_req = urllib.request.Request(up_url, data=up_payload, headers=up_headers, method="PUT")
                    with urllib.request.urlopen(up_req, timeout=8):
                        return True
    except Exception:
        pass
    return False

def supabase_sign_in(email, password):
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }
    payload = json.dumps({"email": email.strip(), "password": password.strip()}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return True, data.get("user", {}).get("email", email)
    except urllib.error.HTTPError as e:
        err_msg = "Invalid email or password"
        try:
            err_json = json.loads(e.read().decode("utf-8"))
            raw_err = err_json.get("error_description") or err_json.get("msg") or ""
            # If email is not confirmed, auto-confirm it and retry!
            if "not confirmed" in raw_err.lower():
                if auto_confirm_user_by_email(email):
                    # Retry login once confirmed
                    with urllib.request.urlopen(req, timeout=10) as retry_resp:
                        data = json.loads(retry_resp.read().decode("utf-8"))
                        return True, data.get("user", {}).get("email", email)
            err_msg = raw_err if raw_err else err_msg
        except Exception:
            pass
        return False, err_msg
    except Exception as e:
        return False, str(e)

def supabase_sign_up(email, password):
    # Use Admin API to create user with email_confirm=True directly
    admin_url = f"{SUPABASE_URL}/auth/v1/admin/users"
    admin_headers = {
        "apikey": SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    admin_payload = json.dumps({
        "email": email.strip(),
        "password": password.strip(),
        "email_confirm": True
    }).encode("utf-8")
    
    try:
        req = urllib.request.Request(admin_url, data=admin_payload, headers=admin_headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return True, "Surveyor account registered & verified! You can log in now."
    except urllib.error.HTTPError as e:
        # Fallback to standard signup if admin fails
        try:
            err_json = json.loads(e.read().decode("utf-8"))
            msg = err_json.get("msg") or err_json.get("message")
            if "already exists" in str(msg).lower() or "registered" in str(msg).lower():
                auto_confirm_user_by_email(email)
                return True, "Account already exists and is verified. Please sign in."
        except Exception:
            pass
            
    # Fallback standard signup
    url = f"{SUPABASE_URL}/auth/v1/signup"
    headers = {"apikey": SUPABASE_KEY, "Content-Type": "application/json"}
    payload = json.dumps({"email": email.strip(), "password": password.strip()}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            auto_confirm_user_by_email(email)
            return True, "Account registered! You can log in immediately."
    except urllib.error.HTTPError as e:
        err_msg = "Registration failed"
        try:
            err_json = json.loads(e.read().decode("utf-8"))
            err_msg = err_json.get("msg") or err_json.get("error_description") or err_msg
        except Exception:
            pass
        return False, err_msg
    except Exception as e:
        return False, str(e)

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
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                return f"{SUPABASE_URL}/storage/v1/object/public/survey-photos/{storage_path}"
    except Exception as e:
        st.warning(f"Photo upload note: {e}")
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
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def update_survey_record(record_id, updated_data):
    url = f"{SUPABASE_URL}/rest/v1/survey_responses?id=eq.{record_id}"
    headers = {
        "apikey": SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    data = json.dumps(updated_data).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status in [200, 204]

def delete_survey_record(record_id):
    url = f"{SUPABASE_URL}/rest/v1/survey_responses?id=eq.{record_id}"
    headers = {
        "apikey": SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}"
    }
    req = urllib.request.Request(url, headers=headers, method="DELETE")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status in [200, 204]

@st.cache_data(ttl=15)
def fetch_all_responses():
    url = f"{SUPABASE_URL}/rest/v1/survey_responses?select=*&order=created_at.desc"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            df = pd.DataFrame(data)
            # Detect source (On-Field vs Google Form)
            if not df.empty:
                def extract_source(row):
                    if "data_source" in row and pd.notna(row["data_source"]) and row["data_source"]:
                        return str(row["data_source"])
                    notes = str(row.get("surveyor_notes", ""))
                    if "[SOURCE: Google Form]" in notes or "Google Form" in notes:
                        return "Google Form"
                    return "On-Field"
                df["source_type"] = df.apply(extract_source, axis=1)
            return df
    except Exception as e:
        return pd.DataFrame()

# ==============================================================================
# AUTHENTICATION SCREEN (LOGIN PAGE)
# ==============================================================================
if not st.session_state.authenticated:
    st.markdown("<div style='text-align: center; margin-top: 2rem;'>", unsafe_allow_html=True)
    st.markdown("## 🔐 Socio-Economic Survey Portal Login")
    st.caption("Secure Surveyor Authentication via Supabase")
    st.markdown("</div>", unsafe_allow_html=True)

    col_l1, col_l2, col_l3 = st.columns([1, 1.4, 1])
    with col_l2:
        tab_login, tab_signup, tab_quick = st.tabs(["🔑 Sign In", "📝 Create Account", "⚡ Quick Access"])
        
        # --- TAB: SIGN IN ---
        with tab_login:
            st.write("")
            login_email = st.text_input("Email / Surveyor ID", placeholder="surveyor@example.com", key="login_email")
            login_pass = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")
            
            if st.button("Log In to Portal", type="primary", use_container_width=True):
                if not login_email or not login_pass:
                    st.error("Please enter both email and password.")
                else:
                    with st.spinner("Authenticating with Supabase..."):
                        success, res = supabase_sign_in(login_email, login_pass)
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.user_email = res
                            st.success("Authentication successful!")
                            st.rerun()
                        else:
                            st.error(f"Login failed: {res}")

        # --- TAB: SIGN UP ---
        with tab_signup:
            st.write("")
            reg_email = st.text_input("Surveyor Email", placeholder="new_surveyor@example.com", key="reg_email")
            reg_pass = st.text_input("Create Password", type="password", placeholder="Minimum 6 characters", key="reg_pass")
            reg_pass_conf = st.text_input("Confirm Password", type="password", key="reg_pass_conf")
            
            if st.button("Register New Surveyor", use_container_width=True):
                if not reg_email or not reg_pass:
                    st.error("Please fill all fields.")
                elif reg_pass != reg_pass_conf:
                    st.error("Passwords do not match.")
                elif len(reg_pass) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    with st.spinner("Creating account in Supabase..."):
                        success, msg = supabase_sign_up(reg_email, reg_pass)
                        if success:
                            st.success(msg)
                        else:
                            st.error(f"Registration note: {msg}")

        # --- TAB: QUICK ACCESS ---
        with tab_quick:
            st.write("")
            st.info("Direct access for authorized field enumerators or offline evaluation.")
            guest_name = st.text_input("Enumerator Name", value="Field Surveyor 1", key="guest_name")
            if st.button("Continue as Enumerator", type="secondary", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.user_email = f"{guest_name.strip()} (Enumerator)"
                st.rerun()

    st.stop()  # Stop execution here until logged in

# ==============================================================================
# LOGGED-IN PORTAL INTERFACE
# ==============================================================================

# --- Sidebar: User Info, Logout & Global Source Trigger ---
st.sidebar.markdown(f"**👤 Surveyor:** `{st.session_state.user_email}`")
if st.sidebar.button("🚪 Sign Out", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.user_email = ""
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("🎚️ Data Source View")

# TRIGGER BUTTON / SELECTOR for Google Form vs On-Field Data
data_source_trigger = st.sidebar.radio(
    "Select Source Filter:",
    ["🌐 All Data (Combined)", "📱 On-Field Data Only", "📋 Google Form Data Only"],
    index=0
)

# Fetch data from Supabase
df_raw = fetch_all_responses()

# Apply Trigger Button Filter
if not df_raw.empty and "source_type" in df_raw.columns:
    if data_source_trigger == "📱 On-Field Data Only":
        df_filtered = df_raw[df_raw["source_type"] == "On-Field"].copy()
    elif data_source_trigger == "📋 Google Form Data Only":
        df_filtered = df_raw[df_raw["source_type"] == "Google Form"].copy()
    else:
        df_filtered = df_raw.copy()
else:
    df_filtered = df_raw.copy()

# Header Display
col_head1, col_head2 = st.columns([3, 1.2])
with col_head1:
    st.markdown('<div class="main-title">🏡 Socio-Economic Community Assessment</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">Active Filter: <b>{data_source_trigger}</b> | Logged in as: {st.session_state.user_email}</div>', unsafe_allow_html=True)
with col_head2:
    st.write("")
    if st.button("🔄 Refresh Cloud Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- Main App Navigation Tabs ---
nav_tab1, nav_tab2, nav_tab3, nav_tab4, nav_tab5 = st.tabs([
    "📝 Fill Household Survey",
    "📊 Analytics & Indicators",
    "🗺️ Geospatial / GIS Mapping",
    "📸 Photo Evidence Gallery",
    "📋 Submissions Table & Export"
])

# ==============================================================================
# TAB 1: SURVEY ENTRY (ON-FIELD & GOOGLE FORM DATA CAPTURE)
# ==============================================================================
with nav_tab1:
    # Trigger / Toggle for Entry Mode
    entry_mode = st.radio(
        "Select Entry Mode:",
        ["📱 On-Field Door-to-Door Survey (with Camera Photos)", "📋 Enter / Import Google Form Data"],
        horizontal=True
    )
    
    if entry_mode == "📋 Enter / Import Google Form Data":
        st.info("📋 **Google Form Data Entry**: You can upload an exported Google Form responses CSV or manually submit responses collected from Google Forms.")
        
        uploaded_csv = st.file_uploader("📥 Upload Google Form Responses CSV File", type=["csv"])
        if uploaded_csv is not None:
            try:
                csv_df = pd.read_csv(uploaded_csv)
                st.write(f"Detected **{len(csv_df)}** rows in CSV:")
                st.dataframe(csv_df.head(3), use_container_width=True)
                
                if st.button(f"⬆️ Import & Sync {len(csv_df)} Google Form Responses to Supabase", type="primary"):
                    with st.spinner("Syncing Google Form records to Supabase..."):
                        success_count = 0
                        for _, row in csv_df.iterrows():
                            # Normalize fields from typical Google Form CSV columns
                            name_val = str(row.get("Name", row.get("full_name", row.get("Name *", "Google Form Respondent"))))
                            email_val = str(row.get("Email", row.get("email", "gform@survey.com")))
                            locality_val = str(row.get("Which area or locality do you belong to?", row.get("locality", "Not Specified")))
                            
                            g_record = {
                                "full_name": name_val,
                                "email": email_val,
                                "gender": str(row.get("Gender", "Prefer not to say")),
                                "age": int(pd.to_numeric(row.get("Age", 30), errors="coerce") or 30),
                                "locality": locality_val,
                                "household_members": str(row.get("How many members are there in your household?", "3 to 4")),
                                "highest_qualification": str(row.get("What is your highest educational qualification?", "Secondary")),
                                "members_studying": str(row.get("How many members of your household are currently studying?", "1")),
                                "distance_to_education": str(row.get("How far is the nearest educational institution?", "1 to 3 km")),
                                "education_difficulties": ["No major difficulty"],
                                "employment_status": str(row.get("What is your current employment status?", "Employed")),
                                "primary_occupation": str(row.get("What is your primary occupation?", "Private job")),
                                "earning_members": "1",
                                "monthly_income": str(row.get("What is your approximate monthly household income?", "20,000 to 30,000 INR")),
                                "house_type": str(row.get("What type of house do you live in?", "Concrete House / Brick House")),
                                "available_rooms": "2",
                                "has_electricity": "Yes",
                                "drinking_water_source": "Tap water",
                                "water_available_year_round": "Yes",
                                "toilet_access": "Private toilet",
                                "primary_cooking_fuel": "LPG",
                                "waste_disposal": "Municipal or local collection",
                                "has_internet": "Yes",
                                "internet_devices": ["Smartphone"],
                                "rating_education": 3,
                                "rating_healthcare": 3,
                                "rating_transportation": 3,
                                "rating_banking": 3,
                                "rating_markets": 3,
                                "biggest_problems": ["Waste management"],
                                "highest_priority_improvement": ["Roads and transport"],
                                "photo_urls": [],
                                "surveyor_notes": f"[SOURCE: Google Form] Imported from CSV ({uploaded_csv.name})"
                            }
                            try:
                                insert_survey_record(g_record)
                                success_count += 1
                            except Exception:
                                pass
                        st.success(f"✅ Successfully imported and uploaded {success_count} Google Form records to Supabase!")
                        st.cache_data.clear()
                        st.rerun()
            except Exception as e:
                st.error(f"Error reading CSV: {e}")

        st.markdown("---")
        st.subheader("Or Manually Enter a Single Google Form Response")

    # Survey Form (Common for On-Field or Single Google Form Entry)
    form_source_tag = "[SOURCE: Google Form]" if "Google Form" in entry_mode else "[SOURCE: On-Field]"
    
    with st.form(f"survey_form_{st.session_state.household_count}", clear_on_submit=True):
        st.caption(f"Entry Mode: **{entry_mode}** | Recording Household #{st.session_state.household_count}")
        
        # Section 1: Respondent Information
        st.markdown('<div class="section-header">Section 1: Respondent Information</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name *", placeholder="e.g. Ramesh Kumar")
            gender = st.radio("Gender *", ["Male", "Female", "Prefer not to say"], horizontal=True)
        with col2:
            email = st.text_input("Email Address *", placeholder="e.g. ramesh@example.com")
            age = st.number_input("Age (Years) *", min_value=1, max_value=120, value=30)
            
        # Section 2: Location and Household
        st.markdown('<div class="section-header">Section 2: Location & Household</div>', unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        with col3:
            locality = st.text_input("Which area or locality do you belong to? *", placeholder="e.g. Ward 4, Azad Nagar")
            gps_tag = st.text_input("GPS Coordinates (e.g. 19.0760, 72.8777)")
        with col4:
            household_members = st.radio("How many members are there in your household? *", 
                                         ["1 to 2", "3 to 4", "5 to 6", "7 to 8", "More than 8"], horizontal=True)

        # Section 3: Education
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

        # Section 4: Employment & Income
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

        # Section 5: Housing, Water & Basic Amenities
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

        # Section 6: Digital Access
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

        # Section 7: Essential Services Rating & Local Problems
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

        # Section 8: Photo Evidence (Only if On-Field)
        uploaded_photo_urls = []
        if "On-Field" in entry_mode:
            st.markdown('<div class="section-header">Section 8: Photo Evidence & Field Notes</div>', unsafe_allow_html=True)
            st.caption("Capture photos using smartphone camera or upload gallery files to Supabase Storage (`survey-photos`).")
            cam_photo = st.camera_input("📷 Take Photo with Smartphone Camera")
            file_photos = st.file_uploader("🖼️ Or Upload Existing Photos from Device", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
        else:
            cam_photo = None
            file_photos = None

        surveyor_notes = st.text_area("Observations / Notes (Optional)", placeholder="e.g. Additional remarks or notes...")

        st.markdown("---")
        submitted = st.form_submit_button(f"💾 Save Record ({entry_mode.split()[0]}) & Next", type="primary", use_container_width=True)

        if submitted:
            if not full_name.strip():
                st.error("⚠️ Please enter the respondent's full name.")
            elif not locality.strip():
                st.error("⚠️ Please enter the locality/area name.")
            else:
                with st.spinner("Saving record to Supabase..."):
                    if cam_photo is not None:
                        c_url = upload_photo_to_supabase(cam_photo.getvalue(), f"cam_h{st.session_state.household_count}.jpg")
                        if c_url:
                            uploaded_photo_urls.append(c_url)
                            
                    if file_photos:
                        for f in file_photos:
                            f_url = upload_photo_to_supabase(f.getvalue(), f.name)
                            if f_url:
                                uploaded_photo_urls.append(f_url)

                    # Notes containing Source Tag and GPS
                    final_notes = f"{form_source_tag} "
                    if gps_tag.strip():
                        final_notes += f"[GPS: {gps_tag.strip()}] "
                    if surveyor_notes and surveyor_notes.strip():
                        final_notes += surveyor_notes.strip()

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
                        "surveyor_notes": final_notes.strip() if final_notes.strip() else None
                    }

                    try:
                        insert_survey_record(record)
                        st.success(f"🎉 Record for {full_name} ({entry_mode.split()[0]}) successfully saved to Supabase!")
                        st.session_state.household_count += 1
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as err:
                        st.error(f"Failed to insert into Supabase: {err}")

# ==============================================================================
# TAB 2: ANALYTICS & SOCIO-ECONOMIC INDICATORS
# ==============================================================================
with nav_tab2:
    st.subheader(f"📊 Socio-Economic Indicators ({data_source_trigger})")
    
    if df_filtered.empty:
        st.info("ℹ️ No records found for the selected filter. Enter records in Tab 1 to populate analytics.")
    else:
        tot_hh = len(df_filtered)
        tot_photos = sum([len(p) for p in df_filtered['photo_urls'] if isinstance(p, list)])
        elec_rate = (df_filtered['has_electricity'] == 'Yes').mean() * 100 if tot_hh > 0 else 0
        water_rate = (df_filtered['drinking_water_source'] == 'Tap water').mean() * 100 if tot_hh > 0 else 0
        toilet_rate = (df_filtered['toilet_access'] == 'Private toilet').mean() * 100 if tot_hh > 0 else 0

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Responses in View", tot_hh)
        m2.metric("Photos Uploaded", tot_photos)
        m3.metric("Electricity Access", f"{elec_rate:.1f}%")
        m4.metric("Piped Water Access", f"{water_rate:.1f}%")
        m5.metric("Private Sanitation", f"{toilet_rate:.1f}%")

        st.divider()

        ca1, ca2 = st.columns(2)
        with ca1:
            st.subheader("Monthly Household Income Distribution")
            inc_counts = df_filtered['monthly_income'].value_counts().reset_index()
            inc_counts.columns = ['Income Bracket', 'Households']
            fig_inc = px.bar(inc_counts, x='Income Bracket', y='Households', color='Households', color_continuous_scale='Blues')
            fig_inc.update_layout(xaxis_tickangle=-30)
            st.plotly_chart(fig_inc, use_container_width=True)

        with ca2:
            st.subheader("House Structural Types")
            house_counts = df_filtered['house_type'].value_counts().reset_index()
            house_counts.columns = ['House Type', 'Count']
            fig_house = px.pie(house_counts, names='House Type', values='Count', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_house, use_container_width=True)

        ca3, ca4 = st.columns(2)
        with ca3:
            st.subheader("Primary Occupations")
            occ_counts = df_filtered['primary_occupation'].value_counts().reset_index()
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
                if col_name in df_filtered.columns:
                    val = pd.to_numeric(df_filtered[col_name], errors='coerce').mean()
                    avg_ratings.append({"Service": srv_label, "Avg Rating": round(val, 2)})
            df_srv = pd.DataFrame(avg_ratings)
            fig_srv = px.bar(df_srv, x='Service', y='Avg Rating', range_y=[0, 5], color='Avg Rating', color_continuous_scale='Viridis', text='Avg Rating')
            st.plotly_chart(fig_srv, use_container_width=True)

# ==============================================================================
# TAB 3: GEOSPATIAL / GIS MAPPING
# ==============================================================================
with nav_tab3:
    st.subheader(f"🗺️ Geospatial Household Ground-Truth Map ({data_source_trigger})")
    st.caption("Pins show GPS-tagged locations with household profiles.")

    def parse_gps(notes):
        if not isinstance(notes, str):
            return None, None
        match = re.search(r'\[GPS:\s*([+-]?\d+\.?\d*),\s*([+-]?\d+\.?\d*)\]', notes)
        if match:
            return float(match.group(1)), float(match.group(2))
        return None, None

    if not df_filtered.empty:
        gps_coords = [parse_gps(n) for n in df_filtered['surveyor_notes']]
        valid_coords = [(lat, lon, df_filtered.iloc[i]) for i, (lat, lon) in enumerate(gps_coords) if lat is not None and lon is not None]

        if valid_coords:
            center_lat = sum([c[0] for c in valid_coords]) / len(valid_coords)
            center_lon = sum([c[1] for c in valid_coords]) / len(valid_coords)
            m = folium.Map(location=[center_lat, center_lon], zoom_start=14, tiles="CartoDB positron")

            for lat, lon, row in valid_coords:
                is_gform = row.get("source_type") == "Google Form"
                marker_color = "green" if is_gform else "blue"
                popup_html = f"""
                <div style="font-family: sans-serif; font-size: 12px; width: 200px;">
                    <b style="color: #2563eb;">{row['full_name']}</b> ({row.get('source_type', 'On-Field')})<br>
                    <span>{row['locality']}</span><hr style="margin: 4px 0;">
                    <b>House:</b> {row['house_type']}<br>
                    <b>Income:</b> {row['monthly_income']}<br>
                    <b>Water:</b> {row['drinking_water_source']}<br>
                </div>
                """
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{row['full_name']} ({row.get('source_type', 'On-Field')})",
                    icon=folium.Icon(color=marker_color, icon="home", prefix="fa")
                ).add_to(m)

            st_folium(m, width="100%", height=500)
        else:
            st.info("ℹ️ No GPS coordinates found in the filtered records. Enter GPS coordinates during survey entry to display map pins.")
    else:
        st.info("No records to display on map.")

# ==============================================================================
# TAB 4: PHOTO EVIDENCE GALLERY
# ==============================================================================
with nav_tab4:
    st.subheader(f"📸 Field Evidence Photo Gallery ({data_source_trigger})")
    st.caption("Photos retrieved live from your Supabase Storage bucket (`survey-photos`).")

    if not df_filtered.empty:
        records_with_photos = df_filtered[df_filtered['photo_urls'].apply(lambda x: isinstance(x, list) and len(x) > 0)]
        if records_with_photos.empty:
            st.info("No photos found in the filtered records.")
        else:
            for idx, row in records_with_photos.iterrows():
                with st.expander(f"📷 {row['full_name']} — {row['locality']} ({len(row['photo_urls'])} photos | {row.get('source_type', 'On-Field')})", expanded=True):
                    cols = st.columns(min(len(row['photo_urls']), 4))
                    for i, p_url in enumerate(row['photo_urls']):
                        with cols[i % 4]:
                            st.image(p_url, caption=f"Photo {i+1}", use_container_width=True)
                    st.caption(f"**House Type:** {row['house_type']} | **Water Source:** {row['drinking_water_source']} | **Notes:** {row.get('surveyor_notes', 'None')}")
    else:
        st.info("No records available.")

# ==============================================================================
# TAB 5: SUBMISSIONS TABLE & EXPORT
# ==============================================================================
with nav_tab5:
    st.subheader(f"📋 Submissions Table & Management ({data_source_trigger})")
    
    if not df_filtered.empty:
        # Table Display
        st.dataframe(df_filtered, use_container_width=True)
        
        # CSV Export
        col_dl1, col_dl2 = st.columns([1.5, 3])
        with col_dl1:
            csv_data = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 Download ({data_source_trigger}) as CSV",
                data=csv_data,
                file_name=f"survey_data_{data_source_trigger.split()[1].lower()}.csv",
                mime="text/csv",
                use_container_width=True
            )

        st.markdown("---")
        st.markdown("### ✏️ Edit or 🗑️ Delete a Survey Record")
        st.caption("Select any household record below to edit its answers or permanently delete it from Supabase.")

        # Build dropdown options
        record_map = {f"{r['full_name']} — {r['locality']} (ID: {str(r['id'])[:8]}...)": r['id'] for _, r in df_filtered.iterrows()}
        selected_label = st.selectbox("Choose Household to Edit or Delete:", list(record_map.keys()))
        selected_id = record_map[selected_label]
        target_row = df_filtered[df_filtered['id'] == selected_id].iloc[0]

        edit_col, del_col = st.columns([2.5, 1])

        with edit_col:
            with st.expander(f"✏️ Edit Details for **{target_row['full_name']}**", expanded=True):
                with st.form(f"edit_form_{selected_id}"):
                    e_c1, e_c2 = st.columns(2)
                    with e_c1:
                        new_name = st.text_input("Full Name", value=str(target_row.get('full_name', '')))
                        curr_g = target_row.get('gender', 'Male')
                        new_gender = st.selectbox("Gender", ["Male", "Female", "Prefer not to say"], 
                                                 index=["Male", "Female", "Prefer not to say"].index(curr_g) if curr_g in ["Male", "Female", "Prefer not to say"] else 0)
                        new_locality = st.text_input("Locality / Area", value=str(target_row.get('locality', '')))
                        curr_hh = target_row.get('household_members', '3 to 4')
                        hh_opts = ["1 to 2", "3 to 4", "5 to 6", "7 to 8", "More than 8"]
                        new_hh_members = st.selectbox("Household Members", hh_opts,
                                                     index=hh_opts.index(curr_hh) if curr_hh in hh_opts else 1)
                        new_occupation = st.text_input("Primary Occupation", value=str(target_row.get('primary_occupation', '')))
                        curr_inc = target_row.get('monthly_income')
                        inc_opts = ["Below 10,000 INR", "10,000 to 20,000 INR", "20,000 to 30,000 INR", "30,000 to 50,000 INR", "50,000 to 75,000 INR", "Above 75,000 INR", "Prefer not to say"]
                        new_income = st.selectbox("Monthly Income", inc_opts,
                                                 index=inc_opts.index(curr_inc) if curr_inc in inc_opts else 2)
                    with e_c2:
                        new_email = st.text_input("Email", value=str(target_row.get('email', '')))
                        new_age = st.number_input("Age", min_value=1, max_value=120, value=int(target_row.get('age', 30)))
                        new_house_type = st.text_input("House Type", value=str(target_row.get('house_type', '')))
                        new_water = st.text_input("Drinking Water Source", value=str(target_row.get('drinking_water_source', '')))
                        new_electricity = st.selectbox("Electricity Available?", ["Yes", "No"], index=0 if target_row.get('has_electricity') == 'Yes' else 1)
                        curr_toilet = target_row.get('toilet_access')
                        toilet_opts = ["Private toilet", "Shared toilet", "No toilet"]
                        new_toilet = st.selectbox("Toilet Access", toilet_opts,
                                                 index=toilet_opts.index(curr_toilet) if curr_toilet in toilet_opts else 0)

                    new_notes = st.text_area("Surveyor Notes", value=str(target_row.get('surveyor_notes', '')))
                    
                    save_edit = st.form_submit_button("💾 Save Changes to Record", type="primary", use_container_width=True)
                    if save_edit:
                        updated_payload = {
                            "full_name": new_name.strip(),
                            "email": new_email.strip(),
                            "gender": new_gender,
                            "age": int(new_age),
                            "locality": new_locality.strip(),
                            "household_members": new_hh_members,
                            "primary_occupation": new_occupation.strip(),
                            "monthly_income": new_income,
                            "house_type": new_house_type.strip(),
                            "drinking_water_source": new_water.strip(),
                            "has_electricity": new_electricity,
                            "toilet_access": new_toilet,
                            "surveyor_notes": new_notes.strip() if new_notes.strip() else None
                        }
                        with st.spinner("Updating record in Supabase..."):
                            if update_survey_record(selected_id, updated_payload):
                                st.success(f"✅ Record for {new_name} updated successfully in Supabase!")
                                st.cache_data.clear()
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Failed to update record in Supabase.")

        with del_col:
            with st.expander("🗑️ Delete Record", expanded=True):
                st.warning(f"Permanently delete survey for **{target_row['full_name']}**?")
                confirm_del = st.checkbox("I confirm permanent deletion", key=f"conf_del_{selected_id}")
                if st.button("🚨 Delete Record", type="primary", use_container_width=True, disabled=not confirm_del):
                    with st.spinner("Deleting record from Supabase..."):
                        if delete_survey_record(selected_id):
                            st.success("🗑️ Record permanently deleted from Supabase!")
                            st.cache_data.clear()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Failed to delete record from Supabase.")
    else:
        st.info("No records to display or manage.")
