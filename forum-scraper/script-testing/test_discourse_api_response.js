const axios = require('axios');

async function testDiscourseApiResponse() {
  console.log('Testing Discourse API response to understand content extraction...\n');
  
  try {
    // Test the latest topics API
    console.log('🔍 Fetching from latest.json API...');
    const topicsResponse = await axios.get('https://www.trainerroad.com/forum/latest.json?limit=5');
    const topics = topicsResponse.data.topic_list.topics;
    
    console.log(`Found ${topics.length} topics from latest.json\n`);
    
    // Examine the first topic in detail
    const firstTopic = topics[0];
    console.log('📄 First topic structure:');
    console.log('Title:', firstTopic.title);
    console.log('Excerpt:', firstTopic.excerpt || '[NONE]');
    console.log('Available fields:', Object.keys(firstTopic).sort());
    console.log('Full topic object:', JSON.stringify(firstTopic, null, 2));
    
    console.log('\n' + '='.repeat(80));
    
    // Now test the individual topic API to get the full content
    console.log(`\n🔍 Fetching individual topic ${firstTopic.id}.json to get full content...`);
    const topicResponse = await axios.get(`https://www.trainerroad.com/forum/t/${firstTopic.id}.json`);
    const topicData = topicResponse.data;
    
    console.log('Available fields in topic response:', Object.keys(topicData).sort());
    
    if (topicData.post_stream && topicData.post_stream.posts && topicData.post_stream.posts.length > 0) {
      const firstPost = topicData.post_stream.posts[0]; // The original post
      console.log('\n📄 First post (original topic content):');
      console.log('Available fields:', Object.keys(firstPost).sort());
      console.log('Raw content:', firstPost.raw ? firstPost.raw.substring(0, 200) + '...' : '[NONE]');
      console.log('Cooked content:', firstPost.cooked ? firstPost.cooked.substring(0, 200) + '...' : '[NONE]');
      console.log('Excerpt:', firstPost.excerpt || '[NONE]');
      
      // Test HTML stripping
      if (firstPost.cooked) {
        const strippedContent = firstPost.cooked.replace(/<[^>]*>/g, '');
        console.log('Stripped HTML content:', strippedContent.substring(0, 200) + '...');
      }
    }
    
    console.log('\n' + '='.repeat(80));
    
    // Check a few more topics to see the pattern
    console.log('\n🔍 Checking excerpt availability across all topics:');
    topics.forEach((topic, index) => {
      console.log(`${index + 1}. "${topic.title.substring(0, 50)}..."`);
      console.log(`   Excerpt: "${topic.excerpt || '[EMPTY]'}" (${(topic.excerpt || '').length} chars)`);
      console.log(`   Posts count: ${topic.posts_count}`);
    });
    
    console.log('\n✅ API response test completed!');
    
  } catch (error) {
    console.error('❌ Error testing Discourse API:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
  }
}

// Run the test
if (require.main === module) {
  testDiscourseApiResponse().then(() => {
    console.log('Test finished');
    process.exit(0);
  }).catch(error => {
    console.error('Test failed:', error);
    process.exit(1);
  });
}

module.exports = { testDiscourseApiResponse };