const axios = require('axios')
const { baseEventHandler } = require('../mautic/handler')

async function sendMessageToMautic(username, membership, email, type, userId, freePeriod = null) {
  const data = {
    email: email,
    firstname: username,
    membership: membership,
    id: userId,
    freePeriod
  }

  let mauticType = null

  if (type.includes('new_user')) {
    mauticType = 'free'
  }

  if (type.includes('subscription-free-period-assigned')) {
    mauticType = 'subscription-free-period'
  }

  if (type.includes('subscription-active')) {
    mauticType = 'active'
  }

  if (type.includes('subscription-cancel')) {
    mauticType = 'cancelled'
  }

  if (type.includes('subscription-expire')) {
    mauticType = 'expired'
  }

  if (type.includes('subscription-suspend')) {
    mauticType = 'suspended'
  }

  if (mauticType) {
    await baseEventHandler(data, mauticType)
  }
}

function sendTelegramChat(username, old_status, membership, userid) {
  const bot_key = "1494068802:AAH-ntRMrGwhcNOTxil8tJIMu_ley8WRHtw"
  const chat_id = "-334706105"
  const text = username + ': ' + old_status + '->active (' + membership + ') ' + userid
  const url = 'https://api.telegram.org/bot' + bot_key + '/sendMessage?chat_id=' + chat_id + '&text=' + text

  axios.post(url)
    .then((response) => {
      // Success
    }, (error) => {
      console.log(error);
    })
}

async function handleEmailWebhook(req, res) {
  let body = req.body
  const data = {}
  const query = req.query
  let type = ""
  if (query.type) {
    type = query.type.toLowerCase()
  }

  let userId
  if (type.includes("subscription-")) {
    userId = query.userid
    const { membership, email, freePeriod, old_status: old_status, username } = query

    data.userid = userId
    data.email = email
    data.username = username
    data.eventtype = type
    data.eventvalue = membership
    data.body = query
    await sendMessageToMautic(username, membership, email, type, userId, freePeriod)

    if (type === "subscription-active") {
      sendTelegramChat(username, old_status, membership, userId)
    }
  }

  if (type.includes('new_user')) {
    userId = body.userid
    data.userid = userId
    const username = body.username
    const membership = body.role
    const email = body.email
    data.email = email
    data.username = username
    data.eventtype = "new_user"
    data.eventvalue = membership
    data.body = body
    await sendMessageToMautic(username, membership, email, type, userId)
  }

  if (body.event && body.event != "") {
    userId = body.userId
    data.userid = userId
    data.eventtype = body.event
    data.username = body.firstName
    data.eventvalue = body.planName
    data.email = ""
    data.body = body
    console.log(data)
  }

  return data
}

module.exports = {
  sendMessageToMautic,
  sendTelegramChat,
  handleEmailWebhook
}