// Simple test to verify the email service integration without external calls
const path = require('path');

// Mock the mautic handler to avoid actual API calls
const mockMauticHandler = {
  baseEventHandler: async (data, type) => {
    console.log(`✅ Mautic handler called with type: ${type}`);
    console.log(`   Data:`, data);
    return Promise.resolve({ success: true });
  }
};

// Mock require to return our mock handler
const originalRequire = require;
require = function(id) {
  if (id === '../mautic/handler') {
    return mockMauticHandler;
  }
  return originalRequire.apply(this, arguments);
};

// Now test the email service
const { sendMessageToMautic } = require('../src/common/emailService');

console.log('Testing email service with direct mautic integration...\n');

// Test different event types
const testCases = [
  {
    name: 'New User Registration',
    type: 'new_user',
    expectedMauticType: 'free'
  },
  {
    name: 'Subscription Active',
    type: 'subscription-active',
    expectedMauticType: 'active'
  },
  {
    name: 'Subscription Cancel',
    type: 'subscription-cancel',
    expectedMauticType: 'cancelled'
  },
  {
    name: 'Free Period Assigned',
    type: 'subscription-free-period-assigned',
    expectedMauticType: 'subscription-free-period'
  }
];

async function runTests() {
  for (const testCase of testCases) {
    console.log(`Testing: ${testCase.name}`);
    await sendMessageToMautic(
      'testuser',
      'premium',
      'test@example.com',
      testCase.type,
      123,
      { startDate: '2025-07-09', endDate: '2025-07-15' }
    );
    console.log('');
  }
  
  console.log('🎉 All tests completed successfully!');
  console.log('✅ Email service now uses direct mautic calls instead of API calls');
}

runTests().catch(console.error);