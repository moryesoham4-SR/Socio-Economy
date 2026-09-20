-- ==============================================================================
-- SOCIO-ECONOMIC COMMUNITY SURVEY - SUPABASE SETUP SCRIPT
-- ==============================================================================

-- 1. Create survey_responses table
CREATE TABLE IF NOT EXISTS public.survey_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    
    -- Section 1: Basic Information
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    gender TEXT NOT NULL,
    age INTEGER NOT NULL,
    
    -- Section 2: Location and Household
    locality TEXT NOT NULL,
    household_members TEXT NOT NULL,
    
    -- Section 3: Education
    highest_qualification TEXT NOT NULL,
    highest_qualification_other TEXT,
    members_studying TEXT NOT NULL,
    distance_to_education TEXT NOT NULL,
    education_difficulties TEXT[] NOT NULL DEFAULT '{}',
    education_difficulties_other TEXT,
    
    -- Section 4: Employment & Income
    employment_status TEXT NOT NULL,
    employment_status_other TEXT,
    primary_occupation TEXT NOT NULL,
    primary_occupation_other TEXT,
    earning_members TEXT NOT NULL,
    monthly_income TEXT NOT NULL,
    
    -- Section 5: Housing & Living Conditions
    house_type TEXT NOT NULL,
    house_type_other TEXT,
    available_rooms TEXT NOT NULL,
    has_electricity TEXT NOT NULL,
    drinking_water_source TEXT NOT NULL,
    drinking_water_source_other TEXT,
    water_available_year_round TEXT NOT NULL,
    toilet_access TEXT NOT NULL,
    primary_cooking_fuel TEXT NOT NULL,
    primary_cooking_fuel_other TEXT,
    waste_disposal TEXT NOT NULL,
    waste_disposal_other TEXT,
    
    -- Section 6: Digital Access
    has_internet TEXT NOT NULL,
    internet_devices TEXT[] NOT NULL DEFAULT '{}',
    internet_devices_other TEXT,
    
    -- Section 7: Community Problems & Ratings
    rating_education INTEGER NOT NULL,
    rating_healthcare INTEGER NOT NULL,
    rating_transportation INTEGER NOT NULL,
    rating_banking INTEGER NOT NULL,
    rating_markets INTEGER NOT NULL,
    biggest_problems TEXT[] NOT NULL DEFAULT '{}',
    biggest_problems_other TEXT,
    highest_priority_improvement TEXT[] NOT NULL DEFAULT '{}',
    highest_priority_improvement_other TEXT,
    
    -- Photos uploaded to Supabase Storage
    photo_urls TEXT[] NOT NULL DEFAULT '{}',
    
    -- Additional Surveyor Notes
    surveyor_notes TEXT
);

-- 2. Enable Row Level Security (RLS)
ALTER TABLE public.survey_responses ENABLE ROW LEVEL SECURITY;

-- Clean existing policies if re-running
DROP POLICY IF EXISTS "Allow public insert to survey_responses" ON public.survey_responses;
DROP POLICY IF EXISTS "Allow public read to survey_responses" ON public.survey_responses;

-- Allow anonymous or authenticated users to insert survey responses
CREATE POLICY "Allow public insert to survey_responses" 
ON public.survey_responses 
FOR INSERT 
TO public 
WITH CHECK (true);

-- Allow public or authenticated users to read survey responses (for dashboard/reporting)
CREATE POLICY "Allow public read to survey_responses" 
ON public.survey_responses 
FOR SELECT 
TO public 
USING (true);

-- 3. Set up Storage Bucket for Survey Photos
INSERT INTO storage.buckets (id, name, public)
VALUES ('survey-photos', 'survey-photos', true)
ON CONFLICT (id) DO UPDATE SET public = true;

-- Clean existing storage policies if re-running
DROP POLICY IF EXISTS "Allow public upload to survey-photos bucket" ON storage.objects;
DROP POLICY IF EXISTS "Allow public read of survey-photos bucket" ON storage.objects;
DROP POLICY IF EXISTS "Allow public delete from survey-photos bucket" ON storage.objects;

-- Allow public uploads to survey-photos storage bucket
CREATE POLICY "Allow public upload to survey-photos bucket"
ON storage.objects 
FOR INSERT 
TO public 
WITH CHECK (bucket_id = 'survey-photos');

-- Allow public read access to survey-photos storage bucket
CREATE POLICY "Allow public read of survey-photos bucket"
ON storage.objects 
FOR SELECT 
TO public 
USING (bucket_id = 'survey-photos');

-- Allow public delete from survey-photos bucket
CREATE POLICY "Allow public delete from survey-photos bucket"
ON storage.objects 
FOR DELETE 
TO public 
USING (bucket_id = 'survey-photos');
