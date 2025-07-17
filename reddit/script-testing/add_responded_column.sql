-- Migration script to add 'responded' column to existing forum-posts table
-- Run this if the table already exists without the responded column

ALTER TABLE "forum-posts" 
ADD COLUMN IF NOT EXISTS responded BOOLEAN DEFAULT false;

-- Update any existing NULL values to false
UPDATE "forum-posts" 
SET responded = false 
WHERE responded IS NULL;