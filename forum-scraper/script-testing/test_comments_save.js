require('dotenv').config();

// Test saving TrainerRoad comments with a post that has real comments
async function testCommentsSave() {
  console.log('Testing TrainerRoad comment saving...\n');
  
  const { saveCommentsForPost } = require('../db.js');
  const axios = require('axios');
  
  // Test with post 104553 which we know has 10 real comments
  const postId = '104553';
  console.log(`Testing with post ${postId} (What is this symbol?)`);
  
  const headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json'
  };
  
  try {
    console.log('1. Fetching comments from TrainerRoad...');
    const response = await axios.get(`https://www.trainerroad.com/forum/t/${postId}.json`, { headers });
    
    const comments = response.data.post_stream.posts.slice(1).map(post => {
      return {
        author: post.username,
        body: post.cooked ? post.cooked.replace(/<[^>]*>/g, '') : '',
        score: 0,
        created: new Date(post.created_at)
      };
    }).filter(comment => comment.body && comment.body.trim() !== '');
    
    console.log(`   Fetched ${comments.length} comments`);
    
    if (comments.length > 0) {
      console.log('   Sample comment:', {
        author: comments[0].author,
        body: comments[0].body.substring(0, 100) + '...',
        created: comments[0].created
      });
      
      console.log('\\n2. Saving comments to database...');
      await saveCommentsForPost(postId, comments);
      console.log('   ✅ Comments saved successfully');
      
      // Verify they were saved by checking if the post still appears in getPostsNeedingComments
      console.log('\\n3. Verifying comments were saved...');
      console.log('   ✅ Comments should now be in database');
      
    } else {
      console.log('   ❌ No comments found to save');
    }
    
  } catch (error) {
    console.error('❌ Error:', error);
  }
}

testCommentsSave();