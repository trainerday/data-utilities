#!/usr/bin/env node

require('dotenv').config();
const axios = require('axios');

// Import database functions
const { 
  savePostsOnly, 
  saveCommentsForPost, 
  hasRecentData, 
  getPostsNeedingComments, 
  getHotPostsNeedingEarlyComments 
} = require('./db');

// Enhanced axios request with logging
async function makeRequest(url, headers, requestType = 'REQUEST') {
  const startTime = Date.now();
  try {
    const response = await axios.get(url, { headers });
    const duration = Date.now() - startTime;
    
    console.log(`[${new Date().toISOString()}] ${requestType} | SUCCESS | ${duration}ms | ${url} | Status: ${response.status}`);
    
    return response;
  } catch (error) {
    const duration = Date.now() - startTime;
    const statusCode = error.response?.status;
    const errorMsg = error.response?.data?.message || error.message;
    
    console.log(`[${new Date().toISOString()}] ${requestType} | ERROR | ${duration}ms | ${url} | Status: ${statusCode} | Error: ${errorMsg}`);
    
    throw error;
  }
}

// Helper function to fetch subreddit posts
async function fetchSubredditPosts(subreddit, headers) {
  console.log(`Fetching new posts from r/${subreddit}...`);
  
  const postsResponse = await makeRequest(`https://www.reddit.com/r/${subreddit}.json?t=day&limit=25`, headers, 'POSTS');
  const redditPosts = postsResponse.data.data.children;

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
      comments: []
    };
  });
  
  return posts;
}

// Helper function to fetch TrainerRoad posts
async function fetchDiscourseTopics() {
  console.log('Fetching new topics from TrainerRoad Discourse forum...');
  
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
  
  const topicsResponse = await makeRequest('https://www.trainerroad.com/forum/latest.json?limit=25', headers, 'DISCOURSE');
  const topics = topicsResponse.data.topic_list.topics;

  const posts = [];
  
  for (let i = 0; i < topics.length; i++) {
    const topic = topics[i];
    
    try {
      if (i > 0) {
        await new Promise(resolve => setTimeout(resolve, 500));
      }
      
      const topicUrl = `https://www.trainerroad.com/forum/t/${topic.id}.json`;
      const topicResponse = await makeRequest(topicUrl, headers, 'DISCOURSE_TOPIC');
      
      const firstPost = topicResponse.data.post_stream?.posts?.[0];
      const content = firstPost?.cooked ? firstPost.cooked.replace(/<[^>]*>/g, '').trim() : (topic.excerpt || '');
      
      posts.push({
        title: topic.title,
        author: firstPost?.username || topic.last_poster_username || 'unknown',
        created: new Date(topic.created_at),
        score: topic.like_count || 0,
        num_comments: Math.max(0, topic.posts_count - 1),
        url: `https://www.trainerroad.com/forum/t/${topic.slug}/${topic.id}`,
        selftext: content,
        subreddit: 'trainerroad',
        comments: []
      });
      
    } catch (error) {
      console.error(`Error fetching topic ${topic.id} content:`, error.message);
      posts.push({
        title: topic.title,
        author: topic.last_poster_username || 'unknown',
        created: new Date(topic.created_at),
        score: topic.like_count || 0,
        num_comments: Math.max(0, topic.posts_count - 1),
        url: `https://www.trainerroad.com/forum/t/${topic.slug}/${topic.id}`,
        selftext: topic.excerpt || '',
        subreddit: 'trainerroad',
        comments: []
      });
    }
  }
  
  console.log(`Fetched ${posts.length} TrainerRoad topics with content`);
  return posts;
}

// Helper function to fetch comments for Reddit posts
async function fetchPostComments(postId, subreddit, headers) {
  const commentsUrl = `https://www.reddit.com/r/${subreddit}/comments/${postId}.json`;
  const commentsResponse = await makeRequest(commentsUrl, headers, 'COMMENTS');
  
  const comments = commentsResponse.data[1]?.data?.children || [];
  
  return comments.map(comment => {
    const commentData = comment.data;
    return {
      author: commentData.author,
      body: commentData.body,
      score: commentData.score,
      created: new Date(commentData.created_utc * 1000)
    };
  }).filter(comment => comment.body && comment.body !== '[deleted]');
}

