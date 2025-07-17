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

async function checkDatabase() {
  console.log('Checking database for integrated Reddit + Discourse data...\n');
  
  try {
    const client = await pool.connect();
    
    // Check total posts by source
    const sourceStats = await client.query(`
      SELECT source, COUNT(*) as count 
      FROM "forum-posts" 
      GROUP BY source 
      ORDER BY count DESC
    `);
    
    console.log('📊 Posts by source:');
    sourceStats.rows.forEach(row => {
      console.log(`  ${row.source}: ${row.count} posts`);
    });
    
    // Check posts by subreddit/forum
    const forumStats = await client.query(`
      SELECT subreddit, source, COUNT(*) as count 
      FROM "forum-posts" 
      GROUP BY subreddit, source 
      ORDER BY count DESC
    `);
    
    console.log('\n📊 Posts by forum:');
    forumStats.rows.forEach(row => {
      console.log(`  ${row.subreddit} (${row.source}): ${row.count} posts`);
    });
    
    // Show recent posts from each source
    const recentPosts = await client.query(`
      SELECT title, author, subreddit, source, created_utc, url
      FROM "forum-posts" 
      WHERE created_utc > extract(epoch from now() - interval '1 day')
      ORDER BY created_utc DESC 
      LIMIT 10
    `);
    
    console.log('\n📰 Recent posts:');
    recentPosts.rows.forEach(row => {
      const date = new Date(row.created_utc * 1000).toLocaleString();
      console.log(`  [${row.source}] ${row.subreddit}: "${row.title.substring(0, 60)}..." by ${row.author} (${date})`);
    });
    
    // Check comments
    const commentStats = await client.query(`
      SELECT source, COUNT(*) as count 
      FROM "forum-post-comments" 
      GROUP BY source 
      ORDER BY count DESC
    `);
    
    console.log('\n💬 Comments by source:');
    if (commentStats.rows.length === 0) {
      console.log('  No comments found yet');
    } else {
      commentStats.rows.forEach(row => {
        console.log(`  ${row.source}: ${row.count} comments`);
      });
    }
    
    client.release();
    console.log('\n✅ Database check completed successfully!');
    
  } catch (error) {
    console.error('❌ Error checking database:', error.message);
  }
}

// Run the check
if (require.main === module) {
  checkDatabase().then(() => {
    console.log('Check finished');
    process.exit(0);
  }).catch(error => {
    console.error('Check failed:', error);
    process.exit(1);
  });
}

module.exports = { checkDatabase };