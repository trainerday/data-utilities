require('dotenv').config();

// Test Telegram notifications
async function testTelegram() {
  console.log('Testing Telegram bot connection...\n');
  
  const TelegramNotifier = require('../telegram-notifier');
  
  if (!process.env.TELEGRAM_BOT_TOKEN || process.env.TELEGRAM_BOT_TOKEN === 'your_telegram_bot_token_here') {
    console.error('❌ Telegram bot token not configured');
    console.log('Please follow TELEGRAM-SETUP.md to set up your bot');
    return;
  }
  
  if (!process.env.TELEGRAM_CHAT_ID || process.env.TELEGRAM_CHAT_ID === 'your_telegram_chat_id_here') {
    console.error('❌ Telegram chat ID not configured');
    console.log('Please follow TELEGRAM-SETUP.md to get your chat ID');
    return;
  }
  
  const telegram = new TelegramNotifier(process.env.TELEGRAM_BOT_TOKEN, process.env.TELEGRAM_CHAT_ID);
  
  // Test connection
  console.log('1. Testing bot connection...');
  const connected = await telegram.testConnection();
  
  if (!connected) {
    console.error('❌ Could not connect to Telegram bot');
    return;
  }
  
  // Test notification with sample performance post
  console.log('\n2. Testing performance post notification...');
  
  const samplePost = {
    title: "How to improve my FTP? [TEST]",
    author: "test_user",
    created: new Date(),
    score: 15,
    num_comments: 8,
    url: "https://reddit.com/r/cycling/test",
    selftext: "This is a test performance post to verify Telegram notifications are working correctly. Your forum scraper is successfully categorizing and notifying about performance-related posts!",
    subreddit: "cycling",
    category: "Performance"
  };
  
  try {
    await telegram.notifyPerformancePost(samplePost);
    console.log('✅ Test notification sent successfully!');
    console.log('Check your Telegram for the test message.');
  } catch (error) {
    console.error('❌ Failed to send test notification:', error.message);
  }
}

testTelegram();