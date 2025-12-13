-- ============================================================================
-- Classroom Control - Supabase Database Setup
-- ============================================================================
-- Run this SQL in your Supabase project's SQL Editor:
-- 1. Go to your Supabase project dashboard
-- 2. Click "SQL Editor" in the left sidebar  
-- 3. Click "New Query"
-- 4. Paste this entire file and click "Run"
-- ============================================================================

-- Table for storing incoming commands from students
CREATE TABLE IF NOT EXISTS classroom_commands (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    action TEXT NOT NULL,
    category TEXT NOT NULL,
    session_id TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE
);

-- Table for system status (pause/resume)
CREATE TABLE IF NOT EXISTS system_status (
    id TEXT PRIMARY KEY DEFAULT 'main',
    paused BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default system status
INSERT INTO system_status (id, paused) 
VALUES ('main', false) 
ON CONFLICT (id) DO NOTHING;

-- Enable Row Level Security
ALTER TABLE classroom_commands ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_status ENABLE ROW LEVEL SECURITY;

-- Policies for classroom_commands
-- Allow anyone to insert commands (students)
CREATE POLICY "Allow insert commands" ON classroom_commands
    FOR INSERT 
    WITH CHECK (true);

-- Allow anyone to read commands (for the relay app)
CREATE POLICY "Allow read commands" ON classroom_commands
    FOR SELECT 
    USING (true);

-- Policies for system_status  
-- Allow anyone to read status (for web frontend)
CREATE POLICY "Allow read status" ON system_status
    FOR SELECT 
    USING (true);

-- Allow anyone to update status (for relay app kill switch)
-- In production, you might want to restrict this to authenticated users
CREATE POLICY "Allow update status" ON system_status
    FOR UPDATE 
    USING (true);

CREATE POLICY "Allow insert status" ON system_status
    FOR INSERT 
    WITH CHECK (true);

-- Enable real-time for both tables
ALTER PUBLICATION supabase_realtime ADD TABLE classroom_commands;
ALTER PUBLICATION supabase_realtime ADD TABLE system_status;

-- Optional: Create index for faster timestamp queries
CREATE INDEX IF NOT EXISTS idx_commands_timestamp ON classroom_commands(timestamp DESC);

-- Optional: Auto-cleanup old commands (keeps last 24 hours)
-- This function deletes commands older than 24 hours
CREATE OR REPLACE FUNCTION cleanup_old_commands()
RETURNS void AS $$
BEGIN
    DELETE FROM classroom_commands 
    WHERE timestamp < NOW() - INTERVAL '24 hours';
END;
$$ LANGUAGE plpgsql;

-- Optional: Create a cron job to run cleanup daily
-- Note: Requires pg_cron extension (available in Supabase)
-- Uncomment the following lines if you want automatic cleanup:
-- SELECT cron.schedule('cleanup-commands', '0 0 * * *', 'SELECT cleanup_old_commands()');

-- ============================================================================
-- Verification: Run these queries to verify setup
-- ============================================================================
-- SELECT * FROM classroom_commands LIMIT 5;
-- SELECT * FROM system_status;

-- ============================================================================
-- Test: Insert a test command
-- ============================================================================
-- INSERT INTO classroom_commands (action, category, session_id)
-- VALUES ('confetti', 'visual', 'test_session');
