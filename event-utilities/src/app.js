require('./common/awsQueue')
const createError = require('http-errors')
const express = require('express')
const cookieParser = require('cookie-parser')
const cors = require('cors')
const logger = require('morgan')
const bodyParser = require('body-parser')

const indexRouter = require('./routes/index')

const app = express()
app.use(bodyParser.json())
app.use(cors())
app.use(logger('dev'))
app.use(express.json())
app.use(express.urlencoded({ extended: false }))
app.use(cookieParser())

app.use('/', indexRouter)

// catch 404 and forward to error handler
app.use((req, res, next) => {
  next(createError(404))
})

// error handler
app.use((err, req, res) => {
  // set locals, only providing error in development
  res.locals.message = err.message
  res.locals.error = req.app.get('env') === 'development' ? err : {}

  // render the error page
  res.status(err.status || 500)
  res.render('error')
})

module.exports = app
