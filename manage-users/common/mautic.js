var axios =require('axios')
var dotenv = require('dotenv') 
dotenv.config();

var basicAuth = `Basic ${process.env.MAUTIC_API_KEY}`
var headers = {headers: { 'Authorization': basicAuth}}
var mauticBaseUrl = 'https://crm.trainerday.com'; // Your Mautic base URL

async function getContactIdByEmail(email) {
    var dataOut= {email: email}
    var url3 = 'https://crm.trainerday.com/api/contacts/new'
    var response3 = await axios.post(url3, dataOut, {headers: { 'Authorization': basicAuth, 'Content-Type': 'application/json' }})
    var id2 = response3.data.contact.id
    return id2
}

async function updateContactDNC(contactId, method = 'add') {
    var url = `${mauticBaseUrl}/api/contacts/${contactId}/dnc/email/${method}`;

    try {
        var response = await axios.post(url,{},headers);
        return response.data;
    } catch (error) {
        console.error('Error unsubscribing contact:', error.response ? error.response.data : error.message);
        throw error;
    }
}

/**
 * Unsubscribes a user from all emails based on their email address.
 * @param {string} email - The email address of the user to unsubscribe.
 */
async function unsubscribeMauticUser(email){
    await unsubscribeSubscribeUser(email, 'add');
}
async function subscribeMauticUser(email){
    await unsubscribeSubscribeUser(email, 'remove');
}

async function unsubscribeSubscribeUser(email, method = 'add') {
    try {
        var contactId = await getContactIdByEmail(email);
        await updateContactDNC(contactId,method);
        console.log('User unsubscribed successfully');
        console.log('mautic_id:', contactId)
    } catch (error) {
        console.error('Error unsubscribing user:', error.message);
    }
}

module.exports = unsubscribeMauticUser;


// Example usage: Unsubscribe a user with the email 'user@example.com'

//unsubscribeMauticUser('thebigbadwolfguy@gmail.com');

//subscribeUser('av@totxt.net');


