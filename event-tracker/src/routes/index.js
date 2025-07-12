const express = require('express')
const { saveData } = require('../common/datawarehouse')
const { SQS } = require('../common/awsQueue')
const sendToTelegram = require('../common/sendToTelegram')
const { handleMauticEvent } = require('../mautic/handler')
const router = express.Router()
var Mixpanel = require('mixpanel');
var mixpanel = Mixpanel.init('957f498449a3c30ec903fd23365b7286');

// Health check route
router.get('/', (req, res) => {
  res.json({ status: 'ok', service: 'events-tracker', timestamp: new Date().toISOString() })
})

router.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'events-tracker', timestamp: new Date().toISOString() })
})


router.post('/webhook', async (req, res) => {
  let queueMessageBody = null
  let queueMessageActionName = null
  const { body } = req
  const { userId, name, value, payload = null } = body
  await saveData(body)

  const isWorkoutPopularityModifyEvent = (name === 'workout downloaded') || (name === 'workout sent')
  const isPlanPopularityModifyEvent = (name === 'plan downloaded')
  const isReasonForUnsubscribingEvent = (name === 'Reason for unsubscribing')

  if (isWorkoutPopularityModifyEvent && payload) {
    const { workoutId } = payload
    if (workoutId && Number(workoutId) > 0) {
      queueMessageBody = { workoutId, eventName: name }
      queueMessageActionName = 'increase_workout_popularity_index'
    }
  }

  if (isPlanPopularityModifyEvent && payload) {
    const { planId } = payload
    if (planId) {
      queueMessageBody = { planId, eventName: name, subEventName: value }
      queueMessageActionName = 'increase_plan_popularity_index'
    }
  }

  try {
    await handleMauticEvent(body)
  } catch (e) {
    console.log(e)
  }

  if (queueMessageBody && queueMessageActionName) {
    await SQS.sendMessage({
      QueueUrl: 'https://sqs.us-east-1.amazonaws.com/949540593093/prod_app',
      MessageBody: JSON.stringify(queueMessageBody),
      MessageAttributes: {
        userId: {
          DataType: 'String',
          StringValue: String(userId)
        },
        actionName: {
          DataType: 'String',
          StringValue: queueMessageActionName
        }
      }
    }).promise()
  }

  try {
    if (name.toLowerCase().includes('subscription')) {
      mixpanel.track("Subscription Changed", {
        plan: value,
        distinct_id: userId,
        membership_status: payload.to
      })

      mixpanel.people.set(userId, {
        plan: value,
        membership_status: payload.to
      })

    }
  }catch (e) {
    console.log(e)
  }

  if (isReasonForUnsubscribingEvent) {
    const { username, email } = payload
    let msg = `👤 ${username} | ${userId} | ${email} \n`
    msg += `🔸 ${value}\n\n`
    const chatId = -1002536121735 // TrainerDay Goodbye Feedback
    const botKey = '1494068802:AAH-ntRMrGwhcNOTxil8tJIMu_ley8WRHtw' // TrainerDay Good News @TrainerDay_Good_News_bot
    await sendToTelegram(encodeURIComponent(msg), chatId, botKey)
  }

  return res.end()
})

module.exports = router
