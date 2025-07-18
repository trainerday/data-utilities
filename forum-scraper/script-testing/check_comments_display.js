require('dotenv').config();

// Test script to check if comments are properly loaded for display
async function checkCommentsDisplay() {
  console.log('🔍 Checking comments display...\\n');
  
  const { getPostsForDay } = require('../db.js');
  
  try {
    const posts = await getPostsForDay();
    
    console.log(`Found ${posts.length} posts for today`);
    
    // Check for posts with comments
    const postsWithComments = posts.filter(p => p.comments && p.comments.length > 0);
    
    console.log(`\\nPosts with loaded comments: ${postsWithComments.length}`);
    
    postsWithComments.forEach(post => {
      console.log(`\\n📝 "${post.title.substring(0, 50)}..."`);
      console.log(`   ID: ${post.id}`);
      console.log(`   Subreddit: ${post.subreddit}`);
      console.log(`   Comments loaded: ${post.comments.length}`);
      console.log(`   Sample comment: "${post.comments[0]?.body?.substring(0, 100) || 'No comment body'}..."`);
    });
    
    if (postsWithComments.length === 0) {
      console.log('\\n❌ No posts have comments loaded. This means comments exist in DB but aren\'t being displayed.');
    } else {
      console.log('\\n✅ Comments are being loaded and should be displayed in the UI.');
    }
    
  } catch (error) {
    console.error('❌ Error:', error);
  }
}

checkCommentsDisplay();