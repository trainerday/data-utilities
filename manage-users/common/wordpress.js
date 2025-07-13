var axios = require('axios') 
var dotenv = require('dotenv') 
const { v4: uuidv4 } = require('uuid');
dotenv.config();




async function getToken(username, password) {
  const url = "https://trainerday.com/wp-json/jwt-auth/v1/token";
  const data = { username, password };

  try {
    const response = await axios.post(url, data, {
      headers: {
        "Content-Type": "application/json"
      }
    });
    return response.data.token; // Return the token from the response
  } catch (error) {
    console.error(error.response ? error.response.data : error.message);
    throw new Error("Failed to get token");
  }
}

async function deleteWPUser(email){
    var url = `https://trainerday.com/?wpwhpro_action=main-erg&wpwhpro_api_key=${process.env.WP_API_KEY}`
    var data = {action:'delete_user',user_email:email}
    var response = await axios.post(url,data);
    console.log(response.data);
}


const getUserIdByEmail = async (email, token) => {
    try {
        // Define the endpoint URL to search user by email
        const url = `https://trainerday.com/wp-json/wp/v2/users?search=${email}`;

        // Send GET request to find the user by email
        const response = await axios({
            method: 'get',
            url: url,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        const users = response.data;
        if (users.length > 0) {
            // Return the user ID of the first user found
            console.log(`User found with ID: ${users[0].id}`);
            return users[0].id;
        } else {
            throw new Error('User not found');
        }
    } catch (error) {
        console.log('Error finding WP user by email:', error.response ? error.response.data : error.message);
        //throw error;
        return -1
    }
};

const updateUserEmail = async (email) => {
    var token = await getToken("alexv", process.env.WP_PASSWORD);
    const userId = await getUserIdByEmail(email,token)
    if (userId == -1){
        return
    }
    try {
        const url = `https://trainerday.com/wp-json/wp/v2/users/${userId}`;
        const guid = uuidv4();

        // Define the update data
        const data = {
            email: guid + '@example.com',
            password: guid
        };

        // Send PUT request to update user's email
        const response = await axios({
            method: 'put',
            url: url,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            data: data
        });

        console.log(`User email updated successfully: ${response.data.email}`);
    } catch (error) {
        console.log('Error updating WP user email:', error.response ? error.response.data : error.message);
    }
};

module.exports = updateUserEmail

// Example usage
//const email = 'strupish@gmail.com';
//updateUserEmail(email).then(() => {});



//var email = 'thebigbadwolfguy@gmail.com'
//deleteWPUser(email).then(() => {})
    