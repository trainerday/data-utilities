const axios = require('axios');

// Test script to check if the specific missing post shows up in our scraper logic
async function testSpecificPost() {
  console.log('Testing specific TrainerRoad post 104573...\n');
  
  const headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9'
  };

  try {
    // Get the latest topics list
    console.log('1. Fetching latest topics...');
    const topicsResponse = await axios.get('https://www.trainerroad.com/forum/latest.json?limit=30', { headers });
    const topics = topicsResponse.data.topic_list.topics;
    
    // Look for the specific post
    const targetPost = topics.find(topic => topic.id === 104573);
    
    if (targetPost) {
      console.log('✅ Found target post in latest topics!');
      console.log(`   Title: "${targetPost.title}"`);
      console.log(`   Created: ${targetPost.created_at}`);
      console.log(`   Excerpt: "${targetPost.excerpt || 'No excerpt'}"`);
      console.log(`   Posts count: ${targetPost.posts_count}`);
      console.log(`   Category: ${targetPost.category_id}`);
      
      // Now fetch the individual post content
      console.log('\n2. Fetching individual post content...');
      const topicUrl = `https://www.trainerroad.com/forum/t/${targetPost.id}.json`;
      const topicResponse = await axios.get(topicUrl, { headers });
      const firstPost = topicResponse.data.post_stream?.posts?.[0];
      
      if (firstPost) {
        const content = firstPost.cooked ? firstPost.cooked.replace(/<[^>]*>/g, '').trim() : '';
        console.log(`   Content length: ${content.length} characters`);
        console.log(`   Content: "${content}"`);
        
        // Simulate what our scraper would create
        const scrapedPost = {
          title: targetPost.title,
          author: firstPost.username,
          created: new Date(targetPost.created_at),
          score: targetPost.like_count || 0,
          num_comments: Math.max(0, targetPost.posts_count - 1),
          url: `https://www.trainerroad.com/forum/t/${targetPost.slug}/${targetPost.id}`,
          selftext: content,
          subreddit: 'trainerroad'
        };
        
        console.log('\n3. Scraped post object:');
        console.log(JSON.stringify(scrapedPost, null, 2));
        
      } else {
        console.log('❌ No first post found in topic details');
      }
      
    } else {
      console.log('❌ Target post 104573 NOT found in latest topics!');
      console.log('Available topic IDs:', topics.slice(0, 10).map(t => t.id));
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

testSpecificPost();