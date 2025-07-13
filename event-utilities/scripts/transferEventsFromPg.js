const { performance } = require('perf_hooks')
const format = require('pg-format')
const { pool } = require('../src/common/db')

async function start() {
  const t0 = performance.now()

  const t1 = performance.now()

  let { rows: events } = await pool.query('SELECT * from event_log')

  events = events.map((event) => {
    const {
      user_id: userId,
      event_value: eventValue,
      insert_date: insertDate,
      username,
      email
    } = event

    let {
      event_type: eventType
    } = event

    let jsonData = null

    if (eventType === 'new_user') {
      eventType = 'new user registered'

      jsonData = {
        username,
        email
      }
    }

    if (eventType.includes('subscription-')) {
      const regex = /subscription-(.*)/

      const [, statusTo] = eventType.match(regex)

      jsonData = {
        from: 'unknown',
        to: statusTo
      }

      eventType = `subscription status changed to ${statusTo}`
    }

    return [userId, eventType, eventValue, jsonData, insertDate]
  })

  const insertSql = format('INSERT INTO events (user_id, name, value, json_data, created_at) VALUES %L', events)

  await pool.query(insertSql)

  // eslint-disable-next-line no-console
  console.log('\x1b[33m%s\x1b[0m', `Time ${Math.round(((t1 - t0) / 1000))} seconds.`)

  return process.exit()
}

start()
