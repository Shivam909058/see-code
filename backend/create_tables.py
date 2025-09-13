#!/usr/bin/env python3
"""
Simple script to create/fix database tables
"""

from supabase import create_client
import os
from app.utils.config import get_settings

def create_tables():
    """Create the required database tables"""
    
    try:
        settings = get_settings()
        
        # Use service key for admin operations
        if not settings.supabase_service_key:
            print("❌ SUPABASE_SERVICE_KEY not found in environment")
            print("Please add SUPABASE_SERVICE_KEY to your .env file")
            return False
            
        supabase = create_client(settings.supabase_url, settings.supabase_service_key)
        
        print("🔧 Creating/fixing database tables...")
        
        # SQL commands to execute
        sql_commands = [
            # Drop existing constraints if they exist
            "ALTER TABLE IF EXISTS analyses DROP CONSTRAINT IF EXISTS analyses_status_check;",
            "ALTER TABLE IF EXISTS analyses DROP CONSTRAINT IF EXISTS analyses_type_check;",
            
            # Create the analyses table with all required columns
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(50) NOT NULL,
                repository_url TEXT,
                repository_info JSONB DEFAULT '{}',
                quality_metrics JSONB DEFAULT '{}',
                language_stats JSONB DEFAULT '[]',
                issues JSONB DEFAULT '[]',
                dependencies JSONB DEFAULT '[]',
                architecture_insights JSONB DEFAULT '[]',
                summary TEXT DEFAULT '',
                recommendations JSONB DEFAULT '[]',
                processing_time FLOAT DEFAULT 0,
                files_analyzed INTEGER DEFAULT 0,
                lines_analyzed INTEGER DEFAULT 0,
                issues_count INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            
            # Add correct constraints
            "ALTER TABLE analyses ADD CONSTRAINT analyses_status_check CHECK (status IN ('pending', 'running', 'completed', 'failed'));",
            "ALTER TABLE analyses ADD CONSTRAINT analyses_type_check CHECK (type IN ('github', 'upload', 'local'));",
            
            # Create analysis_sessions table
            """
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                analysis_id UUID REFERENCES analyses(id) ON DELETE CASCADE,
                user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
                question TEXT NOT NULL,
                answer TEXT,
                confidence FLOAT,
                context TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            
            # Enable RLS
            "ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;",
            "ALTER TABLE analysis_sessions ENABLE ROW LEVEL SECURITY;",
            
            # Drop existing policies if they exist
            "DROP POLICY IF EXISTS \"Users can view their own analyses\" ON analyses;",
            "DROP POLICY IF EXISTS \"Users can insert their own analyses\" ON analyses;",
            "DROP POLICY IF EXISTS \"Users can update their own analyses\" ON analyses;",
            "DROP POLICY IF EXISTS \"Users can delete their own analyses\" ON analyses;",
            "DROP POLICY IF EXISTS \"Users can view their own sessions\" ON analysis_sessions;",
            "DROP POLICY IF EXISTS \"Users can insert their own sessions\" ON analysis_sessions;",
            
            # Create RLS policies with correct syntax
            """
            CREATE POLICY "Users can view their own analyses" ON analyses
                FOR SELECT USING (auth.uid() = user_id);
            """,
            """
            CREATE POLICY "Users can insert their own analyses" ON analyses
                FOR INSERT WITH CHECK (auth.uid() = user_id);
            """,
            """
            CREATE POLICY "Users can update their own analyses" ON analyses
                FOR UPDATE USING (auth.uid() = user_id);
            """,
            """
            CREATE POLICY "Users can delete their own analyses" ON analyses
                FOR DELETE USING (auth.uid() = user_id);
            """,
            """
            CREATE POLICY "Users can view their own sessions" ON analysis_sessions
                FOR SELECT USING (auth.uid() = user_id);
            """,
            """
            CREATE POLICY "Users can insert their own sessions" ON analysis_sessions
                FOR INSERT WITH CHECK (auth.uid() = user_id);
            """
        ]
        
        # Execute each SQL command
        for i, sql in enumerate(sql_commands, 1):
            try:
                print(f"Executing command {i}/{len(sql_commands)}...")
                result = supabase.rpc('exec_sql', {'query': sql}).execute()
                print(f"✅ Command {i} executed successfully")
            except Exception as e:
                print(f"⚠️  Command {i} failed: {str(e)}")
                # Continue with other commands
        
        print("🎉 Database setup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {str(e)}")
        print("\n📋 Manual SQL Setup Required:")
        print("=" * 50)
        print("Please run the following SQL in your Supabase SQL Editor:")
        print()
        
        manual_sql = """
-- Drop existing constraints
ALTER TABLE IF EXISTS analyses DROP CONSTRAINT IF EXISTS analyses_status_check;
ALTER TABLE IF EXISTS analyses DROP CONSTRAINT IF EXISTS analyses_type_check;

-- Create analyses table
CREATE TABLE IF NOT EXISTS analyses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    repository_url TEXT,
    repository_info JSONB DEFAULT '{}',
    quality_metrics JSONB DEFAULT '{}',
    language_stats JSONB DEFAULT '[]',
    issues JSONB DEFAULT '[]',
    dependencies JSONB DEFAULT '[]',
    architecture_insights JSONB DEFAULT '[]',
    summary TEXT DEFAULT '',
    recommendations JSONB DEFAULT '[]',
    processing_time FLOAT DEFAULT 0,
    files_analyzed INTEGER DEFAULT 0,
    lines_analyzed INTEGER DEFAULT 0,
    issues_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add constraints
ALTER TABLE analyses ADD CONSTRAINT analyses_status_check 
    CHECK (status IN ('pending', 'running', 'completed', 'failed'));
ALTER TABLE analyses ADD CONSTRAINT analyses_type_check 
    CHECK (type IN ('github', 'upload', 'local'));

-- Enable RLS
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view their own analyses" ON analyses
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own analyses" ON analyses
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own analyses" ON analyses
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own analyses" ON analyses
    FOR DELETE USING (auth.uid() = user_id);
"""
        print(manual_sql)
        return False

if __name__ == "__main__":
    create_tables()
