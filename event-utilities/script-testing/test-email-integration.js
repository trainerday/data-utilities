const { handleEmailWebhook, sendMessageToMautic } = require('../src/common/emailService');

// Mock request and response objects for testing
const mockReq = {
  body: {
    userid: 123,
    username: 'testuser',
    role: 'premium',
    email: 'test@example.com'
  },
  query: {
    type: 'new_user'
  }
};

const mockRes = {
  jsonp: (data) => console.log('Response:', data),
  status: (code) => ({ jsonp: (data) => console.log('Error response:', code, data) })
};

console.log('Testing email webhook integration...');

// Test the email webhook handler
handleEmailWebhook(mockReq, mockRes)
  .then(result => {
    console.log('Email webhook test result:', result);
    console.log('✅ Email integration test completed successfully');
  })
  .catch(error => {
    console.error('❌ Email integration test failed:', error);
  });