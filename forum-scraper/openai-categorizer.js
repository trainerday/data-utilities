const axios = require('axios');

// OpenAI categorization for forum posts
class PostCategorizer {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseURL = 'https://api.openai.com/v1';
  }

  async categorizePost(title, content, subreddit = 'reddit') {
    // Handle TrainerRoad posts separately - no OpenAI needed
    if (subreddit && subreddit.toLowerCase().includes('trainerroad')) {
      return 'TrainerRoad';
    }

    const prompt = `Analyze this cycling/fitness forum post and categorize it. Choose from these categories:

1. PERFORMANCE - if it discusses:
   - Training methods, workouts, intervals, climbing, speed
   - FTP, power, heart rate, fitness metrics
   - Race preparation, competition strategy
   - Performance improvement techniques
   - Coaching, training plans
   - Physical conditioning, strength training
   - Nutrition for performance
   - Recovery strategies for better performance

2. INDOOR CYCLING - if it discusses:
   - Indoor trainers, smart trainers, trainer workouts
   - Indoor cycling apps (Zwift, etc.)
   - Indoor training setups, pain caves
   - Trainer-specific equipment or accessories
   - Indoor cycling experiences or comparisons

3. OTHER - if it discusses anything else (bike purchases, repairs, maintenance, routes, travel, casual riding, safety, gear, clothing, social aspects, general health/lifestyle topics, equipment for comfort/convenience, etc.)

Title: "${title}"
Content: "${content || 'No content provided'}"

If it's PERFORMANCE, respond: "Performance"
If it's INDOOR CYCLING, respond: "Indoor Cycling" 
If it's OTHER, respond: "Other: [brief 2-3 word description of what it's about]"

Examples:
- "Other: Bike maintenance"
- "Other: Route planning"
- "Other: Gear reviews"`;

    try {
      const response = await axios.post(
        `${this.baseURL}/chat/completions`,
        {
          model: 'gpt-3.5-turbo',
          messages: [
            {
              role: 'user',
              content: prompt
            }
          ],
          max_tokens: 20,
          temperature: 0.1
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const result = response.data.choices[0].message.content.trim();
      
      // Validate and normalize response
      if (result.toLowerCase().includes('performance')) {
        return 'Performance';
      } else if (result.toLowerCase().includes('indoor')) {
        return 'Indoor Cycling';
      } else if (result.toLowerCase().startsWith('other')) {
        return result;
      } else {
        console.warn(`Unexpected OpenAI response: "${result}", defaulting to "Other: Uncategorized"`);
        return 'Other: Uncategorized';
      }
      
    } catch (error) {
      console.error('Error calling OpenAI API:', error.message);
      return 'Other: API Error';
    }
  }

  // Batch categorize multiple posts
  async categorizePosts(posts) {
    const results = [];
    
    for (const post of posts) {
      try {
        // Add delay to respect rate limits
        if (results.length > 0) {
          await new Promise(resolve => setTimeout(resolve, 1000)); // 1 second delay
        }
        
        const category = await this.categorizePost(post.title, post.selftext, post.subreddit);
        results.push({
          ...post,
          category
        });
        
        console.log(`Categorized: "${post.title.substring(0, 50)}..." → ${category}`);
        
      } catch (error) {
        console.error(`Error categorizing post "${post.title}":`, error.message);
        results.push({
          ...post,
          category: 'other'
        });
      }
    }
    
    return results;
  }
}

module.exports = PostCategorizer;