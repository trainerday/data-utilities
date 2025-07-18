require('dotenv').config();

// Test Telegram notifications for Indoor Cycling category
async function testTelegramIndoor() {
  console.log('Testing Telegram indoor cycling notification...\n');
  
  const TelegramNotifier = require('../telegram-notifier');
  
  if (!process.env.TELEGRAM_BOT_TOKEN || process.env.TELEGRAM_BOT_TOKEN === 'your_telegram_bot_token_here') {
    console.error('❌ Telegram bot token not configured');
    return;
  }
  
  if (!process.env.TELEGRAM_CHAT_ID || process.env.TELEGRAM_CHAT_ID === 'your_telegram_chat_id_here') {
    console.error('❌ Telegram chat ID not configured');
    return;
  }
  
  const telegram = new TelegramNotifier(process.env.TELEGRAM_BOT_TOKEN, process.env.TELEGRAM_CHAT_ID);
  
  // Test indoor cycling notification
  const samplePost = {
    title: "Best smart trainer for Zwift? [TEST]",
    author: "zwift_user",
    created: new Date(),
    score: 12,
    num_comments: 5,
    url: "https://reddit.com/r/cycling/test",
    selftext: "Looking for a direct drive trainer that works well with Zwift. Budget around $800. Any recommendations?",
    subreddit: "cycling",
    category: "Indoor Cycling"
  };
  
  try {
    await telegram.notifyPerformancePost(samplePost);
    console.log('✅ Indoor cycling test notification sent successfully!');
    console.log('Check your Telegram for the test message.');
  } catch (error) {
    console.error('❌ Failed to send test notification:', error.message);
  }
}

testTelegramIndoor();