const AWS = require('aws-sdk')

// Debug environment variables
console.log('AWS Environment Variables:')
console.log('AWS_ACCESS_KEY_ID:', process.env.AWS_ACCESS_KEY_ID ? 'SET' : 'NOT SET')
console.log('AWS_SECRET_ACCESS_KEY:', process.env.AWS_SECRET_ACCESS_KEY ? 'SET' : 'NOT SET')
console.log('AWS_REGION:', process.env.AWS_REGION || 'us-east-1')

AWS.config.update({
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  region: process.env.AWS_REGION || 'us-east-1'
})

const SQS = new AWS.SQS({ apiVersion: '2012-11-05' })

module.exports = {
  SQS
}
