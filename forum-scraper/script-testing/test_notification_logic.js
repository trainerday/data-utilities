require('dotenv').config();

// Test the new notification logic - only send for NEW posts
async function testNotificationLogic() {
  console.log('Testing new notification logic...\n');
  
  const { savePostsOnly, markPostsAsNotified } = require('../db');
  const TelegramNotifier = require('../telegram-notifier');
  
  // Mock posts - one new, one existing
  const mockPosts = [
    {
      title: "Test New Performance Post",
      author: "test_user",
      created: new Date(),
      score: 10,
      num_comments: 3,
      url: "https://reddit.com/r/cycling/comments/test_new_123/test/",
      selftext: "This is a test new performance post",
      subreddit: "cycling",
      category: "Performance"
    },
    {
      title: "Test New Indoor Cycling Post", 
      author: "zwift_user",
      created: new Date(),
      score: 8,
      num_comments: 2,
      url: "https://reddit.com/r/cycling/comments/test_new_456/indoor/",
      selftext: "This is a test new indoor cycling post",
      subreddit: "cycling",
      category: "Indoor Cycling"
    }
  ];
  
  try {
    // Save posts - this will return only truly new posts
    console.log('1. Saving posts...');
    const actualNewPosts = await savePostsOnly(mockPosts);
    console.log(`   Found ${actualNewPosts.length} truly new posts`);
    
    // Filter for performance/indoor posts
    const newPerformancePosts = actualNewPosts.filter(post => 
      post.category === 'Performance' || post.category === 'Indoor Cycling'
    );
    
    console.log(`   Found ${newPerformancePosts.length} new performance/indoor posts`);
    
    // Test notification (only if Telegram is configured)
    if (newPerformancePosts.length > 0 && 
        process.env.TELEGRAM_BOT_TOKEN && 
        process.env.TELEGRAM_BOT_TOKEN !== 'your_telegram_bot_token_here' &&
        process.env.TELEGRAM_CHAT_ID && 
        process.env.TELEGRAM_CHAT_ID !== 'your_telegram_chat_id_here') {
      
      console.log('2. Sending notifications...');
      const telegram = new TelegramNotifier(process.env.TELEGRAM_BOT_TOKEN, process.env.TELEGRAM_CHAT_ID);
      await telegram.notifyBatchPerformancePosts(newPerformancePosts);
      
      // Mark as notified
      const postIds = newPerformancePosts.map(post => post.id);
      await markPostsAsNotified(postIds);
      
      console.log('   ✅ Notifications sent and posts marked as notified');
      
      // Test saving same posts again - should not send notifications
      console.log('3. Testing duplicate prevention...');
      const duplicateNewPosts = await savePostsOnly(mockPosts);
      console.log(`   Found ${duplicateNewPosts.length} truly new posts (should be 0)`);
      
      if (duplicateNewPosts.length === 0) {
        console.log('   ✅ Duplicate prevention working correctly');
      } else {
        console.log('   ❌ Found duplicates when there should be none');
      }
      
    } else {
      console.log('2. Telegram not configured, skipping notification test');
    }
    
    console.log('\n✅ Notification logic test completed');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

testNotificationLogic();