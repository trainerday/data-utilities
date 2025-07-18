require('dotenv').config();

// Test categorizing a few existing posts to see the system in action
async function categorizeExistingPosts() {
  console.log('Testing categorization on existing posts...\n');
  
  const { Pool } = require('pg');
  const PostCategorizer = require('../openai-categorizer');
  
  if (!process.env.OPENAI_API_KEY || process.env.OPENAI_API_KEY === 'your_openai_api_key_here') {
    console.error('❌ OpenAI API key not configured');
    return;
  }
  
  const pool = new Pool({
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    database: process.env.DB_DATABASE,
    user: process.env.DB_USERNAME,
    password: process.env.DB_PASSWORD,
    ssl: {
      require: true,
      rejectUnauthorized: false,
      ca: process.env.DB_SSL_CERT
    }
  });
  
  try {
    const client = await pool.connect();
    
    // Get a few recent posts that haven't been categorized yet
    const result = await client.query(`
      SELECT id, title, selftext, subreddit 
      FROM "forum-posts" 
      WHERE category = 'other' 
      AND created_utc >= extract(epoch from date_trunc('day', now())) 
      ORDER BY created_utc DESC 
      LIMIT 5
    `);
    
    if (result.rows.length === 0) {
      console.log('No posts found to categorize');
      return;
    }
    
    console.log(`Found ${result.rows.length} posts to categorize:\n`);
    
    const categorizer = new PostCategorizer(process.env.OPENAI_API_KEY);
    
    for (const post of result.rows) {
      console.log(`📝 "${post.title}"`);
      console.log(`   Content: "${(post.selftext || '').substring(0, 100)}${post.selftext && post.selftext.length > 100 ? '...' : ''}"`);
      
      try {
        const category = await categorizer.categorizePost(post.title, post.selftext, post.subreddit);
        
        // Update the post category in database
        await client.query(
          'UPDATE "forum-posts" SET category = $1 WHERE id = $2',
          [category, post.id]
        );
        
        console.log(`   ✅ Categorized as: ${category.toUpperCase()}`);
        
        if (category === 'Performance' || category === 'Indoor Cycling') {
          console.log(`   🎯 This is a ${category.toUpperCase()} post!`);
        }
        
      } catch (error) {
        console.error(`   ❌ Error: ${error.message}`);
      }
      
      console.log();
      
      // Add delay between requests
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    client.release();
    console.log('✅ Categorization test completed');
    
  } catch (error) {
    console.error('❌ Database error:', error.message);
  } finally {
    await pool.end();
  }
}

categorizeExistingPosts();