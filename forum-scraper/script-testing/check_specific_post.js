const axios = require('axios');

// Check specific TrainerRoad post for comments
async function checkSpecificPost() {
  const headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json'
  };
  
  // Check post 104571 - should have 1 comment
  const postId = '104571';
  console.log(`Checking post ${postId}...`);
  
  try {
    const response = await axios.get(`https://www.trainerroad.com/forum/t/${postId}.json`, { headers });
    
    console.log(`Total posts in stream: ${response.data.post_stream.posts.length}`);
    console.log(`First post (OP): ${response.data.post_stream.posts[0].username}`);
    
    if (response.data.post_stream.posts.length > 1) {
      console.log('\\nComments found:');
      response.data.post_stream.posts.slice(1).forEach((post, index) => {
        console.log(`Comment ${index + 1}: ${post.username} - "${post.cooked?.replace(/<[^>]*>/g, '').substring(0, 100)}..."`);
      });
    } else {
      console.log('No comments found - only the original post');
    }
    
    // Also check the reported comment count in the topic metadata
    console.log(`\\nTopic metadata:`);
    console.log(`Posts count: ${response.data.posts_count}`);
    console.log(`Participants count: ${response.data.participant_count}`);
    
  } catch (error) {
    console.error('Error:', error.message);
  }
}

checkSpecificPost();