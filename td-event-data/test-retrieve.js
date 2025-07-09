import { S3Client, ListObjectsV2Command, GetObjectCommand } from '@aws-sdk/client-s3';

// R2 configuration - update these with your account details
const ACCOUNT_ID = 'your-account-id';
const ACCESS_KEY_ID = 'your-r2-access-key';
const SECRET_ACCESS_KEY = 'your-r2-secret-key';
const BUCKET_NAME = 'posthog-events';

const s3Client = new S3Client({
  region: 'auto',
  endpoint: `https://${ACCOUNT_ID}.r2.cloudflarestorage.com`,
  credentials: {
    accessKeyId: ACCESS_KEY_ID,
    secretAccessKey: SECRET_ACCESS_KEY,
  },
});

async function listFiles() {
  try {
    const command = new ListObjectsV2Command({
      Bucket: BUCKET_NAME,
      Prefix: 'posthog-events/',
      MaxKeys: 10
    });
    
    const response = await s3Client.send(command);
    
    if (response.Contents) {
      console.log(`Found ${response.Contents.length} files:\n`);
      response.Contents.forEach(obj => {
        console.log(`- ${obj.Key} (${obj.Size} bytes, ${obj.LastModified})`);
      });
      return response.Contents;
    } else {
      console.log('No files found in bucket');
      return [];
    }
  } catch (error) {
    console.error('Error listing files:', error);
    return [];
  }
}

async function getFile(key) {
  try {
    const command = new GetObjectCommand({
      Bucket: BUCKET_NAME,
      Key: key,
    });
    
    const response = await s3Client.send(command);
    const data = await response.Body.transformToString();
    return JSON.parse(data);
  } catch (error) {
    console.error(`Error getting file ${key}:`, error);
    return null;
  }
}

async function testRetrieve() {
  console.log('Listing files in R2 bucket...\n');
  const files = await listFiles();
  
  if (files.length > 0) {
    console.log('\nRetrieving latest file...');
    const latestFile = files[files.length - 1];
    const content = await getFile(latestFile.Key);
    
    if (content) {
      console.log('\nFile content:');
      console.log(JSON.stringify(content, null, 2));
    }
  }
}

testRetrieve();