const axios = require('axios');

// Telegram notification service
class TelegramNotifier {
  constructor(botToken, chatId) {
    this.botToken = botToken;
    this.chatId = chatId;
    this.baseURL = `https://api.telegram.org/bot${botToken}`;
  }

  async sendMessage(text, options = {}) {
    try {
      const response = await axios.post(`${this.baseURL}/sendMessage`, {
        chat_id: this.chatId,
        text: text,
        parse_mode: options.parseMode || 'HTML',
        disable_web_page_preview: options.disablePreview || false
      });

      return response.data;
    } catch (error) {
      console.error('Error sending Telegram message:', error.message);
      throw error;
    }
  }

  async notifyPerformancePost(post) {
    const emoji = this.getSourceEmoji(post.subreddit);
    const timeAgo = this.getTimeAgo(post.created);
    
    let categoryIcon, categoryText;
    if (post.category === 'Performance') {
      categoryIcon = '⚡';
      categoryText = 'PERFORMANCE';
    } else if (post.category === 'Indoor Cycling') {
      categoryIcon = '🏠';
      categoryText = 'INDOOR CYCLING';
    } else {
      categoryIcon = '⚡';
      categoryText = 'PERFORMANCE';
    }
    
    // Create filtered forum URL
    const categoryParam = post.category === 'Indoor Cycling' ? 'Indoor%20Cycling' : post.category;
    const forumUrl = `https://forum-scraper.uat.trainerday.com/forums/${categoryParam}`;
    
    const message = `${categoryIcon} <b>NEW ${categoryText} POST</b> ${emoji}

📝 <b>${this.escapeHtml(post.title)}</b>

👤 By: ${this.escapeHtml(post.author)}
⏰ ${timeAgo}
💬 ${post.num_comments} comments
⭐ ${post.score} points

${post.selftext ? this.truncateText(this.escapeHtml(post.selftext), 200) : 'No content preview'}

🔗 <a href="${forumUrl}">View ${categoryText} Posts</a>
📄 <a href="${post.url}">Original Post</a>`;

    return this.sendMessage(message);
  }

  async notifyBatchPerformancePosts(posts) {
    if (posts.length === 0) return;

    if (posts.length === 1) {
      return this.notifyPerformancePost(posts[0]);
    }

    const message = `⚡ <b>${posts.length} NEW PERFORMANCE POSTS</b>

${posts.map((post, index) => {
      const emoji = this.getSourceEmoji(post.subreddit);
      return `${index + 1}. ${emoji} <b>${this.escapeHtml(post.title)}</b>
   👤 ${this.escapeHtml(post.author)} | 💬 ${post.num_comments} | ⭐ ${post.score}
   🔗 <a href="${post.url}">View</a>`;
    }).join('\n\n')}`;

    return this.sendMessage(message);
  }

  getSourceEmoji(subreddit) {
    switch (subreddit) {
      case 'cycling': return '🚴';
      case 'Velo': return '🏆';
      case 'trainerroad': return '📊';
      default: return '🔗';
    }
  }

  getTimeAgo(date) {
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));

    if (hours > 0) {
      return `${hours}h ago`;
    } else if (minutes > 0) {
      return `${minutes}m ago`;
    } else {
      return 'Just now';
    }
  }

  escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - 3) + '...';
  }

  // Test the bot connection
  async testConnection() {
    try {
      const response = await axios.get(`${this.baseURL}/getMe`);
      console.log('✅ Telegram bot connected:', response.data.result.username);
      return true;
    } catch (error) {
      console.error('❌ Telegram bot connection failed:', error.message);
      return false;
    }
  }
}

module.exports = TelegramNotifier;