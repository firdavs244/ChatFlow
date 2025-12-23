-- ChatFlow Database Initialization
-- This script runs when PostgreSQL container starts for the first time

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable full-text search
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for better performance (will be created by SQLAlchemy, but adding here for completeness)
-- These are just comments showing what indexes we'll have

-- Users table indexes
-- CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
-- CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Messages table indexes  
-- CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id);
-- CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON messages(sender_id);
-- CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

-- Chat members table indexes
-- CREATE INDEX IF NOT EXISTS idx_chat_members_user_id ON chat_members(user_id);
-- CREATE INDEX IF NOT EXISTS idx_chat_members_chat_id ON chat_members(chat_id);

-- Full-text search index for messages (optional, for advanced search)
-- CREATE INDEX IF NOT EXISTS idx_messages_content_fts ON messages USING gin(to_tsvector('english', content));

-- Grant permissions (if needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO chatflow;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO chatflow;

