var express = require('express');
var axios = require('axios');
var { savePosts, savePostsOnly, saveCommentsForPost, getPostsForDay, hasRecentData, getPostsNeedingComments, getHotPostsNeedingEarlyComments, logRequest, getRequestLogs, getRequestStats, updatePostResponseStatus } = require('../db');
var router = express.Router();

// Console logging function
function logToConsole(type, url, duration, success, error = null, statusCode = null) {
  const timestamp = new Date().toISOString();
  const status = success ? 'SUCCESS' : 'ERROR';
  const errorMsg = error ? ` | Error: ${error}` : '';
  const statusMsg = statusCode ? ` | Status: ${statusCode}` : '';
  
  console.log(`[${timestamp}] ${type} | ${status} | ${duration}ms | ${url}${statusMsg}${errorMsg}`);
}

// Enhanced axios request with logging
async function makeRedditRequest(url, headers, requestType = 'REDDIT') {
  const startTime = Date.now();
  try {
    const response = await axios.get(url, { headers });
    const duration = Date.now() - startTime;
    
    // Log to both console and database
    logToConsole(requestType, url, duration, true, null, response.status);
    await logRequest(requestType, url, duration, true, response.status, null);
    
    return response;
  } catch (error) {
    const duration = Date.now() - startTime;
    const statusCode = error.response?.status;
    const errorMsg = error.response?.data?.message || error.message;
    
    // Log to both console and database
    logToConsole(requestType, url, duration, false, errorMsg, statusCode);
    await logRequest(requestType, url, duration, false, statusCode, errorMsg);
    
    throw error;
  }
}

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'Express' });
});

