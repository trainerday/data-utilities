const axios = require('axios');

async function testEmailWebhook() {
  console.log('Testing /email-webhook endpoint...\n');
  
  const testData = {
    userid: 123,
    username: 'testuser',
    role: 'premium',
    email: 'test@example.com'
  };
  
  const queryParams = '?type=new_user';
  const url = `http://localhost:3000/email-webhook${queryParams}`;
  
  try {
    console.log(`Making POST request to: ${url}`);
    console.log('Request body:', testData);
    
    const response = await axios.post(url, testData, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 5000
    });
    
    console.log('\n✅ Success!');
    console.log('Status:', response.status);
    console.log('Response:', response.data);
    
  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      console.log('❌ Server not running. Please start with: npm start');
    } else if (error.code === 'TIMEOUT') {
      console.log('❌ Request timed out');
    } else {
      console.log('❌ Error:', error.message);
      if (error.response) {
        console.log('Status:', error.response.status);
        console.log('Response:', error.response.data);
      }
    }
  }
}

async function testTrackEndpoint() {
  console.log('\nTesting /track endpoint...\n');
  
  const testData = {
    userid: 123,
    event: 'test_event'
  };
  
  const url = 'http://localhost:3000/track';
  
  try {
    console.log(`Making POST request to: ${url}`);
    console.log('Request body:', testData);
    
    const response = await axios.post(url, testData, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 5000
    });
    
    console.log('\n✅ Success!');
    console.log('Status:', response.status);
    console.log('Response:', response.data);
    
  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      console.log('❌ Server not running. Please start with: npm start');
    } else if (error.code === 'TIMEOUT') {
      console.log('❌ Request timed out');
    } else {
      console.log('❌ Error:', error.message);
      if (error.response) {
        console.log('Status:', error.response.status);
        console.log('Response:', error.response.data);
      }
    }
  }
}

async function runTests() {
  await testEmailWebhook();
  await testTrackEndpoint();
  console.log('\nTests completed.');
}

runTests();