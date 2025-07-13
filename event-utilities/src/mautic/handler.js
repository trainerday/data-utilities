const axios = require('axios')
const { pool } = require('../common/db')

const basicAuth = "Basic YWRtaW46ZHZuIXB1azFtbmgqeGh0LkhOSg=="

async function getData(userId) {
  const select = "select * from events where user_id ='"+ userId +"' and name = 'new user registered'"
  let email = ""
  const res = await pool.query(select)
  if (res.rows.length > 0) {
    email = res.rows[0].json_data.email
  }
  return email
}

async function baseEventHandler(payload, type) {
  const { email, firstname, membership, freePeriod } = payload
  const userId = payload.id || payload.userId

  let segmentId = 1

  const data = {
    email
  }

  if (type === "event") {
    segmentId = 5
    data.user_id = userId

    try {
      data.email = await getData(data.user_id)
    } catch {}

    data.last_event_description = JSON.stringify(payload)
  }

  if ((data.email == null || data.email === "")) return

  if (type !== "event") {
    data.firstname = firstname
    data.user_id = userId
    data.membership_status = type
  }

  if (type === "free") {
    segmentId = 1
    data.register_month = new Date().toISOString().slice(0, 7)
  }

  if (type === "subscription-free-period") {
    segmentId = 12
    data.membership = membership
    // freePeriod example { startDate:"2025-07-09", endDate:"2025-07-15" }
    data.membership_fp_start_date = freePeriod.startDate
    data.membership_fp_end_date = freePeriod.endDate
  }

  if (type === "active") {
    segmentId = 2
    data.membership_status_date = new Date().toISOString().slice(0, 10)
    data.membership = membership
    data.subscription_month = new Date().toISOString().slice(0, 7)
  }

  if (type === "cancelled") {
    data.membership_status_date = new Date().toISOString().slice(0, 10)
    data.cancel_month = new Date().toISOString().slice(0, 7)
    data.membership = membership
    segmentId = 3
  }

  if (type === "expired") {
    data.membership = membership
    segmentId = 4
  }

  if (type === "suspended") {
    data.membership = membership
    segmentId = 10
  }

  return addContactAndAddToSegment(data, segmentId)
}

async function addContactAndAddToSegment(contactData, segmentId) {
  const headers = { 'Authorization': basicAuth, 'Content-Type': 'application/json' }

  const contactResp = await axios.post('https://crm.trainerday.com/api/contacts/new', contactData, { headers })
  const { contact } = contactResp.data

  return axios.post(`https://crm.trainerday.com/api/segments/${segmentId}/contact/${contact.id}/add`, {}, { headers })
}

async function handleMauticEvent(payload) {
  return baseEventHandler(payload, "event")
}

module.exports = {
  handleMauticEvent,
  baseEventHandler
}