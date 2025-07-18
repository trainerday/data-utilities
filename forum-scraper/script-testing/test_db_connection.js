require('dotenv').config();

// Test the database connection configuration
async function testDbConnection() {
  console.log('Testing database connection configuration...\n');
  
  console.log('Environment variables:');
  console.log('DB_HOST:', process.env.DB_HOST || 'NOT SET');
  console.log('DB_PORT:', process.env.DB_PORT || 'NOT SET');
  console.log('DB_DATABASE:', process.env.DB_DATABASE || 'NOT SET');
  console.log('DB_USERNAME:', process.env.DB_USERNAME || 'NOT SET');
  console.log('DB_PASSWORD:', process.env.DB_PASSWORD ? 'SET' : 'NOT SET');
  console.log('DB_SSL_CERT length:', process.env.DB_SSL_CERT ? process.env.DB_SSL_CERT.length : 'NOT SET');
  console.log('DB_SSLROOTCERT:', process.env.DB_SSLROOTCERT || 'NOT SET');
  
  const fs = require('fs');
  const path = require('path');
  const { Pool } = require('pg');
  
  try {
    // Test the exact configuration from db.js
    console.log('\\nTesting pool configuration...');
    
    const poolConfig = {
      host: process.env.DB_HOST,
      port: process.env.DB_PORT,
      database: process.env.DB_DATABASE,
      user: process.env.DB_USERNAME,
      password: process.env.DB_PASSWORD,
      ssl: {
        require: true,
        rejectUnauthorized: false, // This should allow self-signed certificates
        ca: process.env.DB_SSL_CERT || fs.readFileSync(path.join(__dirname, '..', process.env.DB_SSLROOTCERT || 'postgres.crt')).toString()
      }
    };
    
    console.log('SSL config:');
    console.log('- require:', poolConfig.ssl.require);
    console.log('- rejectUnauthorized:', poolConfig.ssl.rejectUnauthorized);
    console.log('- ca length:', poolConfig.ssl.ca ? poolConfig.ssl.ca.length : 'NOT SET');
    
    const pool = new Pool(poolConfig);
    const client = await pool.connect();
    console.log('\\n✅ Connection successful!');
    
    const result = await client.query('SELECT NOW() as current_time');
    console.log('Query result:', result.rows[0]);
    
    client.release();
    await pool.end();
    
  } catch (error) {
    console.error('\\n❌ Connection failed:', error.message);
    
    // Try without SSL to see if that's the issue
    console.log('\\nTrying without SSL...');
    try {
      const poolNoSSL = new Pool({
        host: process.env.DB_HOST,
        port: process.env.DB_PORT,
        database: process.env.DB_DATABASE,
        user: process.env.DB_USERNAME,
        password: process.env.DB_PASSWORD,
        ssl: false
      });
      
      const client = await poolNoSSL.connect();
      console.log('✅ Connection without SSL successful!');
      client.release();
      await poolNoSSL.end();
      
    } catch (noSSLError) {
      console.error('❌ Connection without SSL also failed:', noSSLError.message);
    }
  }
}

testDbConnection();