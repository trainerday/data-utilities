require('dotenv').config();

// Test fetching TrainerRoad comments using the actual scraper functions
async function testFetchTRComments() {
  console.log('Testing TrainerRoad comment fetching with actual functions...\n');
  
  const { getPostsNeedingComments, saveCommentsForPost } = require('../db.js');
  const axios = require('axios');
  
  // Copy the fetchDiscourseComments function from routes/index.js
  async function fetchDiscourseComments(topicId, headers) {
    const commentsUrl = `https://www.trainerroad.com/forum/t/${topicId}.json`;
    console.log(`Fetching comments from: ${commentsUrl}`);
    
    const response = await axios.get(commentsUrl, { headers });
    
    if (!response.data.post_stream || !response.data.post_stream.posts) {
      return [];
    }
    
    // Skip the first post (original topic) and get comments
    const comments = response.data.post_stream.posts.slice(1).map(post => {
      return {
        author: post.username,
        body: post.cooked ? post.cooked.replace(/<[^>]*>/g, '') : '', // Strip HTML
        score: 0, // Discourse doesn't have comment scores like Reddit
        created: new Date(post.created_at)
      };
    }).filter(comment => comment.body && comment.body.trim() !== '');
    
    return comments;
  }
  
  try {
    // Get posts needing comments
    console.log('1. Getting posts needing comments...');
    const postsNeedingComments = await getPostsNeedingComments();
    const trainerRoadPosts = postsNeedingComments.filter(p => p.subreddit === 'trainerroad');
    
    console.log(`   Found ${postsNeedingComments.length} total posts needing comments`);
    console.log(`   Found ${trainerRoadPosts.length} TrainerRoad posts needing comments`);
    
    if (trainerRoadPosts.length > 0) {
      console.log('\\nTrainerRoad posts needing comments:');
      trainerRoadPosts.forEach(post => {
        console.log(`   - "${post.title}" (ID: ${post.id}, Comments: ${post.num_comments})`);
      });
      
      // Test fetching comments for the first TrainerRoad post
      const testPost = trainerRoadPosts[0];
      console.log(`\\n2. Testing comment fetch for post ID: ${testPost.id}`);
      
      const headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json'
      };
      
      const comments = await fetchDiscourseComments(testPost.id, headers);
      console.log(`   Fetched ${comments.length} comments`);
      
      if (comments.length > 0) {
        console.log('   Sample comment:', comments[0]);
        
        console.log('\\n3. Saving comments to database...');
        await saveCommentsForPost(testPost.id, comments);
        console.log('   ✅ Comments saved successfully');
      } else {
        console.log('   ❌ No comments found');
      }
    } else {
      console.log('\\n❌ No TrainerRoad posts found that need comments');
    }
    
  } catch (error) {
    console.error('❌ Error:', error);
  }
}

testFetchTRComments();