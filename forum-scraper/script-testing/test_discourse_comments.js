const axios = require('axios');

// Test TrainerRoad comment fetching
async function testDiscourseComments() {
  console.log('Testing TrainerRoad comment fetching...\n');
  
  const headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9'
  };

  // Test with a known post that has comments (104553 has 10 comments)
  const topicId = '104553';
  console.log(`Testing topic ID: ${topicId}`);
  
  try {
    const commentsUrl = `https://www.trainerroad.com/forum/t/${topicId}.json`;
    console.log(`Fetching: ${commentsUrl}`);
    
    const response = await axios.get(commentsUrl, { headers });
    
    console.log(`Response status: ${response.status}`);
    console.log(`Post stream exists: ${!!response.data.post_stream}`);
    console.log(`Posts array length: ${response.data.post_stream?.posts?.length || 0}`);
    
    if (response.data.post_stream && response.data.post_stream.posts) {
      const allPosts = response.data.post_stream.posts;
      console.log(`\nAll posts in stream: ${allPosts.length}`);
      
      // Skip the first post (original topic) and get comments
      const commentPosts = allPosts.slice(1);
      console.log(`Comment posts (excluding OP): ${commentPosts.length}`);
      
      commentPosts.forEach((post, index) => {
        const content = post.cooked ? post.cooked.replace(/<[^>]*>/g, '').trim() : '';
        console.log(`\nComment ${index + 1}:`);
        console.log(`  Author: ${post.username}`);
        console.log(`  Created: ${post.created_at}`);
        console.log(`  Content: "${content.substring(0, 100)}${content.length > 100 ? '...' : ''}"`);
      });
      
      // Test the actual function logic
      const comments = commentPosts.map(post => {
        return {
          author: post.username,
          body: post.cooked ? post.cooked.replace(/<[^>]*>/g, '') : '',
          score: 0,
          created: new Date(post.created_at)
        };
      }).filter(comment => comment.body && comment.body.trim() !== '');
      
      console.log(`\nFiltered comments: ${comments.length}`);
      
    } else {
      console.log('No post stream found');
    }
    
  } catch (error) {
    console.error('Error:', error.message);
    if (error.response) {
      console.error(`Status: ${error.response.status}`);
      console.error(`Data:`, error.response.data);
    }
  }
}

testDiscourseComments();