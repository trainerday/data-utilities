require('dotenv').config();
const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

// PostgreSQL connection configuration
const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_DATABASE,
  user: process.env.DB_USERNAME,
  password: process.env.DB_PASSWORD,
  ssl: {
    require: true,
    rejectUnauthorized: false, // Allow self-signed certificates for local development
    ca: process.env.DB_SSL_CERT || fs.readFileSync(path.join(__dirname, process.env.DB_SSLROOTCERT || 'postgres.crt')).toString()
  }
});

// Initialize database tables
async function initDb() {
  try {
    const client = await pool.connect();
    
    // Create forum-posts table
    await client.query(`
      CREATE TABLE IF NOT EXISTS "forum-posts" (
        id TEXT PRIMARY KEY,
        title TEXT,
        author TEXT,
        created_utc BIGINT,
        score INTEGER,
        num_comments INTEGER,
        url TEXT,
        selftext TEXT,
        permalink TEXT,
        subreddit TEXT,
        source TEXT DEFAULT 'reddit',
        fetched_at BIGINT,
        responded BOOLEAN DEFAULT false
      )
    `);
    
    // Create forum-post-comments table (renamed from comments)
    await client.query(`
      CREATE TABLE IF NOT EXISTS "forum-post-comments" (
        id SERIAL PRIMARY KEY,
        post_id TEXT,
        author TEXT,
        body TEXT,
        score INTEGER,
        created_utc BIGINT,
        source TEXT DEFAULT 'reddit',
        FOREIGN KEY (post_id) REFERENCES "forum-posts" (id),
        UNIQUE(post_id, author, created_utc)
      )
    `);
    
    // Create request logs table
    await client.query(`
      CREATE TABLE IF NOT EXISTS request_logs (
        id SERIAL PRIMARY KEY,
        timestamp BIGINT,
        request_type TEXT,
        url TEXT,
        duration_ms INTEGER,
        success BOOLEAN,
        status_code INTEGER,
        error_message TEXT
      )
    `);
    
    // Create indexes
    await client.query(`CREATE INDEX IF NOT EXISTS idx_forum_posts_created ON "forum-posts" (created_utc)`);
    await client.query(`CREATE INDEX IF NOT EXISTS idx_forum_posts_source ON "forum-posts" (source)`);
    await client.query(`CREATE INDEX IF NOT EXISTS idx_forum_post_comments_post_id ON "forum-post-comments" (post_id)`);
    await client.query(`CREATE INDEX IF NOT EXISTS idx_request_logs_timestamp ON request_logs (timestamp)`);
    
    client.release();
    console.log('PostgreSQL tables initialized successfully');
    return pool;
  } catch (error) {
    console.error('Error initializing database:', error);
    throw error;
  }
}

// Save posts without comments (initial save)
async function savePostsOnly(posts) {
  const client = await pool.connect();
  const now = Math.floor(Date.now() / 1000);
  
  try {
    for (const post of posts) {
      // Extract post ID from URL (handles both Reddit and Discourse)
      let postId;
      if (post.subreddit === 'trainerroad') {
        // Discourse URL format: .../t/slug/ID
        postId = post.url.split('/').pop();
      } else {
        // Reddit URL format: extract post ID from permalink
        postId = post.url.split('/').slice(-2)[0];
      }
      
      await client.query(`
        INSERT INTO "forum-posts" 
        (id, title, author, created_utc, score, num_comments, url, selftext, permalink, subreddit, source, fetched_at) 
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        ON CONFLICT (id) DO UPDATE SET
          score = EXCLUDED.score,
          num_comments = EXCLUDED.num_comments,
          selftext = EXCLUDED.selftext,
          fetched_at = EXCLUDED.fetched_at
      `, [
        postId,
        post.title,
        post.author,
        Math.floor(post.created.getTime() / 1000),
        post.score,
        post.num_comments,
        post.url,
        post.selftext,
        post.subreddit === 'trainerroad' ? post.url.replace('https://www.trainerroad.com', '') : post.url.replace('https://reddit.com', ''),
        post.subreddit,
        post.subreddit === 'trainerroad' ? 'discourse' : 'reddit',
        now
      ]);
    }
  } catch (error) {
    throw error;
  } finally {
    client.release();
  }
}

