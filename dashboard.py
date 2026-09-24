import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
try:
    from folium.plugins import LocateControl, Fullscreen
except Exception:
    LocateControl = None
    Fullscreen = None
import streamlit.components.v1 as components
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
    initial_sidebar_state="auto"
)

# Universal Responsive Design (Desktops, Laptops, Tablets & Phones)
st.markdown("""
<style>
    /* Base Responsive Typography & Inputs */
    html, body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    input, select, textarea, .stSelectbox, .stTextInput, .stNumberInput {
        font-size: 15px !important;
    }

    /* Common Button Styling */
    button[kind="primary"], button[kind="secondary"], .stButton > button {
        min-height: 44px !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.15s ease-in-out;
    }

    /* Submit Button */
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 3px 10px rgba(16, 185, 129, 0.25) !important;
        font-size: 15px !important;
        font-weight: 700 !important;
    }

    /* Tab Pill Active Styles */
    div[aria-selected="true"] {
        background-color: #eff6ff !important;
        border-color: #3b82f6 !important;
        color: #1d4ed8 !important;
        font-weight: 700 !important;
    }

    /* Streamlit Header Clearance Fix */
    header[data-testid="stHeader"] {
        background-color: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(8px) !important;
        z-index: 99 !important;
    }

    /* Base Container Clearance */
    .block-container {
        padding-top: 4.75rem !important;
    }

    /* =======================================================
       DESKTOPS & LAPTOPS (>= 1024px)
       ======================================================= */
    @media (min-width: 1024px) {
        .block-container {
            max-width: 1200px !important;
            margin: 0 auto !important;
            padding-top: 4.75rem !important;
            padding-bottom: 3.5rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        .main-title {
            font-size: 1.85rem !important;
            font-weight: 800;
            color: #0f172a;
            margin-top: 0.5rem !important;
            margin-bottom: 0.25rem;
            line-height: 1.3 !important;
        }
        .sub-title {
            font-size: 0.95rem !important;
            color: #64748b;
            margin-bottom: 1.25rem;
        }
        div[data-baseweb="tab-list"] {
            display: flex !important;
            gap: 0.5rem !important;
            border-bottom: 2px solid #e2e8f0 !important;
            padding-bottom: 0.25rem !important;
        }
        div[data-baseweb="tab"] {
            font-size: 0.9rem !important;
            padding: 0.55rem 1.1rem !important;
            border-radius: 8px 8px 0 0 !important;
            border: 1px solid #e2e8f0 !important;
            border-bottom: none !important;
            background-color: #f8fafc !important;
        }
    }

    /* =======================================================
       TABLETS (768px to 1023px)
       ======================================================= */
    @media (min-width: 768px) and (max-width: 1023px) {
        .block-container {
            max-width: 95% !important;
            margin: 0 auto !important;
            padding-top: 4.25rem !important;
            padding-bottom: 3rem !important;
            padding-left: 1.25rem !important;
            padding-right: 1.25rem !important;
        }
        .main-title {
            font-size: 1.55rem !important;
            font-weight: 800;
            margin-top: 0.4rem !important;
            line-height: 1.3 !important;
        }
        .sub-title {
            font-size: 0.9rem !important;
        }
        div[data-baseweb="tab-list"] {
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
            gap: 0.4rem !important;
            padding-bottom: 0.35rem !important;
            border-bottom: 1.5px solid #e2e8f0 !important;
        }
        div[data-baseweb="tab"] {
            font-size: 0.85rem !important;
            padding: 0.5rem 0.85rem !important;
            white-space: nowrap !important;
            border-radius: 8px !important;
            border: 1px solid #e2e8f0 !important;
            background-color: #f8fafc !important;
        }
    }

    /* =======================================================
       MOBILE PHONES (< 768px)
       ======================================================= */
    @media (max-width: 767px) {
        .block-container {
            max-width: 100% !important;
            padding-top: 3.75rem !important;
            padding-bottom: 4rem !important;
            padding-left: 0.65rem !important;
            padding-right: 0.65rem !important;
        }
        .main-title {
            font-size: 1.25rem !important;
            margin-top: 0.35rem !important;
            line-height: 1.3;
        }
        .sub-title {
            font-size: 0.8rem !important;
            margin-bottom: 0.75rem;
        }
        input, select, textarea, .stSelectbox, .stTextInput, .stNumberInput {
            font-size: 16px !important; /* Prevents auto-zoom on mobile */
        }
        button[kind="primary"], button[kind="secondary"], .stButton > button {
            min-height: 48px !important;
            font-size: 15px !important;
        }
        div[data-baseweb="tab-list"] {
            gap: 0.3rem !important;
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
            -webkit-overflow-scrolling: touch !important;
            padding-bottom: 0.4rem !important;
            border-bottom: 1.5px solid #e2e8f0 !important;
        }
        div[data-baseweb="tab"] {
            font-size: 0.8rem !important;
            padding: 0.45rem 0.65rem !important;
            white-space: nowrap !important;
            border-radius: 8px !important;
            background-color: #f8fafc !important;
            border: 1px solid #e2e8f0 !important;
        }
        .stMetric {
            background: #f8fafc;
            padding: 0.5rem;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            margin-bottom: 0.4rem;
        }
        div[data-testid="stForm"] {
            padding: 0.65rem !important;
        }
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
if "active_draft_id" not in st.session_state:
    st.session_state.active_draft_id = None
if "draft_data" not in st.session_state:
    st.session_state.draft_data = {}
if "form_render_id" not in st.session_state:
    st.session_state.form_render_id = 0

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

                def extract_draft_status(row):
                    notes = str(row.get("surveyor_notes", ""))
                    name = str(row.get("full_name", ""))
                    return "[STATUS: DRAFT]" in notes or name.startswith("[DRAFT]")

                df["source_type"] = df.apply(extract_source, axis=1)
                df["is_draft"] = df.apply(extract_draft_status, axis=1)

                # Standardize column naming: primary_occupation -> household_main_occupation
                if "primary_occupation" in df.columns:
                    df = df.rename(columns={
                        "primary_occupation": "household_main_occupation",
                        "primary_occupation_other": "household_main_occupation_other"
                    })
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

# Separate drafts from finalized responses
if not df_raw.empty and "is_draft" in df_raw.columns:
    df_drafts = df_raw[df_raw["is_draft"] == True].copy()
    df_completed = df_raw[df_raw["is_draft"] == False].copy()
else:
    df_drafts = pd.DataFrame()
    df_completed = df_raw.copy()

# Apply Trigger Button Filter on completed responses (so incomplete drafts don't skew analytics)
if not df_completed.empty and "source_type" in df_completed.columns:
    if data_source_trigger == "📱 On-Field Data Only":
        df_filtered = df_completed[df_completed["source_type"] == "On-Field"].copy()
    elif data_source_trigger == "📋 Google Form Data Only":
        df_filtered = df_completed[df_completed["source_type"] == "Google Form"].copy()
    else:
        df_filtered = df_completed.copy()
else:
    df_filtered = df_completed.copy()

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

# Helpers for Safe Select & Multiselect Defaults
def safe_index(options_list, val, default=0):
    if val in options_list:
        return options_list.index(val)
    return default

def safe_multiselect(options_list, values, default=None):
    if default is None:
        default = []
    if isinstance(values, list):
        valid = [v for v in values if v in options_list]
        return valid if valid else default
    return default

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
                                "primary_occupation": str(row.get("What is the household's main occupation?", row.get("What is your primary occupation?", "Private job"))),
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
    curr_draft = st.session_state.get("draft_data", {})

    # Active Draft Resumption Notice Banner
    if st.session_state.active_draft_id:
        draft_display = curr_draft.get("full_name", "Household Survey").replace("[DRAFT] ", "")
        st.info(f"✏️ **Currently Resuming Draft**: `{draft_display}`. You can update any answers, click **'💾 Save & Fill Later'** to save progress, or click **'🚀 Submit Complete Survey & Next'** to finalize.")
        if st.button("❌ Exit Draft & Start Fresh Survey", key="btn_exit_draft"):
            st.session_state.active_draft_id = None
            st.session_state.draft_data = {}
            st.session_state.form_render_id += 1
            st.rerun()

    # Cloud Saved Drafts Selector & Manager
    num_drafts = len(df_drafts)
    with st.expander(f"📂 Saved Drafts / Fill Later ({num_drafts} saved in Cloud)", expanded=(num_drafts > 0 and not st.session_state.active_draft_id)):
        if df_drafts.empty:
            st.info("💡 You currently have no saved drafts. While filling the survey below, you can click **'💾 Save & Fill Later'** at the bottom anytime to pause and resume later from any phone, tablet, or laptop.")
        else:
            st.write("Select an unfinished survey from the cloud to continue filling it:")
            draft_options = {}
            for _, d_row in df_drafts.iterrows():
                d_id = str(d_row["id"])
                d_name = str(d_row.get("full_name", "")).replace("[DRAFT] ", "").strip() or "Unnamed Household"
                d_loc = str(d_row.get("locality", "Unknown Locality")).replace("Locality Pending", "Locality Pending")
                d_time = str(d_row.get("created_at", ""))[:16].replace("T", " ")
                label = f"📝 {d_name} — {d_loc} ({d_time})"
                draft_options[label] = d_id
            
            chosen_draft_label = st.selectbox("Select saved draft to resume:", list(draft_options.keys()), key="sel_draft_pick")
            chosen_draft_id = draft_options[chosen_draft_label]
            
            cd_col1, cd_col2 = st.columns([1.6, 1])
            with cd_col1:
                if st.button("📥 Load & Continue This Survey", type="primary", use_container_width=True, key="btn_load_saved_draft"):
                    target_row = df_drafts[df_drafts["id"] == chosen_draft_id].iloc[0]
                    notes_str = str(target_row.get("surveyor_notes", ""))
                    parsed_payload = {}
                    if "[DRAFT_RAW:" in notes_str:
                        try:
                            raw_match = re.search(r'\[DRAFT_RAW:\s*({.*?})\s*\]', notes_str, re.DOTALL)
                            if raw_match:
                                parsed_payload = json.loads(raw_match.group(1))
                        except Exception:
                            pass
                    if not parsed_payload:
                        parsed_payload = target_row.to_dict()
                    
                    st.session_state.active_draft_id = chosen_draft_id
                    st.session_state.draft_data = parsed_payload
                    st.session_state.form_render_id += 1
                    st.success(f"Loaded draft! Scroll down to continue.")
                    st.rerun()
            with cd_col2:
                if st.button("🗑️ Delete Draft", use_container_width=True, key="btn_delete_saved_draft"):
                    if delete_survey_record(chosen_draft_id):
                        if st.session_state.active_draft_id == chosen_draft_id:
                            st.session_state.active_draft_id = None
                            st.session_state.draft_data = {}
                            st.session_state.form_render_id += 1
                        st.success("Draft deleted from Supabase!")
                        st.cache_data.clear()
                        st.rerun()

    # Pre-calculated default values from loaded draft
    val_name = str(curr_draft.get("full_name", "")).replace("[DRAFT] ", "").replace(" (Locality Pending)", "")
    val_gender = str(curr_draft.get("gender", "Male"))
    val_email = str(curr_draft.get("email", "")).replace("draft@survey.local", "")
    val_age = int(curr_draft.get("age", 30)) if str(curr_draft.get("age", "")).isdigit() else 30
    val_locality = str(curr_draft.get("locality", "")).replace("Locality Pending", "")
    val_gps = str(curr_draft.get("gps_tag", ""))
    val_hh_members = str(curr_draft.get("household_members", "3 to 4"))
    val_qualification = str(curr_draft.get("highest_qualification", "Undergraduate"))
    val_qual_other = str(curr_draft.get("highest_qualification_other", ""))
    val_members_studying = str(curr_draft.get("members_studying", "1"))
    val_distance_edu = str(curr_draft.get("distance_to_education", "1 to 3 km"))
    val_edu_diff = curr_draft.get("education_difficulties", ["No major difficulty"])
    val_edu_diff_other = str(curr_draft.get("education_difficulties_other", ""))
    val_emp_status = str(curr_draft.get("employment_status", "Employed"))
    val_emp_status_other = str(curr_draft.get("employment_status_other", ""))
    val_occupation = str(curr_draft.get("primary_occupation", "Private job"))
    val_occupation_other = str(curr_draft.get("primary_occupation_other", ""))
    val_earning_members = str(curr_draft.get("earning_members", "1"))
    val_income = str(curr_draft.get("monthly_income", "20,000 to 30,000 INR"))
    val_house_type = str(curr_draft.get("house_type", "Concrete House / Brick House"))
    val_house_type_other = str(curr_draft.get("house_type_other", ""))
    val_rooms = str(curr_draft.get("available_rooms", "2"))
    val_elec = str(curr_draft.get("has_electricity", "Yes"))
    val_water = str(curr_draft.get("drinking_water_source", "Tap water"))
    val_water_other = str(curr_draft.get("drinking_water_source_other", ""))
    val_water_year = str(curr_draft.get("water_available_year_round", "Yes"))
    val_toilet = str(curr_draft.get("toilet_access", "Private toilet"))
    val_fuel = str(curr_draft.get("primary_cooking_fuel", "LPG"))
    val_fuel_other = str(curr_draft.get("primary_cooking_fuel_other", ""))
    val_waste = str(curr_draft.get("waste_disposal", "Municipal or local collection"))
    val_waste_other = str(curr_draft.get("waste_disposal_other", ""))
    val_internet = str(curr_draft.get("has_internet", "Yes"))
    val_devices = curr_draft.get("internet_devices", ["Smartphone"])
    val_devices_other = str(curr_draft.get("internet_devices_other", ""))
    val_r_edu = int(curr_draft.get("rating_education", 3))
    val_r_health = int(curr_draft.get("rating_healthcare", 3))
    val_r_trans = int(curr_draft.get("rating_transportation", 3))
    val_r_bank = int(curr_draft.get("rating_banking", 3))
    val_r_market = int(curr_draft.get("rating_markets", 3))
    val_problems = curr_draft.get("biggest_problems", ["Waste management"])
    val_problems_other = str(curr_draft.get("biggest_problems_other", ""))
    val_priority = curr_draft.get("highest_priority_improvement", ["Roads and transport"])
    val_priority_other = str(curr_draft.get("highest_priority_improvement_other", ""))
    val_notes = str(curr_draft.get("raw_notes", curr_draft.get("surveyor_notes", "")))
    saved_photos = curr_draft.get("photo_urls", [])

    with st.form(f"survey_form_{st.session_state.household_count}_{st.session_state.form_render_id}", clear_on_submit=False):
        status_tag = f"Draft Household #{st.session_state.household_count}" if not st.session_state.active_draft_id else "Resuming Saved Survey"
        st.caption(f"Entry Mode: **{entry_mode}** | {status_tag}")
        
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name *", value=val_name, placeholder="e.g. Ramesh Kumar")
            g_opts = ["Male", "Female", "Prefer not to say"]
            gender = st.radio("Gender *", g_opts, index=safe_index(g_opts, val_gender), horizontal=True)
        with col2:
            email = st.text_input("Email Address", value=val_email, placeholder="e.g. ramesh@example.com (optional for draft)")
            age = st.number_input("Age (Years) *", min_value=1, max_value=120, value=val_age)
            
        st.divider()
        col3, col4 = st.columns(2)
        with col3:
            locality = st.text_input("Which area or locality do you belong to? *", value=val_locality, placeholder="e.g. Ward 4, Azad Nagar")
            
            # Direct Phone GPS Location Detection Widget
            gps_detect_html = """
            <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:8px; padding:8px 12px; margin-top:6px; margin-bottom:4px; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;">
                <button type="button" onclick="detectPhoneGPS()" style="background:#059669; color:#fff; border:none; border-radius:6px; padding:7px 12px; font-size:13px; font-weight:600; cursor:pointer; display:inline-flex; align-items:center; gap:5px;">
                    📱 Auto-Detect Phone Location (GPS)
                </button>
                <div id="gps-status" style="margin-top:6px; font-size:12px; color:#1e293b; line-height:1.4;">
                    <span style="color:#64748b;">Tap above to auto-detect high-accuracy GPS coordinates from your phone.</span>
                </div>
            </div>
            <script>
            function detectPhoneGPS() {
                var statusEl = document.getElementById('gps-status');
                if (!navigator.geolocation) {
                    statusEl.innerHTML = '<span style="color:#b91c1c;">❌ Geolocation not supported by your browser. Enter coordinates manually below.</span>';
                    return;
                }
                statusEl.innerHTML = '<span style="color:#2563eb;">📡 Accessing device GPS sensors... Please allow location access if prompted.</span>';
                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        var lat = pos.coords.latitude.toFixed(6);
                        var lon = pos.coords.longitude.toFixed(6);
                        var acc = Math.round(pos.coords.accuracy);
                        var coords = lat + ", " + lon;
                        if (navigator.clipboard && navigator.clipboard.writeText) {
                            navigator.clipboard.writeText(coords);
                        }
                        try {
                            var inputs = window.parent.document.querySelectorAll('input');
                            for (var i = 0; i < inputs.length; i++) {
                                var aria = (inputs[i].getAttribute('aria-label') || '').toLowerCase();
                                var ph = (inputs[i].getAttribute('placeholder') || '').toLowerCase();
                                if (aria.includes('gps') || ph.includes('19.0760')) {
                                    inputs[i].value = coords;
                                    inputs[i].dispatchEvent(new Event('input', { bubbles: true }));
                                    inputs[i].dispatchEvent(new Event('change', { bubbles: true }));
                                }
                            }
                        } catch(e) {}
                        statusEl.innerHTML = '✅ <b>Captured:</b> <span style="background:#fff; border:1px solid #cbd5e1; border-radius:4px; padding:2px 6px; font-family:monospace; font-weight:700;">' + coords + '</span> <span style="color:#059669; font-weight:600;">(±' + acc + 'm accuracy)</span><br><span style="color:#15803d; font-size:11px;">📋 Auto-copied to clipboard! Auto-filled or paste into the GPS field below.</span>';
                    },
                    function(err) {
                        var msg = err.message || 'Unable to retrieve location';
                        if (err.code === 1) msg = 'Location permission denied by browser. Please enable location permission in browser settings.';
                        statusEl.innerHTML = '<span style="color:#b91c1c;">⚠️ ' + msg + '</span>';
                    },
                    { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 }
                );
            }
            </script>
            """
            components.html(gps_detect_html, height=105)
            gps_tag = st.text_input("GPS Coordinates (Latitude, Longitude)", value=val_gps, placeholder="e.g. 19.0760, 72.8777", help="Format: Latitude, Longitude. Auto-detect using phone GPS above or type/paste manually.")
        with col4:
            hh_opts = ["1 to 2", "3 to 4", "5 to 6", "7 to 8", "More than 8"]
            household_members = st.radio("How many members are there in your household? *", 
                                         hh_opts, index=safe_index(hh_opts, val_hh_members, 1), horizontal=True)

        st.divider()
        q_opts = ["Undergraduate", "Higher Secondary", "Secondary", "Primary", "Diploma", "Postgraduate", "No formal education", "Other"]
        highest_qualification = st.selectbox(
            "What is your highest educational qualification? *",
            q_opts, index=safe_index(q_opts, val_qualification)
        )
        highest_qualification_other = ""
        if highest_qualification == "Other":
            highest_qualification_other = st.text_input("Specify other qualification:", value=val_qual_other)

        col5, col6 = st.columns(2)
        with col5:
            stud_opts = ["0", "1", "2", "3", "4+"]
            members_studying = st.radio("How many members are currently studying? *", stud_opts, index=safe_index(stud_opts, val_members_studying, 1), horizontal=True)
        with col6:
            dist_opts = ["Less than 1 km", "1 to 3 km", "3 to 5 km", "More than 5 km"]
            distance_to_education = st.radio("Distance to nearest educational institution? *", 
                                            dist_opts, index=safe_index(dist_opts, val_distance_edu, 1), horizontal=True)

        diff_opts = ["Financial problems", "Distance", "Transportation", "Lack of facilities", "Family responsibilities", "No major difficulty", "Other"]
        education_difficulties = st.multiselect(
            "What is the biggest difficulty in accessing education? (Multi-select) *",
            diff_opts,
            default=safe_multiselect(diff_opts, val_edu_diff, ["No major difficulty"])
        )
        education_difficulties_other = ""
        if "Other" in education_difficulties:
            education_difficulties_other = st.text_input("Specify other education difficulty:", value=val_edu_diff_other)

        st.divider()
        col7, col8 = st.columns(2)
        with col7:
            emp_opts = ["Employed", "Self-employed", "Student", "Homemaker", "Unemployed", "Retired", "Other"]
            employment_status = st.selectbox("What is your current employment status? *", 
                                            emp_opts, index=safe_index(emp_opts, val_emp_status))
            employment_status_other = ""
            if employment_status == "Other":
                employment_status_other = st.text_input("Specify other employment status:", value=val_emp_status_other)
                
            occ_opts = ["Private job", "Business", "Government job", "Agriculture", "Daily wage", "Professional", "Other"]
            primary_occupation = st.selectbox("What is the household's main occupation? *", 
                                             occ_opts, index=safe_index(occ_opts, val_occupation))
            primary_occupation_other = ""
            if primary_occupation == "Other":
                primary_occupation_other = st.text_input("Specify other occupation:", value=val_occupation_other)

        with col8:
            earn_opts = ["0", "1", "2", "3", "4+"]
            earning_members = st.radio("How many earning members are in household? *", earn_opts, index=safe_index(earn_opts, val_earning_members, 1), horizontal=True)
            inc_opts = ["Below 10,000 INR", "10,000 to 20,000 INR", "20,000 to 30,000 INR", "30,000 to 50,000 INR", "50,000 to 75,000 INR", "Above 75,000 INR", "Prefer not to say"]
            monthly_income = st.selectbox(
                "What is your approximate monthly household income? *",
                inc_opts,
                index=safe_index(inc_opts, val_income, 2)
            )

        st.divider()
        col9, col10 = st.columns(2)
        with col9:
            house_opts = ["Concrete House / Brick House", "Apartment or Flat", "Tiled Roof House / Sheet Roof House", "Mud House / Thatched House", "Other"]
            house_type = st.selectbox("What type of house do you live in? *",
                                     house_opts, index=safe_index(house_opts, val_house_type))
            house_type_other = ""
            if house_type == "Other":
                house_type_other = st.text_input("Specify other house type:", value=val_house_type_other)

            room_opts = ["1", "2", "3", "4", "5+"]
            available_rooms = st.radio("How many rooms are available? *", room_opts, index=safe_index(room_opts, val_rooms, 1), horizontal=True)
            elec_opts = ["Yes", "No"]
            has_electricity = st.radio("Does household have electricity? *", elec_opts, index=safe_index(elec_opts, val_elec), horizontal=True)
            toilet_opts = ["Private toilet", "Shared toilet", "No toilet"]
            toilet_access = st.radio("Access to toilet? *", toilet_opts, index=safe_index(toilet_opts, val_toilet), horizontal=True)

        with col10:
            water_opts = ["Tap water", "Borewell", "Well", "Tanker", "River or stream", "Other"]
            drinking_water_source = st.selectbox("Primary source of drinking water? *",
                                                water_opts, index=safe_index(water_opts, val_water))
            drinking_water_source_other = ""
            if drinking_water_source == "Other":
                drinking_water_source_other = st.text_input("Specify other water source:", value=val_water_other)

            water_yr_opts = ["Yes", "No", "Sometimes"]
            water_available_year_round = st.radio("Is water available throughout the year? *", water_yr_opts, index=safe_index(water_yr_opts, val_water_year), horizontal=True)
            fuel_opts = ["LPG", "Electricity", "Firewood", "Kerosene", "Other"]
            primary_cooking_fuel = st.selectbox("Primary cooking fuel? *", fuel_opts, index=safe_index(fuel_opts, val_fuel))
            primary_cooking_fuel_other = ""
            if primary_cooking_fuel == "Other":
                primary_cooking_fuel_other = st.text_input("Specify other cooking fuel:", value=val_fuel_other)

            waste_opts = ["Municipal or local collection", "Community collection point", "Open dumping", "Burning", "Other"]
            waste_disposal = st.selectbox("Household waste disposal? *",
                                         waste_opts, index=safe_index(waste_opts, val_waste))
            waste_disposal_other = ""
            if waste_disposal == "Other":
                waste_disposal_other = st.text_input("Specify other waste disposal method:", value=val_waste_other)

        st.divider()
        col11, col12 = st.columns(2)
        with col11:
            net_opts = ["Yes", "No"]
            has_internet = st.radio("Does household have internet access? *", net_opts, index=safe_index(net_opts, val_internet), horizontal=True)
        with col12:
            dev_opts = ["Smartphone", "Laptop", "Desktop", "Tablet", "Other", "No internet"]
            internet_devices = st.multiselect(
                "Primary devices used to access internet? (Multi-select) *",
                dev_opts,
                default=safe_multiselect(dev_opts, val_devices, ["Smartphone"])
            )
            internet_devices_other = ""
            if "Other" in internet_devices:
                internet_devices_other = st.text_input("Specify other internet device:", value=val_devices_other)

        st.divider()
        st.write("Rate access to essential services in your area from **1 (Very Poor)** to **5 (Very Good)**:")
        
        r_c1, r_c2 = st.columns(2)
        with r_c1:
            r_edu = st.select_slider("Education Quality (1-5)", options=[1, 2, 3, 4, 5], value=val_r_edu)
            r_health = st.select_slider("Healthcare Access (1-5)", options=[1, 2, 3, 4, 5], value=val_r_health)
            r_trans = st.select_slider("Transportation (1-5)", options=[1, 2, 3, 4, 5], value=val_r_trans)
        with r_c2:
            r_bank = st.select_slider("Banking Facilities (1-5)", options=[1, 2, 3, 4, 5], value=val_r_bank)
            r_market = st.select_slider("Local Markets (1-5)", options=[1, 2, 3, 4, 5], value=val_r_market)

        prob_opts = ["Unemployment", "Low income", "Education", "Healthcare", "Drinking water", "Sanitation", "Transportation", "Housing", "Waste management", "Digital connectivity", "Other"]
        biggest_problems = st.multiselect(
            "What is the biggest socio-economic problem in your area? (Multi-select) *",
            prob_opts,
            default=safe_multiselect(prob_opts, val_problems, ["Waste management"])
        )
        biggest_problems_other = ""
        if "Other" in biggest_problems:
            biggest_problems_other = st.text_input("Specify other problem:", value=val_problems_other)

        prio_opts = ["Education", "Employment", "Healthcare", "Roads and transport", "Drinking water", "Sanitation", "Housing", "Digital connectivity", "Waste management", "Other"]
        highest_priority = st.multiselect(
            "What improvement should be given highest priority? (Multi-select) *",
            prio_opts,
            default=safe_multiselect(prio_opts, val_priority, ["Roads and transport"])
        )
        highest_priority_other = ""
        if "Other" in highest_priority:
            highest_priority_other = st.text_input("Specify other priority:", value=val_priority_other)

        # Photo Evidence (Only if On-Field)
        if "On-Field" in entry_mode:
            st.divider()
            if saved_photos:
                st.caption(f"📸 **Photos Already Saved with this Survey ({len(saved_photos)})**:")
                p_cols = st.columns(min(len(saved_photos), 4))
                for i, p_url in enumerate(saved_photos):
                    p_cols[i % min(len(saved_photos), 4)].image(p_url, width=110)
            
            st.caption("Capture new photos using smartphone camera or upload gallery files to Supabase Storage (`survey-photos`).")
            cam_photo = st.camera_input("📷 Take Photo with Smartphone Camera")
            file_photos = st.file_uploader("🖼️ Or Upload Existing Photos from Device", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
        else:
            cam_photo = None
            file_photos = None

        surveyor_notes = st.text_area("Observations / Notes (Optional)", value=val_notes, placeholder="e.g. Additional remarks or notes...")

        st.markdown("---")
        
        # Dual Action Buttons: Save & Fill Later OR Submit Final
        col_act1, col_act2 = st.columns([1, 1])
        with col_act1:
            save_draft_submitted = st.form_submit_button(
                "💾 Save & Fill Later (Draft)", 
                use_container_width=True,
                help="Save your current answers as a cloud draft. You can safely close your device and finish this survey anytime."
            )
        with col_act2:
            final_submitted = st.form_submit_button(
                "🚀 Submit Complete Survey & Next", 
                type="primary", 
                use_container_width=True,
                help="Finalize and permanently submit this completed survey."
            )

        # --- HANDLER 1: SAVE & FILL LATER (DRAFT) ---
        if save_draft_submitted:
            with st.spinner("Saving draft to Supabase Cloud..."):
                new_photo_urls = []
                if cam_photo is not None:
                    c_url = upload_photo_to_supabase(cam_photo.getvalue(), f"draft_cam_{int(time.time())}.jpg")
                    if c_url:
                        new_photo_urls.append(c_url)
                if file_photos:
                    for f in file_photos:
                        f_url = upload_photo_to_supabase(f.getvalue(), f.name)
                        if f_url:
                            new_photo_urls.append(f_url)

                total_photos = saved_photos + new_photo_urls
                draft_name = full_name.strip() if full_name.strip() else f"Household #{st.session_state.household_count}"
                draft_loc = locality.strip() if locality.strip() else "Locality Pending"

                draft_state_payload = {
                    "full_name": draft_name,
                    "gender": gender,
                    "email": email.strip(),
                    "age": int(age),
                    "locality": draft_loc,
                    "gps_tag": gps_tag.strip(),
                    "household_members": household_members,
                    "highest_qualification": highest_qualification,
                    "highest_qualification_other": highest_qualification_other,
                    "members_studying": members_studying,
                    "distance_to_education": distance_to_education,
                    "education_difficulties": education_difficulties,
                    "education_difficulties_other": education_difficulties_other,
                    "employment_status": employment_status,
                    "employment_status_other": employment_status_other,
                    "primary_occupation": primary_occupation,
                    "primary_occupation_other": primary_occupation_other,
                    "earning_members": earning_members,
                    "monthly_income": monthly_income,
                    "house_type": house_type,
                    "house_type_other": house_type_other,
                    "available_rooms": available_rooms,
                    "has_electricity": has_electricity,
                    "drinking_water_source": drinking_water_source,
                    "drinking_water_source_other": drinking_water_source_other,
                    "water_available_year_round": water_available_year_round,
                    "toilet_access": toilet_access,
                    "primary_cooking_fuel": primary_cooking_fuel,
                    "primary_cooking_fuel_other": primary_cooking_fuel_other,
                    "waste_disposal": waste_disposal,
                    "waste_disposal_other": waste_disposal_other,
                    "has_internet": has_internet,
                    "internet_devices": internet_devices,
                    "internet_devices_other": internet_devices_other,
                    "rating_education": int(r_edu),
                    "rating_healthcare": int(r_health),
                    "rating_transportation": int(r_trans),
                    "rating_banking": int(r_bank),
                    "rating_markets": int(r_market),
                    "biggest_problems": biggest_problems,
                    "biggest_problems_other": biggest_problems_other,
                    "highest_priority_improvement": highest_priority,
                    "highest_priority_improvement_other": highest_priority_other,
                    "raw_notes": surveyor_notes.strip() if surveyor_notes else "",
                    "photo_urls": total_photos,
                    "entry_mode": entry_mode
                }

                raw_json = json.dumps(draft_state_payload)
                draft_notes_col = f"{form_source_tag} [STATUS: DRAFT] [DRAFT_RAW: {raw_json}]"
                if surveyor_notes and surveyor_notes.strip():
                    draft_notes_col += f" {surveyor_notes.strip()}"

                draft_record = {
                    "full_name": f"[DRAFT] {draft_name}",
                    "email": email.strip() if email.strip() else "draft@survey.local",
                    "gender": gender,
                    "age": int(age),
                    "locality": draft_loc,
                    "household_members": household_members,
                    "highest_qualification": highest_qualification,
                    "highest_qualification_other": highest_qualification_other if highest_qualification_other else None,
                    "members_studying": members_studying,
                    "distance_to_education": distance_to_education,
                    "education_difficulties": education_difficulties if education_difficulties else ["No major difficulty"],
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
                    "internet_devices": internet_devices if internet_devices else ["Smartphone"],
                    "internet_devices_other": internet_devices_other if internet_devices_other else None,
                    "rating_education": int(r_edu),
                    "rating_healthcare": int(r_health),
                    "rating_transportation": int(r_trans),
                    "rating_banking": int(r_bank),
                    "rating_markets": int(r_market),
                    "biggest_problems": biggest_problems if biggest_problems else ["Waste management"],
                    "biggest_problems_other": biggest_problems_other if biggest_problems_other else None,
                    "highest_priority_improvement": highest_priority if highest_priority else ["Roads and transport"],
                    "highest_priority_improvement_other": highest_priority_other if highest_priority_other else None,
                    "photo_urls": total_photos,
                    "surveyor_notes": draft_notes_col
                }

                try:
                    if st.session_state.active_draft_id:
                        update_survey_record(st.session_state.active_draft_id, draft_record)
                        st.session_state.draft_data = draft_state_payload
                        st.success(f"💾 Draft updated for '{draft_name}'! You can safely leave and resume anytime.")
                    else:
                        resp_ins = insert_survey_record(draft_record)
                        if isinstance(resp_ins, list) and len(resp_ins) > 0 and "id" in resp_ins[0]:
                            st.session_state.active_draft_id = resp_ins[0]["id"]
                        st.session_state.draft_data = draft_state_payload
                        st.success(f"💾 Draft saved for '{draft_name}'! You can resume filling it anytime from '📂 Saved Drafts' above.")
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving draft to Supabase: {e}")

        # --- HANDLER 2: FINAL COMPLETE SUBMISSION ---
        if final_submitted:
            if not full_name.strip() or full_name.strip().startswith("[DRAFT]"):
                st.error("⚠️ Please enter the respondent's full name.")
            elif not locality.strip() or locality.strip() == "Locality Pending":
                st.error("⚠️ Please enter the locality / area name.")
            else:
                with st.spinner("Submitting final survey to Supabase..."):
                    new_photo_urls = []
                    if cam_photo is not None:
                        c_url = upload_photo_to_supabase(cam_photo.getvalue(), f"cam_h{st.session_state.household_count}.jpg")
                        if c_url:
                            new_photo_urls.append(c_url)
                    if file_photos:
                        for f in file_photos:
                            f_url = upload_photo_to_supabase(f.getvalue(), f.name)
                            if f_url:
                                new_photo_urls.append(f_url)

                    total_photos = saved_photos + new_photo_urls

                    # Build clean surveyor notes
                    final_notes = f"{form_source_tag} "
                    if gps_tag.strip():
                        final_notes += f"[GPS: {gps_tag.strip()}] "
                    if surveyor_notes and surveyor_notes.strip():
                        final_notes += surveyor_notes.strip()

                    final_record = {
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
                        "photo_urls": total_photos,
                        "surveyor_notes": final_notes.strip() if final_notes.strip() else None
                    }

                    try:
                        if st.session_state.active_draft_id:
                            update_survey_record(st.session_state.active_draft_id, final_record)
                            st.success(f"🎉 Resumed survey for '{full_name}' successfully completed and finalized!")
                        else:
                            insert_survey_record(final_record)
                            st.success(f"🎉 Survey for '{full_name}' successfully submitted to Supabase!")
                        
                        st.session_state.active_draft_id = None
                        st.session_state.draft_data = {}
                        st.session_state.form_render_id += 1
                        st.session_state.household_count += 1
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
                    except Exception as err:
                        st.error(f"Failed to submit survey to Supabase: {err}")

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

        # Mobile-friendly 2-row layout
        row1_c1, row1_c2 = st.columns(2)
        row1_c1.metric("Responses in View", tot_hh)
        row1_c2.metric("Photos Uploaded", tot_photos)

        row2_c1, row2_c2, row2_c3 = st.columns(3)
        row2_c1.metric("Electricity", f"{elec_rate:.1f}%")
        row2_c2.metric("Piped Water", f"{water_rate:.1f}%")
        row2_c3.metric("Sanitation", f"{toilet_rate:.1f}%")

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
            st.subheader("Household Main Occupations")
            occ_col = 'household_main_occupation' if 'household_main_occupation' in df_filtered.columns else 'primary_occupation'
            occ_counts = df_filtered[occ_col].value_counts().reset_index()
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
    st.subheader(f"🗺️ GIS Mapping & Household Ground-Truth ({data_source_trigger})")
    st.caption("Interactive GIS map with direct phone location detection, satellite imagery, household pins, and manual coordinate search.")

    def parse_gps(notes):
        if not isinstance(notes, str):
            return None, None
        match = re.search(r'\[GPS:\s*([+-]?\d+\.?\d*),\s*([+-]?\d+\.?\d*)\]', notes)
        if match:
            return float(match.group(1)), float(match.group(2))
        return None, None

    # Manual Coordinate Search & Pin Bar
    col_gis1, col_gis2 = st.columns([3, 1])
    with col_gis1:
        manual_gis_search = st.text_input(
            "📍 Manual Coordinate Search / Custom Pin (Latitude, Longitude):", 
            placeholder="e.g. 19.0760, 72.8777",
            key="gis_manual_search"
        )
    with col_gis2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        pin_manual_btn = st.button("📌 Pin on Map", use_container_width=True, key="btn_gis_pin")

    manual_point = None
    if manual_gis_search and manual_gis_search.strip():
        m_match = re.search(r'([+-]?\d+\.?\d*)\s*,\s*([+-]?\d+\.?\d*)', manual_gis_search.strip())
        if m_match:
            manual_point = (float(m_match.group(1)), float(m_match.group(2)))

    # Parse filtered survey GPS coordinates
    valid_coords = []
    if not df_filtered.empty and 'surveyor_notes' in df_filtered.columns:
        gps_coords = [parse_gps(n) for n in df_filtered['surveyor_notes']]
        valid_coords = [(lat, lon, df_filtered.iloc[i]) for i, (lat, lon) in enumerate(gps_coords) if lat is not None and lon is not None]

    # Determine center and zoom level
    if manual_point:
        center_lat, center_lon = manual_point
        zoom_start = 16
    elif valid_coords:
        center_lat = sum([c[0] for c in valid_coords]) / len(valid_coords)
        center_lon = sum([c[1] for c in valid_coords]) / len(valid_coords)
        zoom_start = 14
    else:
        center_lat, center_lon = 19.0760, 72.8777
        zoom_start = 13

    # Build Folium Map with 100% Free, Open Tile Layers (No API Key Required)
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start, tiles=None)

    folium.TileLayer(
        tiles='https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        name='🗺️ Street Map (OpenStreetMap)',
        show=True
    ).add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri World Imagery',
        name='🛰️ Satellite View (Esri)',
        show=False
    ).add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
        attr='Esri World Street Map',
        name='🏙️ Detailed Map (Esri Topo)',
        show=False
    ).add_to(m)

    # Phone GPS Live Tracking Control
    if LocateControl:
        LocateControl(
            auto_start=False,
            keepCurrentZoomLevel=False,
            locateOptions={"enableHighAccuracy": True, "maxZoom": 18},
            strings={"title": "📍 Track My Phone Location (GPS)"}
        ).add_to(m)

    # Fullscreen control
    if Fullscreen:
        Fullscreen(position='topleft').add_to(m)

    # Layer Switcher
    folium.LayerControl(position='topright').add_to(m)

    # Plot Household survey markers
    for lat, lon, row in valid_coords:
        is_gform = row.get("source_type") == "Google Form"
        marker_color = "green" if is_gform else "blue"
        occ_display = row.get('household_main_occupation', row.get('primary_occupation', 'N/A'))
        popup_html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-size: 12px; width: 220px; line-height: 1.4;">
            <b style="color: #2563eb; font-size: 13px;">{row['full_name']}</b><br>
            <span style="color: #64748b;">📍 {row['locality']} ({row.get('source_type', 'On-Field')})</span><hr style="margin: 5px 0;">
            <b>Occupation:</b> {occ_display}<br>
            <b>House:</b> {row['house_type']}<br>
            <b>Income:</b> {row['monthly_income']}<br>
            <b>Water:</b> {row['drinking_water_source']}<br>
            <b>GPS:</b> {lat:.6f}, {lon:.6f}
        </div>
        """
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"{row['full_name']} — {row['locality']}",
            icon=folium.Icon(color=marker_color, icon="home", prefix="fa")
        ).add_to(m)

    # Plot Manual Location Pin if searched
    if manual_point:
        folium.Marker(
            location=[manual_point[0], manual_point[1]],
            popup=folium.Popup(f"<b>📍 Manually Pinned Location:</b><br>{manual_point[0]:.6f}, {manual_point[1]:.6f}", max_width=250),
            tooltip=f"Manual Pin: {manual_point[0]:.6f}, {manual_point[1]:.6f}",
            icon=folium.Icon(color="red", icon="crosshairs", prefix="fa")
        ).add_to(m)
        folium.Circle(
            location=[manual_point[0], manual_point[1]],
            radius=60,
            color="red",
            weight=2,
            fill=True,
            fill_opacity=0.15
        ).add_to(m)

    # Render Map & Capture User Click
    map_data = st_folium(m, width="100%", height=520, returned_objects=["last_clicked"])

    # Click-to-Coordinate Feedback
    if map_data and map_data.get("last_clicked"):
        c_lat = map_data["last_clicked"]["lat"]
        c_lng = map_data["last_clicked"]["lng"]
        st.success(f"📍 **Selected Point Coordinates:** `{c_lat:.6f}, {c_lng:.6f}` — Clicked on map")

    col_gis_info1, col_gis_info2 = st.columns([2, 1])
    with col_gis_info1:
        if valid_coords:
            st.caption(f"Showing **{len(valid_coords)}** GPS-tagged household profiles. 🔵 Blue = On-Field Survey | 🟢 Green = Google Form import | 🔴 Red = Manual Pin.")
        else:
            st.info("ℹ️ No GPS-tagged household records found yet in this filter. Tap the **📍 crosshair button** on the map to find your phone location, or click anywhere on the map to inspect coordinates.")
    with col_gis_info2:
        st.caption("💡 **Tip:** Tap 📍 on top-left to track phone GPS. Toggle 🛰️ Satellite view on top-right.")

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
    st.subheader("📋 Data Management & Submissions")

    num_saved_drafts = len(df_drafts) if (not df_raw.empty and "is_draft" in df_raw.columns) else 0
    t5_completed, t5_drafts = st.tabs([f"✅ Finalized Responses ({len(df_filtered)})", f"📝 Incomplete Drafts ({num_saved_drafts})"])

    with t5_drafts:
        st.markdown("### 📝 Incomplete Draft Surveys (Save & Fill Later)")
        st.caption("Surveys paused on the field. You can resume and finish any draft, or remove obsolete ones.")
        if df_drafts.empty:
            st.info("No saved drafts found in cloud. You can click '💾 Save & Fill Later' on any survey in Tab 1.")
        else:
            display_drafts = df_drafts[["full_name", "locality", "created_at"]].copy()
            display_drafts["full_name"] = display_drafts["full_name"].str.replace("[DRAFT] ", "")
            st.dataframe(display_drafts, use_container_width=True)

            st.write("---")
            draft_manage_map = {}
            for _, d_row in df_drafts.iterrows():
                d_id = str(d_row["id"])
                d_name = str(d_row.get("full_name", "")).replace("[DRAFT] ", "").strip()
                d_loc = str(d_row.get("locality", "N/A"))
                d_time = str(d_row.get("created_at", ""))[:16].replace("T", " ")
                draft_manage_map[f"📝 {d_name} — {d_loc} ({d_time})"] = d_id
            
            chosen_draft_m_label = st.selectbox("Select draft to resume or manage:", list(draft_manage_map.keys()), key="sel_t5_draft")
            chosen_draft_m_id = draft_manage_map[chosen_draft_m_label]
            
            col_dm1, col_dm2 = st.columns([1.5, 1])
            with col_dm1:
                if st.button("🚀 Resume This Draft in Tab 1", type="primary", use_container_width=True, key="btn_resume_t5"):
                    target_row = df_drafts[df_drafts["id"] == chosen_draft_m_id].iloc[0]
                    notes_str = str(target_row.get("surveyor_notes", ""))
                    parsed_payload = {}
                    if "[DRAFT_RAW:" in notes_str:
                        try:
                            raw_match = re.search(r'\[DRAFT_RAW:\s*({.*?})\s*\]', notes_str, re.DOTALL)
                            if raw_match:
                                parsed_payload = json.loads(raw_match.group(1))
                        except Exception:
                            pass
                    if not parsed_payload:
                        parsed_payload = target_row.to_dict()
                    
                    st.session_state.active_draft_id = chosen_draft_m_id
                    st.session_state.draft_data = parsed_payload
                    st.session_state.form_render_id += 1
                    st.success("Draft loaded! Switch to '📝 Fill Household Survey' tab to finish and submit.")
                    st.rerun()
            with col_dm2:
                if st.button("🗑️ Delete This Draft", use_container_width=True, key="btn_del_t5"):
                    if delete_survey_record(chosen_draft_m_id):
                        if st.session_state.active_draft_id == chosen_draft_m_id:
                            st.session_state.active_draft_id = None
                            st.session_state.draft_data = {}
                            st.session_state.form_render_id += 1
                        st.success("Draft removed from cloud.")
                        st.cache_data.clear()
                        st.rerun()

    with t5_completed:
        st.markdown(f"### Filtered View: **{data_source_trigger}**")
        if not df_filtered.empty:
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
                            new_occupation = st.text_input("Household Main Occupation", value=str(target_row.get('household_main_occupation', target_row.get('primary_occupation', ''))))
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
