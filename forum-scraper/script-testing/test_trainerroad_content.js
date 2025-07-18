const axios = require('axios');

// Simple test script to verify TrainerRoad content extraction
async function testTrainerRoadContent() {
  console.log('Testing TrainerRoad content extraction...\n');
  
  const headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9'
  };

  try {
    // Test 1: Get topics list
    console.log('1. Fetching topics list...');
    const topicsResponse = await axios.get('https://www.trainerroad.com/forum/latest.json?limit=5', { headers });
    const topics = topicsResponse.data.topic_list.topics;
    console.log(`Found ${topics.length} topics\n`);

    // Test 2: Get individual topic content
    const testTopic = topics[0];
    console.log(`2. Testing topic: "${testTopic.title}"`);
    console.log(`   Topic ID: ${testTopic.id}`);
    console.log(`   Excerpt: "${testTopic.excerpt || 'No excerpt'}"`);
    
    const topicUrl = `https://www.trainerroad.com/forum/t/${testTopic.id}.json`;
    console.log(`   Fetching from: ${topicUrl}`);
    
    const topicResponse = await axios.get(topicUrl, { headers });
    const firstPost = topicResponse.data.post_stream?.posts?.[0];
    
    if (firstPost) {
      const content = firstPost.cooked ? firstPost.cooked.replace(/<[^>]*>/g, '').trim() : '';
      console.log(`   Author: ${firstPost.username}`);
      console.log(`   Content length: ${content.length} characters`);
      console.log(`   Content preview: "${content.substring(0, 200)}${content.length > 200 ? '...' : ''}"`);
    } else {
      console.log('   No content found in first post');
    }

    console.log('\n✅ TrainerRoad content extraction test completed successfully!');
    
  } catch (error) {
    console.error('❌ Error testing TrainerRoad content:', error.message);
    if (error.response) {
      console.error(`   Status: ${error.response.status}`);
      console.error(`   Response: ${JSON.stringify(error.response.data)}`);
    }
  }
}

// Run the test
testTrainerRoadContent();