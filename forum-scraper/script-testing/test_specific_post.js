#!/usr/bin/env node

require('dotenv').config();
const PostCategorizer = require('../openai-categorizer');

async function testSpecificPost() {
  const categorizer = new PostCategorizer(process.env.OPENAI_API_KEY);
  
  const title = "Training";
  const content = "I've been cycling for just a few years now and have finally switched to consistent training. I'm a fit 47 year old and I want to start gravel racing (for fun) towards the end of the season. With my work and commute schedule I can basically do 100km a week with 1000m elevation gain over 4-5 sessions but generally only an hour or so per session with the opportunity for one longer ride (2-4 hours) on the weekend. My question is how much better can one get with this volume/structure of training?";
  
  console.log('Testing categorization for the "Training" post...');
  console.log('Title:', title);
  console.log('Content:', content);
  console.log('');
  
  try {
    const category = await categorizer.categorizePost(title, content, 'cycling');
    console.log('OpenAI Category Result:', category);
    
    // Test a few more times to see if it's consistent
    console.log('\nTesting multiple times for consistency:');
    for (let i = 1; i <= 3; i++) {
      const result = await categorizer.categorizePost(title, content, 'cycling');
      console.log(`Attempt ${i}: ${result}`);
      // Add delay between requests
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
  } catch (error) {
    console.error('Error:', error.message);
  }
}

testSpecificPost();