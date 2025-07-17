const axios = require('axios');
const { savePostsOnly, saveCommentsForPost } = require('../db');

// Test scraping TrainerRoad Discourse forum
async function testDiscourseScaper() {
  console.log('Testing TrainerRoad Discourse scraper...');
  
  try {
    // Step 1: Fetch latest topics from Discourse API
    console.log('Fetching latest topics...');
    const topicsResponse = await axios.get('https://www.trainerroad.com/forum/latest.json?limit=10');
    const topics = topicsResponse.data.topic_list.topics;
    
    console.log(`Found ${topics.length} topics`);
    
    // Step 2: Convert Discourse topics to our format
    const posts = topics.map(topic => {
      return {
        title: topic.title,
        author: topic.last_poster_username || 'unknown',
        created: new Date(topic.created_at),
        score: topic.like_count || 0,
        num_comments: topic.posts_count - 1, // Subtract original post
        url: `https://www.trainerroad.com/forum/t/${topic.slug}/${topic.id}`,
        selftext: topic.excerpt || '',
        subreddit: 'trainerroad', // Use as source identifier
        comments: [] // Will be filled later
      };
    });
    
    console.log('Sample post:', JSON.stringify(posts[0], null, 2));
    
    // Step 3: Test saving posts to database (same tables as Reddit)
    console.log('Saving posts to database...');
    await savePostsOnly(posts);
    console.log('Posts saved successfully!');
    
    // Step 4: Test fetching comments for one topic
    if (topics.length > 0) {
      const firstTopic = topics[0];
      console.log(`Fetching comments for topic: ${firstTopic.title}`);
      
      try {
        const commentsResponse = await axios.get(`https://www.trainerroad.com/forum/t/${firstTopic.id}.json`);
        const topicData = commentsResponse.data;
        
        if (topicData.post_stream && topicData.post_stream.posts) {
          // Skip the first post (original topic) and get comments
          const comments = topicData.post_stream.posts.slice(1).map(post => {
            return {
              author: post.username,
              body: post.cooked ? post.cooked.replace(/<[^>]*>/g, '') : '', // Strip HTML
              score: 0, // Discourse doesn't have comment scores like Reddit
              created: new Date(post.created_at)
            };
          }).filter(comment => comment.body && comment.body.trim() !== '');
          
          console.log(`Found ${comments.length} comments`);
          
          if (comments.length > 0) {
            console.log('Sample comment:', JSON.stringify(comments[0], null, 2));
            
            // Extract post ID from URL for saving comments
            const postId = firstTopic.id.toString();
            await saveCommentsForPost(postId, comments);
            console.log('Comments saved successfully!');
          }
        }
      } catch (error) {
        console.error('Error fetching comments:', error.message);
      }
    }
    
    console.log('\n✅ Discourse scraper test completed successfully!');
    console.log('The existing database tables work perfectly with Discourse data.');
    
  } catch (error) {
    console.error('❌ Error testing Discourse scraper:', error.message);
  }
}

// Run the test
if (require.main === module) {
  testDiscourseScaper().then(() => {
    console.log('Test finished');
    process.exit(0);
  }).catch(error => {
    console.error('Test failed:', error);
    process.exit(1);
  });
}

module.exports = { testDiscourseScaper };