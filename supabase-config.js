/**
 * Supabase Client Configuration
 * 
 * You can set your Supabase credentials here or configure them via the UI Settings modal.
 * Setting them in the UI will save them to localStorage.
 */

const SUPABASE_DEFAULTS = {
    // Replace with your project's URL and Anon Key from Supabase Dashboard -> Project Settings -> API
    url: window.localStorage.getItem('SUPABASE_URL') || '',
    anonKey: window.localStorage.getItem('SUPABASE_ANON_KEY') || '',
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

// Auto-initialize if credentials exist
if (window.supabase && SUPABASE_DEFAULTS.url && SUPABASE_DEFAULTS.anonKey) {
    initSupabase();
}
