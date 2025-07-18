require('dotenv').config();

// Test the optimized flow - only send NEW posts to OpenAI
async function testOptimizedFlow() {
  console.log('Testing optimized OpenAI flow...\n');
  
  const { savePostsOnly, updatePostCategories } = require('../db');
  const PostCategorizer = require('../openai-categorizer');
  
  if (!process.env.OPENAI_API_KEY || process.env.OPENAI_API_KEY === 'your_openai_api_key_here') {
    console.error('❌ OpenAI API key not configured');
    return;
  }
  
  // Mock posts - some new, some existing
  const mockPosts = [
    {
      title: "Test Optimized Performance Post",
      author: "test_user",
      created: new Date(),
      score: 10,
      num_comments: 3,
      url: "https://reddit.com/r/cycling/comments/test_opt_123/test/",
      selftext: "This is a test new performance post for optimization testing",
      subreddit: "cycling"
    },
    {
      title: "Test Optimized Indoor Post", 
      author: "zwift_user",
      created: new Date(),
      score: 8,
      num_comments: 2,
      url: "https://reddit.com/r/cycling/comments/test_opt_456/indoor/",
      selftext: "This is a test new indoor cycling post for optimization testing",
      subreddit: "cycling"
    },
    {
      title: "Test Optimized Other Post",
      author: "bike_user", 
      created: new Date(),
      score: 5,
      num_comments: 1,
      url: "https://reddit.com/r/cycling/comments/test_opt_789/other/",
      selftext: "This is a test bike maintenance post",
      subreddit: "cycling"
    }
  ];
  
  try {
    console.log('🔄 Step 1: Save posts to determine which are new');
    console.log(`   Processing ${mockPosts.length} total posts...`);
    
    // Save posts first to determine which are truly new
    const actualNewPosts = await savePostsOnly(mockPosts);
    console.log(`   ✅ Found ${actualNewPosts.length} truly new posts`);
    
    if (actualNewPosts.length === 0) {
      console.log('   ℹ️  No new posts found, skipping OpenAI categorization');
      console.log('   💰 Cost saved: $0.00 (no API calls made)');
      return;
    }
    
    console.log('\n🤖 Step 2: Send ONLY new posts to OpenAI for categorization');
    console.log(`   Sending ${actualNewPosts.length} posts to OpenAI (instead of ${mockPosts.length})`);
    
    const categorizer = new PostCategorizer(process.env.OPENAI_API_KEY);
    const categorizedNewPosts = await categorizer.categorizePosts(actualNewPosts);
    
    console.log(`   ✅ Categorized ${categorizedNewPosts.length} posts`);
    
    console.log('\n📊 Step 3: Update database with categories');
    await updatePostCategories(categorizedNewPosts);
    console.log(`   ✅ Updated categories for ${categorizedNewPosts.length} posts`);
    
    console.log('\n📈 Results:');
    categorizedNewPosts.forEach((post, index) => {
      console.log(`   ${index + 1}. "${post.title.substring(0, 50)}..." → ${post.category}`);
    });
    
    const savedCalls = mockPosts.length - actualNewPosts.length;
    const estimatedCostSaved = savedCalls * 0.002; // Rough estimate
    console.log(`\n💰 Optimization Impact:`);
    console.log(`   - API calls saved: ${savedCalls}`);
    console.log(`   - Estimated cost saved: $${estimatedCostSaved.toFixed(4)}`);
    
    console.log('\n✅ Optimized flow test completed successfully!');
    console.log('   Only NEW posts were sent to OpenAI for categorization');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

testOptimizedFlow();