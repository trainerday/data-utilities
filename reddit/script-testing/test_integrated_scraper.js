const axios = require('axios');
const { savePostsOnly, saveCommentsForPost, hasRecentData } = require('../db');

// Import the functions we created
async function makeRequest(url, headers, requestType = 'REQUEST') {
  const startTime = Date.now();
  try {
    const response = await axios.get(url, { headers });
    const duration = Date.now() - startTime;
    console.log(`[${requestType}] ${url} - ${duration}ms - SUCCESS`);
    return response;
  } catch (error) {
    const duration = Date.now() - startTime;
    const statusCode = error.response?.status;
    const errorMsg = error.response?.data?.message || error.message;
    console.log(`[${requestType}] ${url} - ${duration}ms - ERROR: ${errorMsg}`);
    throw error;
  }
}

// Helper function to fetch just post data (no comments)
async function fetchSubredditPosts(subreddit, headers) {
  console.log(`Fetching new posts from r/${subreddit}...`);
  
  // Get today's posts from subreddit
  const postsResponse = await makeRequest(`https://www.reddit.com/r/${subreddit}.json?t=day&limit=25`, headers, 'POSTS');
  const redditPosts = postsResponse.data.data.children;

  // Just return post data without comments
  const posts = redditPosts.map(post => {
    const postData = post.data;
    return {
      title: postData.title,
      author: postData.author,
      created: new Date(postData.created_utc * 1000),
      score: postData.score,
      num_comments: postData.num_comments,
      url: `https://reddit.com${postData.permalink}`,
      selftext: postData.selftext,
      subreddit: subreddit,
      comments: [] // No comments initially
    };
  });
  
  return posts;
}

// Helper function to fetch Discourse forum posts
async function fetchDiscourseTopics() {
  console.log('Fetching new topics from TrainerRoad Discourse forum...');
  
  const headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; ForumBot/1.0)',
    'Accept': 'application/json'
  };
  
  // Get latest topics from Discourse
  const topicsResponse = await makeRequest('https://www.trainerroad.com/forum/latest.json?limit=25', headers, 'DISCOURSE');
  const topics = topicsResponse.data.topic_list.topics;

  // Convert to our post format
  const posts = topics.map(topic => {
    return {
      title: topic.title,
      author: topic.last_poster_username || 'unknown',
      created: new Date(topic.created_at),
      score: topic.like_count || 0,
      num_comments: Math.max(0, topic.posts_count - 1), // Subtract original post
      url: `https://www.trainerroad.com/forum/t/${topic.slug}/${topic.id}`,
      selftext: topic.excerpt || '',
      subreddit: 'trainerroad',
      comments: [] // No comments initially
    };
  });
  
  return posts;
}

// Test the integrated scraper
async function testIntegratedScraper() {
  console.log('Testing integrated Reddit + Discourse scraper...');
  
  try {
    let newPostsFound = 0;
    
    console.log(`[${new Date().toISOString()}] Starting automated scrape...`);
    
    // Force fetch for testing (bypass 15-minute check)
    const hasRecent = false; // await hasRecentData();
    
    if (!hasRecent) {
      console.log('Time to check for new posts...');
      
      const headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; RedditBot/1.0)',
        'Accept': 'application/json'
      };

      // Step 1: Fetch new posts from Reddit subreddits and Discourse forum
      const [cyclingPosts, veloPosts, discoursePosts] = await Promise.all([
        fetchSubredditPosts('cycling', headers),
        fetchSubredditPosts('Velo', headers),
        fetchDiscourseTopics()
      ]);

      // Combine and save new posts only
      const allNewPosts = [...cyclingPosts, ...veloPosts, ...discoursePosts];
      await savePostsOnly(allNewPosts);
      newPostsFound = allNewPosts.length;
      console.log(`Saved ${newPostsFound} new posts (without comments)`);
      
      // Show breakdown
      console.log(`  - r/cycling: ${cyclingPosts.length} posts`);
      console.log(`  - r/Velo: ${veloPosts.length} posts`);
      console.log(`  - TrainerRoad Discourse: ${discoursePosts.length} posts`);
    }

    console.log('\n✅ Integrated scraper test completed successfully!');
    console.log('Both Reddit and Discourse data are now being scraped into the same database tables.');
    
  } catch (error) {
    console.error('❌ Error testing integrated scraper:', error.message);
  }
}

// Run the test
if (require.main === module) {
  testIntegratedScraper().then(() => {
    console.log('Test finished');
    process.exit(0);
  }).catch(error => {
    console.error('Test failed:', error);
    process.exit(1);
  });
}

module.exports = { testIntegratedScraper };