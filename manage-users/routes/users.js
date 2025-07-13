var express = require('express')
var router = express.Router()
var dotenv = require('dotenv') 
dotenv.config();

var deleteUser = require('../common/deleteUser');
const e = require('express');

//https://manage-users.prod.trainerday.com/users/delete?email=test&apikey=1231235
router.post('/delete', function(req, res, next) {
  try {
    var email = req.body.email
    var apiKey = req.body.apikey
    if (!apiKey || apiKey !== process.env.API_KEY) {
      res.send('invalid 1')
      return
    }
    if (!email) {
      res.send('missing field')
      return
    }
    if (!email.includes('@')) {
      res.send('invalid 2')
      return
    }
    if (email.toLowerCase().includes('@trainerday.com')) {
      res.send('not allowed')
      return
    }

    deleteUser(email).then(() => {
      res.send('User password and email updated')
    }).catch((error) => {
      res.send('Error updating user')
    })
  }
  catch (e) {
    console.log(e)
  }
})

module.exports = router
