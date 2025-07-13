var updateUserEmail = require('./wordpress.js') 
var unubscribeMauticUser = require('./mautic.js') 
var unubscribeBigMailerUser = require('./bigmailer.js') 
var deleteDiscourseUserByEmail = require('./discourse.js')
async function deleteUser(email){
    await unubscribeMauticUser(email)
    await unubscribeBigMailerUser(email)
    await deleteDiscourseUserByEmail(email)
    await updateUserEmail(email)
}

module.exports = deleteUser

//var args = process.argv.slice(2);
//var email = args[0]
//deleteUser(email).then(() => {})

