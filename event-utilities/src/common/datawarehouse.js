const { pool } = require('./db')

async function saveData({
  userId,
  name,
  value,
  payload
}) {
  const jsonData = JSON.stringify(payload)
  let createdAt
  let insert
  let values

  if (payload) {
    ({ date: createdAt } = payload)
  }

  if (createdAt) {
    insert = 'insert into events (user_id, name, value, json_data, created_at) values ($1, $2, $3, $4, $5);'
    values = [userId, name, value, jsonData, createdAt]
  } else {
    insert = 'insert into events (user_id, name, value, json_data) values ($1, $2, $3, $4);'
    values = [userId, name, value, jsonData]
  }
  await pool.query(insert, values)
}

module.exports = {
  saveData
}
