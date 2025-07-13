const discourseUrl = 'https://forums.trainerday.com';
const adminUsername = 'system';
const axios = require('axios');
var dotenv = require('dotenv') 
dotenv.config();

const apiKey = process.env.DISCORSE;


const getUserIdByEmail = async (email) => {
    try {
        url =`${discourseUrl}/admin/users/list/all.json?filter=${email}`;
        const response = await axios.get(url, {
        headers: {
          'Api-Key': apiKey,
          'Api-Username': adminUsername
        }
      });
      return response.data[0].id;
    } catch (error) {
      console.error('Error Discourse fetching user ID:', error.response?.status, error.response?.data);
      return null;
    }
  };
  
  const deleteUserById = async (userId) => {
    try {
      const response = await axios.delete(`${discourseUrl}/admin/users/${userId}.json`, {
        headers: {
          'Api-Key': apiKey,
          'Api-Username': adminUsername,
          'Content-Type': 'application/json'
        }
      });
      console.log('Discourse User deleted successfully');
    } catch (error) {
      console.error('Error deleting Discourse user:', error.response?.status, error.response?.data);
    }
  };
  
  const deleteDiscourseUserByEmail = async (email) => {
    const userId = await getUserIdByEmail(email);
    if (userId) {
      await deleteUserById(userId);
    } else {
      console.error('Discourse User not found');
    }
  };
  
//const userEmail = 'mail@ptom.de';
//deleteDiscourseUserByEmail(userEmail);

module.exports = deleteDiscourseUserByEmail
