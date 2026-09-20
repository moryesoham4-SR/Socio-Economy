# Socio-Economic Community Survey & GIS Intelligence Platform

An integrated, mobile-first field surveying and decision-support intelligence platform consisting of:
1. **Field Surveyor Web App (`index.html`)**: Mobile-first, single-page application for door-to-door field data collection with camera photo uploads directly to **Supabase Storage** and PostgreSQL.
2. **Executive GIS Analytics Dashboard (`dashboard.py`)**: Interactive **Streamlit** dashboard with **Folium GIS maps**, Plotly distribution charts, and Supabase Storage photo evidence gallery.

---

## Architecture Overview

```text
       ┌───────────────────────────────┐
       │   Field Surveyor Web App      │ (Mobile Browser / Tablet)
       │         index.html            │
       └──────────────┬────────────────┘
                      │
           (Submits Data & Photos)
                      ▼
       ┌───────────────────────────────┐
       │     Supabase Cloud Engine     │
       │  ├─ Database: survey_responses│
       │  └─ Storage:  survey-photos   │
       └──────────────┬────────────────┘
                      │
           (Fetches Data & Photos)
                      ▼
       ┌───────────────────────────────┐
       │   Streamlit GIS Dashboard     │
       │         dashboard.py          │ (Desktop / Decision Makers)
       └───────────────────────────────┘
```

---

## 1. Running the Field Surveyor Web App Locally

```powershell
python server.py
```
Opens the survey portal at: **`http://localhost:8000`**

* **All questions on one single page**: No multi-page clicking while standing at someone's doorstep.
* **Save & Next House**: Validates, uploads photos, inserts into Supabase, increments household count, and resets ready for the next house.
* **Tag GPS Location**: 1-click button to capture on-site latitude & longitude.
* **Camera Capture**: Directly access the smartphone camera to photograph living conditions and utility meters.

---

## 2. Running the Streamlit Dashboard Locally

### Install dependencies:
```bash
pip install -r requirements.txt
```

### Launch Streamlit:
```bash
streamlit run dashboard.py
```
Opens the dashboard at: **`http://localhost:8501`**

---

## 3. Deploying to Streamlit Cloud (Free 1-Click Deployment)

1. Go to [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
2. Click **New app**.
3. Select your repository: **`moryesoham4-SR/Socio-Economy`**.
4. Set Main file path: **`dashboard.py`**.
5. Click **Advanced settings...** and add your Supabase credentials to **Secrets**:
   ```toml
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_ANON_KEY = "your-anon-public-key"
   ```
6. Click **Deploy!** Your live analytics dashboard is now accessible to everyone on the web!

---

## 4. Deploying the Field Surveyor Web App (Vercel / Netlify / GitHub Pages)

Because `index.html` is a standalone single-page web app:
* **Vercel**: Import the GitHub repository and click Deploy (zero configuration needed).
* **Netlify**: Drag-and-drop the folder or connect your GitHub repo.
* **GitHub Pages**: In your repository Settings ➔ Pages, enable GitHub Pages from the `main` branch.

---

## Database & Storage Setup (Supabase)

If you haven't run the SQL script yet:
1. Open your **Supabase Dashboard** ➔ **SQL Editor**.
2. Paste the contents of [`schema.sql`](./schema.sql) and click **Run**.
   - Creates the `survey_responses` table.
   - Creates the `survey-photos` storage bucket.
   - Sets up public access policies.
