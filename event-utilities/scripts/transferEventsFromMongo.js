const { performance } = require('perf_hooks')
const mongoose = require('mongoose')
const format = require('pg-format')
const db = require('./mongooseConnection')
const { pool } = require('../src/common/db')

const eventSchema = new mongoose.Schema({
  userId: Number,
  eventId: String,
  eventName: String,
  name: String,
  subEventName: String,
  insertDate: mongoose.Schema.Types.Date
})

const Event = mongoose.model('Events', eventSchema)

async function start(fromName, toName) {
  const t0 = performance.now()

  db.connectToDatabase()

  const filter = {
    eventName: fromName,
    userId: { $nin: [null, '', undefined] }
    // insertDate: { $gte: new Date('2022-01-01T00:00:00.000Z') }
  }

  let events = await Event.find(filter, {})

  console.log(`Count: ${events.length}`)

  // const eventsIds = events.map(e => e._id)
  events = events.map((event) => {
    const {
      eventName,
      name,
      insertDate,
      userId,
      eventId
    } = event

    let {
      subEventName
    } = event

    subEventName = subEventName.toLowerCase()

    if (subEventName === 'tp') {
      subEventName = 'trainingpeaks'
    }

    let jsonData = null

    if (eventName === 'plan-download') {
      jsonData = {
        planId: eventId
      }
    }

    if (eventName === 'download') {
      jsonData = {
        workoutId: Number(eventId)
      }
    }

    if (subEventName === 'td-calendar' || subEventName === 'calendar') {
      subEventName = 'trainerday calendar'
    }

    if (subEventName === 'google') {
      subEventName = 'google calendar'
    }

    if (eventName === 'search' && name) {
      const regex = /(.*)p:(\d+)/

      let query = ''
      let page = 0

      if (regex.test(name)) {
        [, query, page] = name.match(regex)
      } else {
        query = name
      }

      jsonData = {
        query,
        page: Number(page)
      }
    }

    return [userId, toName, subEventName, jsonData, insertDate]
  })

  const insertSql = format('INSERT INTO events (user_id, name, value, json_data, created_at) VALUES %L', events)

  await pool.query(insertSql)
  // await Event.deleteMany({ _id: { $in: eventsIds } })

  const t1 = performance.now()
  // eslint-disable-next-line no-console
  console.log('\x1b[33m%s\x1b[0m', `Time ${Math.round(((t1 - t0) / 1000))} seconds.`)

  return process.exit()
}

// start('download', 'workout downloaded')
// start('push', 'workout sent')
start('download-activity', 'activity downloaded')
// start('upload-workout-file', 'workout file uploaded')
// start('plan-download', 'plan downloaded')
// start('search', 'workout search performed')
