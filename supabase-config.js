/**
 * Supabase Client Configuration
 */

const SUPABASE_DEFAULTS = {
    url: window.localStorage.getItem('SUPABASE_URL') || 'https://tsfzjhapftoacachqute.supabase.co',
    anonKey: window.localStorage.getItem('SUPABASE_ANON_KEY') || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRzZnpqaGFwZnRvYWNhY2hxdXRlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk4OTE4NTQsImV4cCI6MjEwNTQ2Nzg1NH0.60yo8hh51yQvdoGfYdEy8PF0XVLUyePwfuuK-pndJ6o',
    storageBucket: 'survey-photos'
};

let supabaseClient = null;

function initSupabase(url, key) {
    const supabaseUrl = url || SUPABASE_DEFAULTS.url;
    const supabaseKey = key || SUPABASE_DEFAULTS.anonKey;

    if (supabaseUrl && supabaseKey && window.supabase) {
        try {
            supabaseClient = window.supabase.createClient(supabaseUrl, supabaseKey);
            console.log('Supabase client initialized successfully.');
            return supabaseClient;
        } catch (err) {
            console.error('Failed to initialize Supabase client:', err);
            supabaseClient = null;
            return null;
        }
    }
    supabaseClient = null;
    return null;
}

// Auto-initialize with configured credentials
if (window.supabase && SUPABASE_DEFAULTS.url && SUPABASE_DEFAULTS.anonKey) {
    initSupabase();
}