// Helper function to fetch comments for TrainerRoad posts
async function fetchDiscourseComments(topicId, headers) {
  const commentsUrl = `https://www.trainerroad.com/forum/t/${topicId}.json`;
  const commentsResponse = await makeRequest(commentsUrl, headers, 'DISCOURSE_COMMENTS');
  
  if (!commentsResponse.data.post_stream || !commentsResponse.data.post_stream.posts) {
    return [];
  }
  
  const comments = commentsResponse.data.post_stream.posts.slice(1).map(post => {
    return {
      author: post.username,
      body: post.cooked ? post.cooked.replace(/<[^>]*>/g, '') : '',
      score: 0,
      created: new Date(post.created_at)
    };
  }).filter(comment => comment.body && comment.body.trim() !== '');
  
  return comments;
}

// Main refresh function
async function runRefresh() {
  try {
    let newPostsFound = 0;
    let commentsProcessed = 0;
    let hotPostsFound = 0;
    
    console.log(`[${new Date().toISOString()}] Starting automated scrape...`);
    
    // Check if we should fetch new posts (every 15 minutes)
    const hasRecent = await hasRecentData();
    
    if (!hasRecent) {
      console.log('Time to check for new posts...');
      
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

      // Fetch new posts from Reddit subreddits and Discourse forum
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
    }

    // Check for HOT posts (15+ comments, 15-60 min old) that need early comment fetch
    const hotPosts = await getHotPostsNeedingEarlyComments();
    hotPostsFound = hotPosts.length;
    
    if (hotPosts.length > 0) {
      console.log(`Found ${hotPosts.length} HOT posts needing early comment fetch...`);
      
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

      // Fetch comments for hot posts first (priority)
      for (const post of hotPosts.slice(0, 3)) {
        try {
          if (commentsProcessed > 0) {
            await new Promise(resolve => setTimeout(resolve, 500));
          }
          
          let comments;
          if (post.subreddit === 'trainerroad') {
            comments = await fetchDiscourseComments(post.id, headers);
          } else {
            comments = await fetchPostComments(post.id, post.subreddit, headers);
          }
          await saveCommentsForPost(post.id, comments);
          commentsProcessed++;
          console.log(`🔥 HOT POST: Fetched ${comments.length} comments for "${post.title.substring(0, 50)}..." (${post.num_comments} total comments)`);
        } catch (error) {
          console.error(`Error fetching comments for hot post ${post.id}:`, error.message);
        }
      }
    }

    // Check for regular posts that need comments (1+ hours old, no comments yet)
    const postsNeedingComments = await getPostsNeedingComments();
    
    if (postsNeedingComments.length > 0 && commentsProcessed < 5) {
      console.log(`Found ${postsNeedingComments.length} regular posts needing comment fetch...`);
      
      const headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; RedditBot/1.0)',
        'Accept': 'application/json'
      };

      // Fetch comments for regular posts (remaining quota)
      const remainingQuota = 5 - commentsProcessed;
      for (const post of postsNeedingComments.slice(0, remainingQuota)) {
        try {
          if (commentsProcessed > 0) {
            await new Promise(resolve => setTimeout(resolve, 500));
          }
          
          let comments;
          if (post.subreddit === 'trainerroad') {
            comments = await fetchDiscourseComments(post.id, headers);
          } else {
            comments = await fetchPostComments(post.id, post.subreddit, headers);
          }
          await saveCommentsForPost(post.id, comments);
          commentsProcessed++;
          console.log(`Fetched ${comments.length} comments for post ${post.id}`);
        } catch (error) {
          console.error(`Error fetching comments for post ${post.id}:`, error.message);
        }
      }
    }

    // Log results
    console.log(`[${new Date().toISOString()}] Scrape completed successfully:`);
    console.log(`  - New posts found: ${newPostsFound}`);
    console.log(`  - Hot posts found: ${hotPostsFound}`);
    console.log(`  - Comments processed: ${commentsProcessed}`);
    console.log(`  - Posts needing comments: ${postsNeedingComments.length}`);

  } catch (error) {
    console.error(`[${new Date().toISOString()}] Error in automated scrape:`, error.message);
    process.exit(1);
  }
}

// Run the refresh
if (require.main === module) {
  runRefresh().then(() => {
    console.log(`[${new Date().toISOString()}] Refresh completed, exiting.`);
    process.exit(0);
  }).catch(error => {
    console.error(`[${new Date().toISOString()}] Fatal error:`, error);
    process.exit(1);
  });
}