const axios = require('axios');

// Check what's actually available on TrainerRoad right now
async function checkLatestTrainerRoad() {
  console.log('Checking current TrainerRoad forum for latest posts...\n');
  
  const headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9'
  };

  try {
    const response = await axios.get('https://www.trainerroad.com/forum/latest.json?limit=10', { headers });
    const topics = response.data.topic_list.topics;
    
    console.log(`Found ${topics.length} latest topics on TrainerRoad:`);
    console.log('');
    
    topics.forEach((topic, index) => {
      const createdDate = new Date(topic.created_at);
      const hoursAgo = (Date.now() - createdDate.getTime()) / (1000 * 60 * 60);
      
      console.log(`${index + 1}. "${topic.title}"`);
      console.log(`   ID: ${topic.id}`);
      console.log(`   Created: ${createdDate.toISOString()} (${hoursAgo.toFixed(1)} hours ago)`);
      console.log(`   Posts: ${topic.posts_count}, Likes: ${topic.like_count || 0}`);
      console.log('');
    });
    
    // Check if any are very recent (less than 6 hours old)
    const recentTopics = topics.filter(topic => {
      const hoursAgo = (Date.now() - new Date(topic.created_at).getTime()) / (1000 * 60 * 60);
      return hoursAgo < 6;
    });
    
    if (recentTopics.length > 0) {
      console.log(`🔥 Found ${recentTopics.length} topics created in the last 6 hours:`);
      recentTopics.forEach(topic => {
        const hoursAgo = (Date.now() - new Date(topic.created_at).getTime()) / (1000 * 60 * 60);
        console.log(`   - "${topic.title}" (${hoursAgo.toFixed(1)}h ago)`);
      });
    } else {
      console.log('ℹ️  No topics created in the last 6 hours. Forum activity might be slow today.');
    }
    
  } catch (error) {
    console.error('Error fetching TrainerRoad data:', error.message);
  }
}

checkLatestTrainerRoad();