// Helper function to fetch just post data (no comments)
async function fetchSubredditPosts(subreddit, headers) {
  console.log(`Fetching new posts from r/${subreddit}...`);
  
  // Get today's posts from subreddit
  const postsResponse = await makeRedditRequest(`https://www.reddit.com/r/${subreddit}.json?t=day&limit=25`, headers, 'POSTS');
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

// Helper function to fetch comments for a specific post
async function fetchPostComments(postId, subreddit, headers) {
  const commentsUrl = `https://www.reddit.com/r/${subreddit}/comments/${postId}.json`;
  const commentsResponse = await makeRedditRequest(commentsUrl, headers, 'COMMENTS');
  
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

// Helper function to fetch subreddit data (legacy - with comments)
async function fetchSubredditData(subreddit, headers) {
  console.log(`Fetching fresh data from r/${subreddit}...`);
  
  // Get today's posts from subreddit
  const postsResponse = await makeRedditRequest(`https://www.reddit.com/r/${subreddit}.json?t=day&limit=25`, headers, 'POSTS');
  const redditPosts = postsResponse.data.data.children;

  // Get comments for each post with delay to avoid rate limiting
  const postsWithComments = [];
  for (let i = 0; i < Math.min(redditPosts.length, 10); i++) {
    const post = redditPosts[i];
    try {
      const postData = post.data;
      const commentsUrl = `https://www.reddit.com/r/${subreddit}/comments/${postData.id}.json`;
      
      // Add delay between requests (except for first one)
      if (i > 0) {
        await new Promise(resolve => setTimeout(resolve, 500)); // 500ms delay
      }
      
      const commentsResponse = await makeRedditRequest(commentsUrl, headers, 'COMMENTS');
        
      const comments = commentsResponse.data[1]?.data?.children || [];
      
      postsWithComments.push({
        title: postData.title,
        author: postData.author,
        created: new Date(postData.created_utc * 1000),
        score: postData.score,
        num_comments: postData.num_comments,
        url: `https://reddit.com${postData.permalink}`,
        selftext: postData.selftext,
        subreddit: subreddit,
        comments: comments.map(comment => {
          const commentData = comment.data;
          return {
            author: commentData.author,
            body: commentData.body,
            score: commentData.score,
            created: new Date(commentData.created_utc * 1000)
          };
        }).filter(comment => comment.body && comment.body !== '[deleted]')
      });
    } catch (error) {
      console.error(`Error fetching comments for post ${post.data.id}:`, error.message);
      postsWithComments.push({
        title: post.data.title,
        author: post.data.author,
        created: new Date(post.data.created_utc * 1000),
        score: post.data.score,
        num_comments: post.data.num_comments,
        url: `https://reddit.com${post.data.permalink}`,
        selftext: post.data.selftext,
        subreddit: subreddit,
        comments: []
      });
    }
  }
  
  return postsWithComments;
}

/* GET Reddit cycling data - READ ONLY from database */
router.get('/reddit', async function(req, res, next) {
  try {
    // Just return data from database - no fetching
    const posts = await getPostsForDay();

    res.render('reddit', { 
      title: 'r/cycling + r/Velo - Today\'s Posts', 
      posts: posts,
      fetchTime: new Date(),
      dataSource: 'database',
      newPosts: 0,
      commentsProcessed: 0
    });

  } catch (error) {
    console.error('Error displaying Reddit data:', error.message);
    res.status(500).render('error', { 
      message: 'Failed to display Reddit data',
      error: error 
    });
  }
});

/* API endpoint for automated scraping - POST /api/scrape */
router.post('/api/scrape', async function(req, res, next) {
  try {
    let newPostsFound = 0;
    let commentsProcessed = 0;
    let hotPostsFound = 0;
    
    console.log(`[${new Date().toISOString()}] Starting automated scrape...`);
    
    // Check if we should fetch new posts (every 15 minutes)
    const hasRecent = await hasRecentData();
    
    if (!hasRecent) {
      console.log('Time to check for new posts...');
      
      const headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; RedditBot/1.0)',
        'Accept': 'application/json'
      };

      // Step 1: Fetch new posts (without comments) from both subreddits
      const [cyclingPosts, veloPosts] = await Promise.all([
        fetchSubredditPosts('cycling', headers),
        fetchSubredditPosts('Velo', headers)
      ]);

      // Combine and save new posts only
      const allNewPosts = [...cyclingPosts, ...veloPosts];
      await savePostsOnly(allNewPosts);
      newPostsFound = allNewPosts.length;
      console.log(`Saved ${newPostsFound} new posts (without comments)`);
    }

    // Step 2a: Check for HOT posts (15+ comments, 15-60 min old) that need early comment fetch
    const hotPosts = await getHotPostsNeedingEarlyComments();
    hotPostsFound = hotPosts.length;
    
    if (hotPosts.length > 0) {
      console.log(`Found ${hotPosts.length} HOT posts needing early comment fetch...`);
      
      const headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; RedditBot/1.0)',
        'Accept': 'application/json'
      };

      // Fetch comments for hot posts first (priority)
      for (const post of hotPosts.slice(0, 3)) { // Limit to 3 hot posts
        try {
          // Add delay between requests
          if (commentsProcessed > 0) {
            await new Promise(resolve => setTimeout(resolve, 500)); // 500ms delay
          }
          
          const comments = await fetchPostComments(post.id, post.subreddit, headers);
          await saveCommentsForPost(post.id, comments);
          commentsProcessed++;
          console.log(`🔥 HOT POST: Fetched ${comments.length} comments for "${post.title.substring(0, 50)}..." (${post.num_comments} total comments)`);
        } catch (error) {
          console.error(`Error fetching comments for hot post ${post.id}:`, error.message);
        }
      }
    }

    // Step 2b: Check for regular posts that need comments (1+ hours old, no comments yet)
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
          // Add delay between requests
          if (commentsProcessed > 0) {
            await new Promise(resolve => setTimeout(resolve, 500)); // 500ms delay
          }
          
          const comments = await fetchPostComments(post.id, post.subreddit, headers);
          await saveCommentsForPost(post.id, comments);
          commentsProcessed++;
          console.log(`Fetched ${comments.length} comments for post ${post.id}`);
        } catch (error) {
          console.error(`Error fetching comments for post ${post.id}:`, error.message);
        }
      }
    }

    // Return scrape results as JSON
    res.json({
      success: true,
      timestamp: new Date().toISOString(),
      results: {
        newPostsFound,
        hotPostsFound,
        commentsProcessed,
        postsNeedingComments: postsNeedingComments.length
      }
    });

  } catch (error) {
    console.error('Error in automated scrape:', error.message);
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

/* Force refresh Reddit data - just triggers the scrape API */
router.get('/reddit/refresh', async function(req, res, next) {
  try {
    console.log('Force refresh triggered - running scrape...');
    
    const headers = {
      'User-Agent': 'Mozilla/5.0 (compatible; RedditBot/1.0)',
      'Accept': 'application/json'
    };

    // Just fetch new posts (no comments) - much faster
    const [cyclingPosts, veloPosts] = await Promise.all([
      fetchSubredditPosts('cycling', headers),
      fetchSubredditPosts('Velo', headers)
    ]);

    // Save posts only (no comments)
    const allNewPosts = [...cyclingPosts, ...veloPosts];
    await savePostsOnly(allNewPosts);
    
    console.log(`Force refresh: Saved ${allNewPosts.length} posts (without comments)`);
    
    res.redirect('/reddit');

  } catch (error) {
    console.error('Error in force refresh:', error.message);
    res.status(500).render('error', { 
      message: 'Failed to refresh Reddit data',
      error: error 
    });
  }
});

/* GET request logs */
router.get('/logs', async function(req, res, next) {
  try {
    const logs = await getRequestLogs(200); // Get last 200 requests
    const stats = await getRequestStats();
    
    res.render('logs', { 
      title: 'Reddit API Request Logs',
      logs: logs,
      stats: stats
    });
  } catch (error) {
    console.error('Error fetching logs:', error.message);
    res.status(500).render('error', { 
      message: 'Failed to fetch request logs',
      error: error 
    });
  }
});

/* API endpoint to update post response status */
router.post('/api/update-response-status', async function(req, res, next) {
  try {
    const { postId, responded } = req.body;
    
    if (!postId || typeof responded !== 'boolean') {
      return res.status(400).json({ 
        success: false, 
        error: 'postId and responded (boolean) are required' 
      });
    }
    
    await updatePostResponseStatus(postId, responded);
    
    res.json({
      success: true,
      postId: postId,
      responded: responded
    });
    
  } catch (error) {
    console.error('Error updating response status:', error.message);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router;
