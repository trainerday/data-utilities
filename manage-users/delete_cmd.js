require('dotenv').config()
var deleteUser = require('./common/deleteUser')


var args = process.argv.slice(2);
var email = args[0]
deleteUser(email).then(() => {})