// Save comments for a specific post
async function saveCommentsForPost(postId, comments, source = null) {
  const client = await pool.connect();
  
  try {
    // If source not provided, determine it from the post
    let commentSource = source;
    if (!commentSource) {
      const postResult = await client.query('SELECT source FROM "forum-posts" WHERE id = $1', [postId]);
      commentSource = postResult.rows.length > 0 ? postResult.rows[0].source : 'reddit';
    }
    
    for (const comment of comments) {
      await client.query(`
        INSERT INTO "forum-post-comments" 
        (post_id, author, body, score, created_utc, source) 
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (post_id, author, created_utc) DO NOTHING
      `, [
        postId,
        comment.author,
        comment.body,
        comment.score,
        Math.floor(comment.created.getTime() / 1000),
        commentSource
      ]);
    }
  } catch (error) {
    throw error;
  } finally {
    client.release();
  }
}

// Save posts and comments to database (legacy function for refresh route)
async function savePosts(posts) {
  // For compatibility, just use savePostsOnly and then save comments
  await savePostsOnly(posts);
  
  for (const post of posts) {
    if (post.comments && post.comments.length > 0) {
      const postId = post.url.split('/').slice(-2)[0];
      await saveCommentsForPost(postId, post.comments);
    }
  }
}

// Get posts from database for a specific day
async function getPostsForDay(date = new Date()) {
  const client = await pool.connect();
  
  try {
    // Start of day and end of day in UTC seconds
    const startOfDay = new Date(date);
    startOfDay.setUTCHours(0, 0, 0, 0);
    const endOfDay = new Date(date);
    endOfDay.setUTCHours(23, 59, 59, 999);
    
    const startUtc = Math.floor(startOfDay.getTime() / 1000);
    const endUtc = Math.floor(endOfDay.getTime() / 1000);
    
    // Get posts for the day
    const postsResult = await client.query(`
      SELECT * FROM "forum-posts" 
      WHERE created_utc BETWEEN $1 AND $2 
      ORDER BY created_utc DESC
    `, [startUtc, endUtc]);
    
    if (postsResult.rows.length === 0) {
      return [];
    }
    
    // Get comments for all posts
    const postIds = postsResult.rows.map(p => p.id);
    const commentsResult = await client.query(`
      SELECT * FROM "forum-post-comments" 
      WHERE post_id = ANY($1) 
      ORDER BY score DESC
    `, [postIds]);
    
    // Group comments by post_id
    const commentsByPost = {};
    commentsResult.rows.forEach(comment => {
      if (!commentsByPost[comment.post_id]) {
        commentsByPost[comment.post_id] = [];
      }
      commentsByPost[comment.post_id].push({
        author: comment.author,
        body: comment.body,
        score: comment.score,
        created: new Date(comment.created_utc * 1000)
      });
    });
    
    // Combine posts with their comments
    const result = postsResult.rows.map(post => ({
      id: post.id,
      title: post.title,
      author: post.author,
      created: new Date(post.created_utc * 1000),
      score: post.score,
      num_comments: post.num_comments,
      url: post.url,
      selftext: post.selftext,
      subreddit: post.subreddit,
      responded: post.responded,
      comments: commentsByPost[post.id] || []
    }));
    
    return result;
  } catch (error) {
    throw error;
  } finally {
    client.release();
  }
}

// Check if we have recent data (within last 15 minutes)
async function hasRecentData() {
  const client = await pool.connect();
  
  try {
    const fifteenMinutesAgo = Math.floor(Date.now() / 1000) - 900; // 15 minutes
    
    const result = await client.query(`
      SELECT COUNT(*) as count FROM "forum-posts" WHERE fetched_at > $1
    `, [fifteenMinutesAgo]);
    
    return parseInt(result.rows[0].count) > 0;
  } catch (error) {
    throw error;
  } finally {
    client.release();
  }
}

// Get posts that are 1+ hours old but haven't had comments fetched yet
async function getPostsNeedingComments() {
  const client = await pool.connect();
  
  try {
    const oneHourAgo = Math.floor(Date.now() / 1000) - 3600; // 1 hour ago
    
    const result = await client.query(`
      SELECT id, title, permalink, subreddit, num_comments FROM "forum-posts" 
      WHERE created_utc < $1 
      AND id NOT IN (SELECT DISTINCT post_id FROM "forum-post-comments")
      ORDER BY created_utc DESC
    `, [oneHourAgo]);
    
    return result.rows;
  } catch (error) {
    throw error;
  } finally {
    client.release();
  }
}

