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

async function cleanupDuplicates() {
  console.log('Cleaning up duplicate TrainerRoad posts...\n');
  
  try {
    const client = await pool.connect();
    
    // Find trainerroad posts that are incorrectly marked as reddit source
    const duplicatesResult = await client.query(`
      SELECT id, title, source, subreddit, url
      FROM "forum-posts" 
      WHERE subreddit = 'trainerroad' AND source = 'reddit'
      ORDER BY title
    `);
    
    console.log(`Found ${duplicatesResult.rows.length} TrainerRoad posts incorrectly marked as reddit source:`);
    duplicatesResult.rows.forEach(row => {
      console.log(`  - "${row.title.substring(0, 50)}..." (ID: ${row.id})`);
    });
    
    if (duplicatesResult.rows.length > 0) {
      // Delete the incorrectly categorized posts
      const deleteResult = await client.query(`
        DELETE FROM "forum-posts" 
        WHERE subreddit = 'trainerroad' AND source = 'reddit'
      `);
      
      console.log(`\nDeleted ${deleteResult.rowCount} duplicate posts.`);
      
      // Also delete their comments if any
      const deleteCommentsResult = await client.query(`
        DELETE FROM "forum-post-comments" 
        WHERE post_id IN (
          SELECT id FROM "forum-posts" 
          WHERE subreddit = 'trainerroad' AND source = 'reddit'
        )
      `);
      
      console.log(`Deleted ${deleteCommentsResult.rowCount} associated comments.`);
    }
    
    // Show final stats
    const finalStats = await client.query(`
      SELECT source, subreddit, COUNT(*) as count 
      FROM "forum-posts" 
      GROUP BY source, subreddit 
      ORDER BY count DESC
    `);
    
    console.log('\n📊 Final post distribution:');
    finalStats.rows.forEach(row => {
      console.log(`  ${row.subreddit || 'unknown'} (${row.source}): ${row.count} posts`);
    });
    
    client.release();
    console.log('\n✅ Cleanup completed successfully!');
    
  } catch (error) {
    console.error('❌ Error cleaning up duplicates:', error.message);
  }
}

// Run the cleanup
if (require.main === module) {
  cleanupDuplicates().then(() => {
    console.log('Cleanup finished');
    process.exit(0);
  }).catch(error => {
    console.error('Cleanup failed:', error);
    process.exit(1);
  });
}

module.exports = { cleanupDuplicates };