const axios = require('axios')

const issuesChatId = -523165256 // TrainerDay Critical Issues
const issuesBotToken = '1771705962:AAEi0pxfjuyb4YtSheBCvn4BQb7ewsFs7fE'

module.exports = (message, chatId = issuesChatId, botToken = issuesBotToken) => {
  try {
    if (typeof message === 'object') {
      // eslint-disable-next-line no-param-reassign
      message = JSON.stringify(message)
    }

    return axios.get(`https://api.telegram.org/bot${botToken}/sendMessage?chat_id=${chatId}&text=${message}`)
  } catch (e) {
    console.warn(e)
  }
}