// Get recent posts (15-60 min old) with high comment counts that need early comment fetch
async function getHotPostsNeedingEarlyComments() {
  const client = await pool.connect();
  
  try {
    const now = Math.floor(Date.now() / 1000);
    const fifteenMinutesAgo = now - 900; // 15 minutes
    const oneHourAgo = now - 3600; // 1 hour
    
    const result = await client.query(`
      SELECT id, permalink, subreddit, num_comments, title FROM "forum-posts" 
      WHERE created_utc BETWEEN $1 AND $2
      AND num_comments >= 15
      AND id NOT IN (SELECT DISTINCT post_id FROM "forum-post-comments")
      ORDER BY num_comments DESC
    `, [oneHourAgo, fifteenMinutesAgo]);
    
    return result.rows;
  } catch (error) {
    throw error;
  } finally {
    client.release();
  }
}

// Log request to database
async function logRequest(requestType, url, durationMs, success, statusCode = null, errorMessage = null) {
  const client = await pool.connect();
  
  try {
    const timestamp = Math.floor(Date.now() / 1000);
    
    const result = await client.query(`
      INSERT INTO request_logs 
      (timestamp, request_type, url, duration_ms, success, status_code, error_message)
      VALUES ($1, $2, $3, $4, $5, $6, $7)
      RETURNING id
    `, [timestamp, requestType, url, durationMs, success, statusCode, errorMessage]);
    
    return result.rows[0].id;
  } catch (error) {
    throw error;
  } finally {
    client.release();
  }
}

// Get recent request logs
async function getRequestLogs(limit = 100) {
  const client = await pool.connect();
  
  try {
    const result = await client.query(`
      SELECT * FROM request_logs ORDER BY timestamp DESC LIMIT $1
    `, [limit]);
    
    const logs = result.rows.map(row => ({
      id: row.id,
      timestamp: new Date(row.timestamp * 1000),
      requestType: row.request_type,
      url: row.url,
      durationMs: row.duration_ms,
      success: row.success,
      statusCode: row.status_code,
      errorMessage: row.error_message
    }));
    
    return logs;
  } catch (error) {
    throw error;
  } finally {
    client.release();
  }
}

// Get request statistics
async function getRequestStats() {
  const client = await pool.connect();
  
  try {
    const oneHourAgo = Math.floor(Date.now() / 1000) - 3600;
    
    const result = await client.query(`
      SELECT 
        COUNT(*) as total_requests,
        SUM(CASE WHEN success = true THEN 1 ELSE 0 END) as successful_requests,
        SUM(CASE WHEN success = false THEN 1 ELSE 0 END) as failed_requests,
        AVG(duration_ms) as avg_response_time,
        request_type
      FROM request_logs 
      WHERE timestamp > $1
      GROUP BY request_type
      UNION ALL
      SELECT 
        COUNT(*) as total_requests,
        SUM(CASE WHEN success = true THEN 1 ELSE 0 END) as successful_requests,
        SUM(CASE WHEN success = false THEN 1 ELSE 0 END) as failed_requests,
        AVG(duration_ms) as avg_response_time,
        'ALL' as request_type
      FROM request_logs 
      WHERE timestamp > $1
    `, [oneHourAgo, oneHourAgo]);
    
    return result.rows;
  } catch (error) {
    throw error;
  } finally {
    client.release();
  }
}

// Update response status for a post
async function updatePostResponseStatus(postId, responded) {
  const client = await pool.connect();
  
  try {
    await client.query(`
      UPDATE "forum-posts" 
      SET responded = $1 
      WHERE id = $2
    `, [responded, postId]);
  } catch (error) {
    throw error;
  } finally {
    client.release();
  }
}

module.exports = {
  initDb,
  savePosts,
  savePostsOnly,
  saveCommentsForPost,
  getPostsForDay,
  hasRecentData,
  getPostsNeedingComments,
  getHotPostsNeedingEarlyComments,
  logRequest,
  getRequestLogs,
  getRequestStats,
  updatePostResponseStatus
};