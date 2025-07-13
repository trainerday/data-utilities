const { pool } = require('../common/db')

async function getData() {
  // await pool.query("insert into users (user_id, user_email, user_login, user_registered) " +
  //     " values (1,'a@a.com', 'b', 'yes');")
  // const res = await pool.query('SELECT * from users limit 5')

  // console.log(res.rows)
  // await pool.end()

  const res = await pool.query('SELECT * from users limit 5')

  console.log(res.rows)
}

getData().then(() => {})
