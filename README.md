# Socio-Economic Community Survey Web Application

A full-featured, mobile-responsive web portal for conducting the **Socio-Economic Community Survey** with on-site photo uploads and automatic storage into **Supabase Storage** and **Supabase Database**.

---

## Features

- **Accurate Survey Implementation**: Matches all 11 pages of questions across 8 interactive steps:
  - Personal Information (Name, Email, Gender, Age)
  - Location and Household
  - Education (Qualifications, Studying members, Distance, Access difficulties)
  - Employment & Income (Status, Occupation, Earning members, Monthly income)
  - Housing & Living Conditions (House type, Rooms, Electricity)
  - Water, Sanitation & Energy (Drinking water, Year-round availability, Toilet, Fuel, Waste disposal)
  - Digital Access (Internet access, Devices used)
  - Community Problems & Priorities (5-point Essential Services Rating Matrix, Major problems, Highest priorities)
- **Photo Upload to Supabase Storage**:
  - Drag-and-drop or file browser
  - Mobile camera capture support (`capture="environment"`)
  - Image preview thumbnails with quick-delete options
  - Direct upload to Supabase Storage bucket (`survey-photos`)
- **Supabase Integration**:
  - Direct client-side connection via Supabase JavaScript SDK
  - In-app Configuration Modal to test and save credentials into `localStorage`
  - Zero-setup local browser demo mode if credentials are not entered yet
  - Ready-to-use `schema.sql` script for Supabase
- **Submissions Explorer & Analytics**:
  - Built-in "View Responses" modal with stats (Total submissions, Photos count, Average service rating)
  - Individual record inspector
  - Image lightbox preview
  - 1-click **Export to CSV** for Microsoft Excel and Pandas/Data Analysis

---

## Quick Start (Run Locally)

You can launch the web application using Python:

```bash
cd "C:\Users\HP\.gemini\antigravity\scratch\socio-economic-survey"
python server.py
```

This will automatically open the survey portal at:
👉 **`http://localhost:8000`**

*(Alternatively, you can simply double-click `index.html` in Windows File Explorer to open it directly in Google Chrome, Microsoft Edge, or Firefox!)*

---

## Connecting Your Supabase Project

To save survey submissions and photos permanently to Supabase:

### Step 1: Run the Database & Storage Setup Script
1. Go to your [Supabase Dashboard](https://app.supabase.com) and select your project.
2. Click on **SQL Editor** in the left sidebar.
3. Open or copy the contents of [`schema.sql`](./schema.sql).
4. Paste it into the SQL editor and click **Run**.
   - *This creates the `survey_responses` table, the `survey-photos` storage bucket, and public policies for insertions and reads.*

### Step 2: Connect the Website
1. In your Supabase Dashboard, navigate to **Project Settings** -> **API**.
2. Copy your **Project URL** and **anon public API key**.
3. Open the survey website in your browser, click the **Supabase: Settings** button in the top right navigation bar.
4. Paste your Project URL and Anon Key, then click **Test Connection** followed by **Save & Connect**.
5. The badge will turn green (**Supabase: Connected**). All new submissions and photo uploads will now go directly to your Supabase project!

---

## Project Structure

```text
socio-economic-survey/
├── index.html            # Main survey user interface, modals, stepper
├── app.js                # Core logic, validation, Supabase upload & database insert, CSV export
├── styles.css            # Responsive styles, form cards, custom options, Likert matrix
├── supabase-config.js    # Supabase credentials loader and client initializer
├── schema.sql            # PostgreSQL & Supabase Storage bucket setup script
├── server.py             # Lightweight Python server with CORS and auto-open
└── README.md             # Documentation and usage guide
```
