require('dotenv').config();

// Batch fetch comments for several TrainerRoad posts
async function batchFetchTRComments() {
  console.log('Batch fetching TrainerRoad comments...\n');
  
  try {
    const { getPostsNeedingComments, saveCommentsForPost } = require('../db.js');
    const axios = require('axios');
    
    // Get TrainerRoad posts needing comments
    const postsNeedingComments = await getPostsNeedingComments();
    const trainerRoadPosts = postsNeedingComments.filter(p => p.subreddit === 'trainerroad');
    
    console.log(`Found ${trainerRoadPosts.length} TrainerRoad posts needing comments`);
    
    const headers = {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Accept': 'application/json'
    };
    
    // Process first 5 posts with comments
    const postsToProcess = trainerRoadPosts.filter(p => p.num_comments > 0).slice(0, 5);
    console.log(`Processing ${postsToProcess.length} posts:`);
    
    for (const post of postsToProcess) {
      console.log(`\\n📝 "${post.title}" (${post.num_comments} comments)`);
      
      try {
        const commentsUrl = `https://www.trainerroad.com/forum/t/${post.id}.json`;
        const commentsResponse = await axios.get(commentsUrl, { headers });
        
        if (!commentsResponse.data.post_stream || !commentsResponse.data.post_stream.posts) {
          console.log('   ❌ No post stream found');
          continue;
        }
        
        const comments = commentsResponse.data.post_stream.posts.slice(1).map(post => {
          return {
            author: post.username,
            body: post.cooked ? post.cooked.replace(/<[^>]*>/g, '') : '',
            score: 0,
            created: new Date(post.created_at)
          };
        }).filter(comment => comment.body && comment.body.trim() !== '');
        
        console.log(`   Fetched ${comments.length} comments`);
        
        if (comments.length > 0) {
          await saveCommentsForPost(post.id, comments);
          console.log('   ✅ Saved to database');
        } else {
          console.log('   ⚠️ No valid comments to save');
        }
        
        // Small delay to be nice to the server
        await new Promise(resolve => setTimeout(resolve, 500));
        
      } catch (error) {
        console.log(`   ❌ Error: ${error.message}`);
      }
    }
    
    console.log('\\n🎉 Batch processing complete!');
    
  } catch (error) {
    console.error('❌ Error:', error);
  }
}

batchFetchTRComments();