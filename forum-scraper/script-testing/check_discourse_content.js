const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_DATABASE,
  user: process.env.DB_USERNAME,
  password: process.env.DB_PASSWORD,
  ssl: {
    require: true,
    rejectUnauthorized: true,
    ca: require('fs').readFileSync(require('path').join(__dirname, '..', process.env.DB_SSLROOTCERT)).toString()
  }
});

async function checkDiscourseContent() {
  console.log('Checking Discourse content (selftext field) in database...\n');
  
  try {
    const client = await pool.connect();
    
    // Check Discourse posts and their selftext content
    const discoursePosts = await client.query(`
      SELECT id, title, author, selftext, url, created_utc
      FROM "forum-posts" 
      WHERE source = 'discourse'
      ORDER BY created_utc DESC 
      LIMIT 10
    `);
    
    console.log('🗨️  Recent Discourse posts with content:');
    console.log('='.repeat(80));
    
    discoursePosts.rows.forEach((post, index) => {
      const date = new Date(post.created_utc * 1000).toLocaleString();
      console.log(`\n${index + 1}. "${post.title}"`);
      console.log(`   By: ${post.author} | Date: ${date}`);
      console.log(`   URL: ${post.url}`);
      console.log(`   Content (selftext): "${post.selftext || '[EMPTY]'}"`);
      console.log(`   Content length: ${(post.selftext || '').length} characters`);
    });
    
    // Count empty vs non-empty selftext
    const contentStats = await client.query(`
      SELECT 
        COUNT(*) as total_posts,
        COUNT(CASE WHEN selftext IS NULL OR selftext = '' THEN 1 END) as empty_content,
        COUNT(CASE WHEN selftext IS NOT NULL AND selftext != '' THEN 1 END) as has_content
      FROM "forum-posts" 
      WHERE source = 'discourse'
    `);
    
    console.log('\n📊 Discourse Content Statistics:');
    const stats = contentStats.rows[0];
    console.log(`  Total posts: ${stats.total_posts}`);
    console.log(`  Posts with content: ${stats.has_content}`);
    console.log(`  Posts with empty content: ${stats.empty_content}`);
    console.log(`  Content percentage: ${((stats.has_content / stats.total_posts) * 100).toFixed(1)}%`);
    
    client.release();
    console.log('\n✅ Discourse content check completed!');
    
  } catch (error) {
    console.error('❌ Error checking Discourse content:', error.message);
  }
}

// Run the check
if (require.main === module) {
  checkDiscourseContent().then(() => {
    console.log('Check finished');
    process.exit(0);
  }).catch(error => {
    console.error('Check failed:', error);
    process.exit(1);
  });
}

module.exports = { checkDiscourseContent };