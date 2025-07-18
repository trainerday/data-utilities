require('dotenv').config();

// Manually run TrainerRoad comment fetching exactly like the scraper does
async function manualTRComments() {
  console.log('Manually running TrainerRoad comment fetching...\n');
  
  try {
    const { getPostsNeedingComments, saveCommentsForPost } = require('../db.js');
    const axios = require('axios');
    
    // Get posts needing comments
    const postsNeedingComments = await getPostsNeedingComments();
    const trainerRoadPosts = postsNeedingComments.filter(p => p.subreddit === 'trainerroad');
    
    console.log(`Found ${trainerRoadPosts.length} TrainerRoad posts needing comments`);
    
    if (trainerRoadPosts.length > 0) {
      const headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json'
      };
      
      // Test with just one post first
      const testPost = trainerRoadPosts.find(p => p.num_comments > 5); // Get one with several comments
      if (!testPost) {
        console.log('No TrainerRoad posts with 5+ comments found');
        return;
      }
      
      console.log(`Testing with: "${testPost.title}" (ID: ${testPost.id}, ${testPost.num_comments} comments)`);
      
      // Copy the fetchDiscourseComments logic from routes/index.js
      const commentsUrl = `https://www.trainerroad.com/forum/t/${testPost.id}.json`;
      console.log(`Fetching: ${commentsUrl}`);
      
      const commentsResponse = await axios.get(commentsUrl, { headers });
      
      if (!commentsResponse.data.post_stream || !commentsResponse.data.post_stream.posts) {
        console.log('No post stream found');
        return;
      }
      
      // Skip the first post (original topic) and get comments
      const comments = commentsResponse.data.post_stream.posts.slice(1).map(post => {
        return {
          author: post.username,
          body: post.cooked ? post.cooked.replace(/<[^>]*>/g, '') : '', // Strip HTML
          score: 0, // Discourse doesn't have comment scores like Reddit
          created: new Date(post.created_at)
        };
      }).filter(comment => comment.body && comment.body.trim() !== '');
      
      console.log(`Extracted ${comments.length} comments`);
      
      if (comments.length > 0) {
        console.log('Sample comment:', {
          author: comments[0].author,
          body: comments[0].body.substring(0, 100) + '...',
          created: comments[0].created
        });
        
        console.log('\\nAttempting to save comments...');
        
        // Try to save without using saveCommentsForPost first
        console.log('Database configuration check...');
        console.log('DB_HOST:', process.env.DB_HOST ? 'SET' : 'NOT SET');
        console.log('DB_SSL_CERT:', process.env.DB_SSL_CERT ? 'SET (length: ' + process.env.DB_SSL_CERT.length + ')' : 'NOT SET');
        
        // Use the exact same method as the scraper
        await saveCommentsForPost(testPost.id, comments);
        console.log('✅ Comments saved successfully!');
        
      } else {
        console.log('No valid comments found after filtering');
      }
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    console.error('Stack:', error.stack);
  }
}

manualTRComments();