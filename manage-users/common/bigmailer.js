var bigmailer = require('@api/bigmailer')

var brandId = '55e9e9e3-0564-41c1-ba79-faa7516c009d';
bigmailer.auth(process.env.BIGMAILER_API_KEY);

async function findContact(email){
    var response = await bigmailer.upsertContact({
        unsubscribe_all: false,
        email: email
        }, {
            validate: 'false',
            brand_id: brandId
        })
    return response.data;
}

async function getContact(contactId){
    var response = await bigmailer.getContact({brand_id: brandId, contact_id: contactId})
    console.log(response.data);
}

async function unsubscribeBigMailer(email){
    try{
        var contact = await findContact(email)
        var contactId = contact.id
        //var details = await getContact(contactId)
        var response = await bigmailer.updateContact({unsubscribe_all: true}, {brand_id: brandId, contact_id: contactId})
        //console.log(response.data);
        console.log(`BigMailer: ${email} unsubscribed`);
    }catch(error){
        console.error(error);
    }
}

module.exports = unsubscribeBigMailer