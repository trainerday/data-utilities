const { Pool } = require('pg')
const fs = require('fs')
const sendToTelegram = require('../common/sendToTelegram')

const path = require('path').join(__dirname, '../../ca-certificate.crt')

// Check if certificate file exists, otherwise use environment variable or skip
let sslConfig = { rejectUnauthorized: false }
try {
  if (fs.existsSync(path)) {
    sslConfig.ca = fs.readFileSync(path).toString()
  } else if (process.env.DATABASE_CA_CERT) {
    sslConfig.ca = process.env.DATABASE_CA_CERT
  }
} catch (error) {
  console.log('Warning: Could not load SSL certificate, using basic SSL config')
}

const config = {
  user: 'doadmin',
  host: 'postgress-dw-do-user-979029-0.b.db.ondigitalocean.com',
  database: 'defaultdb',
  password: 'MafHqU5x4JwXcZu3',
  port: 25060,
  ssl: sslConfig
}

const pool = new Pool(config)

pool.on('connect', () => {
  console.log('\x1b[33m%s\x1b[0m', 'Client connected')
})

pool.on('error', (err) => {
  console.log('\x1b[33m%s\x1b[0m', 'Database error')
  console.log(err)
  try {
    sendToTelegram('Something happened on the event tracking server')
  } catch (e) {}

})

pool.on('remove', () => {
  console.log('\x1b[33m%s\x1b[0m', 'Client closed')
})

pool.connect()

module.exports = { pool }
