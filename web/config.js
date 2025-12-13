/**
 * Classroom Control Panel - Configuration
 * 
 * SETUP INSTRUCTIONS:
 * 1. Create a free Supabase account at https://supabase.com
 * 2. Create a new project
 * 3. Go to Settings > API and copy your Project URL and anon/public key
 * 4. Replace the placeholder values below
 * 5. The same values need to be used in the local relay app config
 */

const CONFIG = {
    // Supabase Configuration
    // Get these from your Supabase project: Settings > API
    SUPABASE_URL: 'YOUR_SUPABASE_PROJECT_URL',  // e.g., 'https://xxxxx.supabase.co'
    SUPABASE_ANON_KEY: 'YOUR_SUPABASE_ANON_KEY', // The "anon" / "public" key
    
    // Password for students to join (set this to something your class knows)
    // This is a simple client-side check - Squarespace's password protection adds another layer
    CLASS_PASSWORD: 'classroom123',
    
    // Cooldown between actions (in milliseconds) - prevents spam
    // Set to 0 to disable cooldown
    ACTION_COOLDOWN: 3000,  // 3 seconds default
    
    // Enable/disable specific categories
    CATEGORIES: {
        visual: true,
        reaction: true,
        sound: true,
        poll: true
    },
    
    // Supabase table name (must match local relay app)
    TABLE_NAME: 'classroom_commands',
    
    // Session storage key for remembering login
    SESSION_KEY: 'classroom_session'
};

// Don't modify below this line
if (typeof window !== 'undefined') {
    window.CONFIG = CONFIG;
}
