require('dotenv').config();

// Test OpenAI categorization with sample posts
async function testOpenAICategorization() {
  console.log('Testing OpenAI categorization...\n');
  
  const PostCategorizer = require('../openai-categorizer');
  
  if (!process.env.OPENAI_API_KEY || process.env.OPENAI_API_KEY === 'your_openai_api_key_here') {
    console.error('❌ OpenAI API key not configured');
    return;
  }
  
  const categorizer = new PostCategorizer(process.env.OPENAI_API_KEY);
  
  // Test posts for all 4 categories
  const testPosts = [
    {
      title: "How to improve my FTP?",
      selftext: "I've been training for 6 months and my FTP is stuck at 250W. What training intervals should I focus on to break through this plateau?",
      subreddit: "cycling"
    },
    {
      title: "Best indoor trainer for winter training?", 
      selftext: "Looking for a smart trainer to use with Zwift during the off-season. Budget is $800. Direct drive or wheel-on?",
      subreddit: "cycling"
    },
    {
      title: "Power meter training zones",
      selftext: "Just got my first power meter. How do I set up my training zones correctly? Currently doing 4x8min threshold intervals.",
      subreddit: "cycling"
    },
    {
      title: "Bike won't shift properly",
      selftext: "My rear derailleur seems out of alignment. The chain keeps skipping gears. Any tips for fixing this?",
      subreddit: "cycling"
    },
    {
      title: "TrainerRoad workout discussion",
      selftext: "What's everyone's favorite TrainerRoad workout for building FTP?",
      subreddit: "trainerroad"
    }
  ];
  
  console.log('Testing categorization on sample posts...\n');
  
  for (let i = 0; i < testPosts.length; i++) {
    const post = testPosts[i];
    console.log(`${i + 1}. Testing: "${post.title}"`);
    
    try {
      const category = await categorizer.categorizePost(post.title, post.selftext, post.subreddit);
      console.log(`   Result: ${category.toUpperCase()}`);
      console.log(`   Content: "${post.selftext.substring(0, 80)}..."`);
      console.log();
    } catch (error) {
      console.error(`   Error: ${error.message}`);
    }
    
    // Add delay between requests
    if (i < testPosts.length - 1) {
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
  
  console.log('✅ OpenAI categorization test completed');
}

testOpenAICategorization();