require('dotenv').config();

// Debug script to test discourse data insertion
async function debugDiscourseInsert() {
  console.log('🔍 Debugging TrainerRoad discourse insertion...\n');
  
  // Import the functions we need
  const { savePostsOnly, getPostsForDay } = require('../db.js');
  
  try {
    // Test the fetchDiscourseTopics function by copying the logic
    const axios = require('axios');
    
    const userAgents = [
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ];
    const randomUserAgent = userAgents[Math.floor(Math.random() * userAgents.length)];
    
    const headers = {
      'User-Agent': randomUserAgent,
      'Accept': 'application/json',
      'Accept-Language': 'en-US,en;q=0.9',
      'Accept-Encoding': 'gzip, deflate, br',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1'
    };
    
    // Get latest topics from Discourse
    console.log('1. Fetching topics from TrainerRoad...');
    const topicsResponse = await axios.get('https://www.trainerroad.com/forum/latest.json?limit=5', { headers });
    const topics = topicsResponse.data.topic_list.topics;
    console.log(`   Found ${topics.length} topics`);

    const posts = [];
    
    // Fetch individual topic content for each topic
    for (let i = 0; i < topics.length; i++) {
      const topic = topics[i];
      console.log(`\n2. Processing topic ${i + 1}: "${topic.title}" (ID: ${topic.id})`);
      
      try {
        // Add delay between requests (except for first one)
        if (i > 0) {
          await new Promise(resolve => setTimeout(resolve, 500)); // 500ms delay
        }
        
        // Fetch individual topic to get the first post content
        const topicUrl = `https://www.trainerroad.com/forum/t/${topic.id}.json`;
        const topicResponse = await axios.get(topicUrl, { headers });
        
        // Get the first post content (original post)
        const firstPost = topicResponse.data.post_stream?.posts?.[0];
        const content = firstPost?.cooked ? firstPost.cooked.replace(/<[^>]*>/g, '').trim() : (topic.excerpt || '');
        
        console.log(`   Content length: ${content.length} characters`);
        console.log(`   Content preview: "${content.substring(0, 100)}${content.length > 100 ? '...' : ''}"`);
        
        const post = {
          title: topic.title,
          author: firstPost?.username || topic.last_poster_username || 'unknown',
          created: new Date(topic.created_at),
          score: topic.like_count || 0,
          num_comments: Math.max(0, topic.posts_count - 1), // Subtract original post
          url: `https://www.trainerroad.com/forum/t/${topic.slug}/${topic.id}`,
          selftext: content,
          subreddit: 'trainerroad'
        };
        
        posts.push(post);
        
        // Check if this is our target post
        if (topic.id === 104573) {
          console.log(`   🎯 FOUND TARGET POST 104573!`);
          console.log(`   Full content: "${content}"`);
        }
        
      } catch (error) {
        console.error(`   ❌ Error fetching topic ${topic.id} content:`, error.message);
        // Fallback to basic topic info without content
        posts.push({
          title: topic.title,
          author: topic.last_poster_username || 'unknown',
          created: new Date(topic.created_at),
          score: topic.like_count || 0,
          num_comments: Math.max(0, topic.posts_count - 1),
          url: `https://www.trainerroad.com/forum/t/${topic.slug}/${topic.id}`,
          selftext: topic.excerpt || '',
          subreddit: 'trainerroad'
        });
      }
    }
    
    console.log(`\n3. Saving ${posts.length} posts to database...`);
    await savePostsOnly(posts);
    console.log('   ✅ Posts saved successfully');
    
    console.log('\n4. Checking what was saved in database...');
    const savedPosts = await getPostsForDay();
    const trainerRoadPosts = savedPosts.filter(p => p.subreddit === 'trainerroad');
    
    console.log(`   Found ${trainerRoadPosts.length} TrainerRoad posts in database:`);
    trainerRoadPosts.forEach(post => {
      console.log(`   - "${post.title}" by ${post.author}`);
      console.log(`     Content: "${post.selftext?.substring(0, 100) || 'NO CONTENT'}${post.selftext?.length > 100 ? '...' : ''}"`);
      console.log(`     ID: ${post.id}, URL: ${post.url}`);
    });
    
    // Specifically check for our target post
    const targetPost = trainerRoadPosts.find(p => p.url.includes('104573'));
    if (targetPost) {
      console.log(`\n🎯 Target post 104573 found in database:`);
      console.log(`   Title: "${targetPost.title}"`);
      console.log(`   Author: ${targetPost.author}`);
      console.log(`   Content: "${targetPost.selftext}"`);
      console.log(`   Content length: ${targetPost.selftext?.length || 0} characters`);
    } else {
      console.log(`\n❌ Target post 104573 NOT found in database!`);
    }
    
  } catch (error) {
    console.error('❌ Error:', error);
  }
}

debugDiscourseInsert();