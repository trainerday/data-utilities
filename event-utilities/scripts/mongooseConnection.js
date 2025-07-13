const mongoose = require('mongoose')

const MONGO_URI = 'mongodb+srv://douser:NJuUQg62Z8i07419@mongodb-production-d1c5b3a1.mongo.ondigitalocean.com'
const mongoParams = '?authSource=admin&replicaSet=mongodb-production&tls=true&tlsCAFile=./ca-certificate.crt'
const connectionString = `${MONGO_URI}/trainerday-production${mongoParams}`

const connectToDatabase = () => {
  mongoose.connect(connectionString).then(() => {})
}

const db = mongoose.connection

db.on('connecting', async () => {
  process.env.DATABASE_IS_DOWN = true
})

db.on('connected', async () => {
  console.log('Database connected')
  process.env.DATABASE_IS_DOWN = false
})

db.on('error', (error) => {
  console.error(`Database error: ${error}`)
  mongoose.disconnect().then(() => {})
})

db.on('reconnected', () => {
  console.log('Database reconnected')
})

db.on('disconnected', () => {
  console.log('Database reconnecting')
  process.env.DATABASE_IS_DOWN = true
  setTimeout(() => {
    connectToDatabase()
  }, 1000)
})

module.exports = {
  db,
  connectToDatabase
}
