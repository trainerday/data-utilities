# Telegram Bot Setup Guide

To receive performance post notifications, you need to set up a Telegram bot and get your chat ID.

## Step 1: Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Start a chat with BotFather and send `/newbot`
3. Choose a name for your bot (e.g., "Forum Performance Alerts")
4. Choose a username (e.g., "your_forum_bot")
5. BotFather will give you a **Bot Token** like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

## Step 2: Get Your Chat ID

1. Start a chat with your new bot (click the link BotFather provides)
2. Send any message to your bot (e.g., "Hello")
3. Go to this URL in your browser (replace YOUR_BOT_TOKEN):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. Look for the `"chat":{"id":` field in the response
5. Your Chat ID will be a number like `123456789` or `-123456789`

## Step 3: Update Environment Variables

Edit your `.env` file and replace:

```bash
# Telegram Bot Configuration  
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

## Step 4: Test the Connection

Run the test script:
```bash
node script-testing/test_telegram.js
```

## Example Notification

When a performance post is found, you'll get a message like:

```
⚡ NEW PERFORMANCE POST 🚴

📝 How to improve my FTP?

👤 By: cycling_user
⏰ 2m ago
💬 5 comments
⭐ 12 points

I've been training for 6 months and my FTP is stuck at 250W. What training intervals should I focus on to break through this plateau?

🔗 View Post
```

## Troubleshooting

- **Bot not responding**: Make sure you've started a chat with your bot first
- **Chat ID not found**: Send a message to your bot before calling getUpdates
- **403 Forbidden**: Check that your bot token is correct