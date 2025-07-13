declare const CreateBrand: {
    readonly body: {
        readonly title: "CreateBrandPayload";
        readonly properties: {
            readonly name: {
                readonly description: "Name of the brand";
                readonly type: "string";
                readonly minLength: 1;
                readonly maxLength: 50;
                readonly examples: readonly ["BigMailer Co"];
            };
            readonly from_name: {
                readonly description: "Default name used in the \"From:\" header in campaigns sent from this brand.";
                readonly type: "string";
                readonly examples: readonly ["Chris"];
            };
            readonly from_email: {
                readonly description: "Default email used in the \"From:\" header in campaigns sent from this brand.";
                readonly type: "string";
                readonly format: "email";
                readonly examples: readonly ["chris@bigmailer.io"];
            };
            readonly bounce_danger_percent: {
                readonly description: "An integer percentage (0-100). If a bulk campaign in the brand reaches this threshold percent of bounces, it is paused automatically.";
                readonly type: "integer";
                readonly minimum: 1;
                readonly maximum: 15;
                readonly default: 8;
                readonly examples: readonly [15];
            };
            readonly max_soft_bounces: {
                readonly description: "The maximum number of times a contact can soft bounce before it is considered undeliverable. Set to 0 to remove the limit on soft bounces.";
                readonly type: "integer";
                readonly minimum: 0;
                readonly maximum: 20;
                readonly default: 12;
                readonly examples: readonly [5];
            };
            readonly url: {
                readonly description: "URL of a website associated with the brand";
                readonly type: "string";
                readonly format: "url";
                readonly examples: readonly ["https://www.bigmailer.io/"];
            };
            readonly unsubscribe_text: {
                readonly description: "A message displayed to contacts on the brand unsubscribe page.";
                readonly type: "string";
                readonly examples: readonly ["Sorry to see you go!"];
            };
            readonly contact_limit: {
                readonly description: "The maxmimum number of contacts the brand is allowed to contain.";
                readonly type: "integer";
                readonly minimum: 0;
                readonly maximum: 1000000000;
                readonly multipleOf: 1000;
                readonly examples: readonly [50000];
            };
            readonly logo: {
                readonly description: "A base64 encoded JPEG, PNG, or GIF image identified with the brand.";
                readonly type: "string";
                readonly format: "byte";
                readonly examples: readonly ["R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"];
            };
            readonly connection_id: {
                readonly description: "ID of the connection used to send emails";
                readonly type: "string";
                readonly format: "uuid";
                readonly examples: readonly ["562f699c-dbd0-4047-907c-218a2b482220"];
            };
        };
        readonly required: readonly ["name", "from_name", "from_email"];
        readonly type: "object";
        readonly $schema: "http://json-schema.org/draft-04/schema#";
    };
    readonly response: {
        readonly "200": {
            readonly title: "CreateBrandResult";
            readonly description: "Result of creating a brand";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the brand inserted";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["3887bafa-1929-4065-8e0d-9684dabbe118"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const CreateBulkCampaign: {
    readonly body: {
        readonly title: "CreateBulkCampaignPayload";
        readonly properties: {
            readonly name: {
                readonly description: "Name of the campaign";
                readonly type: "string";
                readonly examples: readonly ["March 2022 Campaign"];
            };
            readonly subject: {
                readonly description: "Subject line for the campaign";
                readonly type: "string";
                readonly examples: readonly ["The January Newsletter"];
            };
            readonly from: {
                readonly properties: {
                    readonly email: {
                        readonly description: "From email address";
                        readonly type: "string";
                        readonly format: "email";
                        readonly examples: readonly ["chris@bigmailer.io"];
                    };
                    readonly name: {
                        readonly description: "From name";
                        readonly type: "string";
                        readonly examples: readonly ["March 2022 Campaign"];
                    };
                };
                readonly type: "object";
            };
            readonly recipient_name: {
                readonly description: "Name of the recipient. Use merge tags to make it more personal and avoid spam filters.";
                readonly type: "string";
                readonly examples: readonly ["*|FIRST_NAME|*"];
            };
            readonly reply_to: {
                readonly properties: {
                    readonly email: {
                        readonly description: "Reply to email address";
                        readonly type: "string";
                        readonly format: "email";
                        readonly examples: readonly ["chris@bigmailer.io"];
                    };
                    readonly name: {
                        readonly description: "Reply to name";
                        readonly type: "string";
                        readonly examples: readonly ["March 2022 Campaign"];
                    };
                };
                readonly type: "object";
            };
            readonly link_params: {
                readonly description: "Additional query string parameters to add to all links in the template.";
                readonly type: "string";
                readonly examples: readonly ["utm_campaign=spring_sale&utm_medium=cpc"];
            };
            readonly preview: {
                readonly description: "Copy shown following your subject line in many email clients.";
                readonly type: "string";
                readonly examples: readonly ["Hurry, 50% Off for 2 Days Only!"];
            };
            readonly html: {
                readonly description: "HTML body of the email.";
                readonly type: "string";
                readonly examples: readonly ["<p>This is the html body.</p>"];
            };
            readonly text: {
                readonly description: "Text body of the email.";
                readonly type: "string";
                readonly examples: readonly ["This is the text body."];
            };
            readonly track_opens: {
                readonly description: "True to enable open tracking (HTML campaigns only).";
                readonly type: "boolean";
                readonly examples: readonly [true];
            };
            readonly track_clicks: {
                readonly description: "True to enable click tracking in HTML links.";
                readonly type: "boolean";
                readonly examples: readonly [true];
            };
            readonly track_text_clicks: {
                readonly description: "True to enable click tracking in text links.";
                readonly type: "boolean";
                readonly examples: readonly [true];
            };
            readonly segment_id: {
                readonly description: "ID of a segment used to filter the lists of contacts the campaign is sent to.";
                readonly type: "string";
                readonly format: "uuid";
                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
            };
            readonly message_type_id: {
                readonly description: "ID of the message type of the campaign.";
                readonly type: "string";
                readonly format: "uuid";
                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
            };
            readonly list_ids: {
                readonly description: "An array of list ids to send the campaign to.";
                readonly items: {
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                };
                readonly type: "array";
                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
            };
            readonly excluded_list_ids: {
                readonly description: "An array of list ids to exclude from the campaign. Any contacts on these lists will not be sent the campaign.";
                readonly items: {
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["9b480ee4-cddd-4f11-92d2-15f7d0f18f9c"];
                };
                readonly type: "array";
                readonly examples: readonly ["9b480ee4-cddd-4f11-92d2-15f7d0f18f9c"];
            };
            readonly scheduled_for: {
                readonly description: "Time at which to send the campaign. Measured in seconds since the UNIX epoch. Omit to send the campaign immediately.";
                readonly type: "integer";
                readonly examples: readonly [1568654293];
            };
            readonly throttling_type: {
                readonly description: "Set to `none` to send the campaign as fast as possible. Set to `burst` to send the campaign in small batches over time.";
                readonly type: "string";
                readonly enum: readonly ["none", "burst"];
                readonly examples: readonly ["burst"];
            };
            readonly throttling_amount: {
                readonly description: "Number of emails to send in each per batch. Must be a multiple of 1000. Required if `throttling_type` is `burst`.";
                readonly type: "integer";
                readonly multipleOf: 1000;
                readonly minimum: 1000;
                readonly maximum: 1000000;
                readonly examples: readonly [1000];
            };
            readonly throttling_period: {
                readonly description: "Time in seconds between sending each batch of emails. Required if `throttling_type` is `burst`.";
                readonly type: "integer";
                readonly enum: readonly [900, 1800, 3600, 7200];
                readonly examples: readonly [900];
            };
            readonly suppression_list_id: {
                readonly description: "ID of a suppression list. Any emails in the suppression list will not be sent the campaign.";
                readonly type: "string";
                readonly format: "uuid";
                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
            };
            readonly ready: {
                readonly description: "Set to true to send or schedule the campaign. The campaign will not be sent or scheduled until activated by setting ready to true.";
                readonly type: "boolean";
                readonly examples: readonly [true];
            };
        };
        readonly required: readonly ["name"];
        readonly type: "object";
        readonly $schema: "http://json-schema.org/draft-04/schema#";
    };
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to create a campaign in";
                };
            };
            readonly required: readonly ["brand_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "CreateBulkCampaignResult";
            readonly description: "Result of creating a bulk campaign";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the bulk campaign created.";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["3887bafa-1929-4065-8e0d-9684dabbe118"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "422": {
            readonly title: "Precondition failed error";
            readonly description: "The operation was rejected because the system is not in a state required for the operation's execution.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["failed_precondition"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The campaign cannot be sent in it's current state."];
                };
                readonly preconditions: {
                    readonly description: "A list of codes to aid in handling the error programatically.";
                    readonly items: {
                        readonly type: "string";
                        readonly examples: readonly ["subject.format"];
                    };
                    readonly type: "array";
                    readonly examples: readonly ["subject.format", "lists.length"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const CreateContact: {
    readonly body: {
        readonly title: "CreateContactPayload";
        readonly properties: {
            readonly email: {
                readonly description: "Email address of the contact";
                readonly format: "email";
                readonly maxLength: 100;
                readonly minLength: 1;
                readonly type: "string";
                readonly examples: readonly ["chris@bigmailer.io"];
            };
            readonly field_values: {
                readonly description: "Field values are saved along with the email as part of the contact.\n\nEach name must match the tag name of a field that exists in the brand.\n\nEach field value must have exactly one of string, integer, or date.\n\n";
                readonly items: {
                    readonly title: "FieldValuePayload";
                    readonly properties: {
                        readonly date: {
                            readonly format: "date";
                            readonly type: "string";
                            readonly examples: readonly ["2019-11-27"];
                        };
                        readonly integer: {
                            readonly format: "int64";
                            readonly type: "integer";
                            readonly examples: readonly [4995590933000642000];
                            readonly minimum: -9223372036854776000;
                            readonly maximum: 9223372036854776000;
                        };
                        readonly name: {
                            readonly type: "string";
                            readonly examples: readonly ["FIRST NAME"];
                        };
                        readonly string: {
                            readonly type: "string";
                            readonly examples: readonly ["Christopher"];
                        };
                    };
                    readonly required: readonly ["name"];
                    readonly type: "object";
                };
                readonly type: "array";
            };
            readonly list_ids: {
                readonly description: "IDs of lists the contact should be added to";
                readonly items: {
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                };
                readonly type: "array";
                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
            };
            readonly unsubscribe_all: {
                readonly default: false;
                readonly description: "Set to true to unsubscribe the contact from all future campaigns, regardless of message type.";
                readonly type: "boolean";
                readonly examples: readonly [true];
            };
            readonly unsubscribe_ids: {
                readonly description: "IDs of message types the contact should be unsubscribed from.";
                readonly items: {
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["23f4c393-7556-4317-a38e-e0b0e60e6c8a"];
                };
                readonly type: "array";
                readonly examples: readonly ["23f4c393-7556-4317-a38e-e0b0e60e6c8a"];
            };
        };
        readonly required: readonly ["email"];
        readonly type: "object";
        readonly $schema: "http://json-schema.org/draft-04/schema#";
    };
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to create the contact in";
                };
            };
            readonly required: readonly ["brand_id"];
        }, {
            readonly type: "object";
            readonly properties: {
                readonly validate: {
                    readonly type: "string";
                    readonly enum: readonly [true, false];
                    readonly default: false;
                    readonly description: "Set to true to validate the email for deliverability before adding the contact. Validation credits must be purchased before using this feature. The API does not add the contact and returns an error if the email is undeliverable.";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                };
            };
            readonly required: readonly [];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "CreateContactResult";
            readonly description: "Result of creating a contact";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the contact inserted";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["3887bafa-1929-4065-8e0d-9684dabbe118"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "422": {
            readonly title: "Contact Exists Error";
            readonly description: "The contact already exists.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Contact already exists with this email."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_already_exists"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const CreateField: {
    readonly body: {
        readonly title: "CreateFieldPayload";
        readonly properties: {
            readonly name: {
                readonly description: "Name of the field";
                readonly type: "string";
                readonly minLength: 1;
                readonly maxLength: 50;
                readonly pattern: "^\\s*\\S.*$";
                readonly examples: readonly ["First Name"];
            };
            readonly merge_tag_name: {
                readonly description: "Name used to reference a field's value via a template or the API.  For example, if merge_tag_name is FIRST_NAME, the field can be  referenced using `*|FIRST_NAME|*` in a template or  `{\"name\": \"FIRST_NAME\", \"string\": \"\"}` via the API.\n";
                readonly type: "string";
                readonly maxLength: 50;
                readonly pattern: "^\\s*\\S.*$";
                readonly examples: readonly ["FIRST_NAME"];
            };
            readonly sample_value: {
                readonly description: "A value used for the field when sending test campaigns.";
                readonly type: "string";
                readonly maxLength: 50;
                readonly examples: readonly ["Christopher"];
            };
            readonly type: {
                readonly description: "Type of the field";
                readonly type: "string";
                readonly enum: readonly ["date", "integer", "text"];
                readonly examples: readonly ["text"];
            };
        };
        readonly required: readonly ["name", "type"];
        readonly type: "object";
        readonly $schema: "http://json-schema.org/draft-04/schema#";
    };
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to create a field in";
                };
            };
            readonly required: readonly ["brand_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "CreateFieldResult";
            readonly description: "Result of creating a field";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the field created";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["3887bafa-1929-4065-8e0d-9684dabbe118"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "422": {
            readonly title: "Field Exists Error";
            readonly description: "A field already exists with the chosen merge tag name.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Field already exists with this merge_tag_name."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_already_exists"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const CreateList: {
    readonly body: {
        readonly title: "CreateListPayload";
        readonly properties: {
            readonly name: {
                readonly description: "Name of the list";
                readonly type: "string";
                readonly minLength: 1;
                readonly maxLength: 50;
                readonly examples: readonly ["High Engagement Contacts"];
            };
        };
        readonly required: readonly ["name"];
        readonly type: "object";
        readonly $schema: "http://json-schema.org/draft-04/schema#";
    };
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to create a list in";
                };
            };
            readonly required: readonly ["brand_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "CreateListResult";
            readonly description: "Result of creating a list";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the list inserted";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["3887bafa-1929-4065-8e0d-9684dabbe118"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const CreateSuppressionList: {
    readonly body: {
        readonly type: "object";
        readonly properties: {
            readonly file: {
                readonly description: "A CSV file containing email addresses in the first column of each row.";
                readonly type: "string";
                readonly format: "binary";
            };
        };
        readonly required: readonly ["file"];
        readonly $schema: "http://json-schema.org/draft-04/schema#";
    };
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to upload a suppression list in";
                };
            };
            readonly required: readonly ["brand_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "CreateSuppressionListResult";
            readonly description: "Result of creating a suppression list";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the suppression list created.";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["3887bafa-1929-4065-8e0d-9684dabbe118"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const CreateTransactionalCampaign: {
    readonly body: {
        readonly title: "CreateTransactionalCampaignPayload";
        readonly properties: {
            readonly name: {
                readonly description: "Name of the campaign";
                readonly type: "string";
                readonly examples: readonly ["March 2022 Campaign"];
            };
            readonly subject: {
                readonly description: "Subject line for the campaign";
                readonly type: "string";
                readonly examples: readonly ["The January Newsletter"];
            };
            readonly from: {
                readonly properties: {
                    readonly email: {
                        readonly description: "From email address";
                        readonly type: "string";
                        readonly format: "email";
                        readonly examples: readonly ["chris@bigmailer.io"];
                    };
                    readonly name: {
                        readonly description: "From name";
                        readonly type: "string";
                        readonly examples: readonly ["March 2022 Campaign"];
                    };
                };
                readonly type: "object";
            };
            readonly recipient_name: {
                readonly description: "Name of the recipient. Use merge tags to make it more personal and avoid spam filters.";
                readonly type: "string";
                readonly examples: readonly ["*|FIRST_NAME|*"];
            };
            readonly reply_to: {
                readonly properties: {
                    readonly email: {
                        readonly description: "Reply to email address";
                        readonly type: "string";
                        readonly format: "email";
                        readonly examples: readonly ["chris@bigmailer.io"];
                    };
                    readonly name: {
                        readonly description: "Reply to name";
                        readonly type: "string";
                        readonly examples: readonly ["March 2022 Campaign"];
                    };
                };
                readonly type: "object";
            };
            readonly link_params: {
                readonly description: "Additional query string parameters to add to all links in the template.";
                readonly type: "string";
                readonly examples: readonly ["utm_campaign=spring_sale&utm_medium=cpc"];
            };
            readonly preview: {
                readonly description: "Copy shown following your subject line in many email clients.";
                readonly type: "string";
                readonly examples: readonly ["Hurry, 50% Off for 2 Days Only!"];
            };
            readonly html: {
                readonly description: "HTML body of the email.";
                readonly type: "string";
                readonly examples: readonly ["<p>This is the html body.</p>"];
            };
            readonly text: {
                readonly description: "Text body of the email.";
                readonly type: "string";
                readonly examples: readonly ["This is the text body."];
            };
            readonly track_opens: {
                readonly description: "True to enable open tracking (HTML campaigns only).";
                readonly type: "boolean";
                readonly examples: readonly [true];
            };
            readonly track_clicks: {
                readonly description: "True to enable click tracking in HTML links.";
                readonly type: "boolean";
                readonly examples: readonly [true];
            };
            readonly track_text_clicks: {
                readonly description: "True to enable click tracking in text links.";
                readonly type: "boolean";
                readonly examples: readonly [true];
            };
            readonly message_type_id: {
                readonly description: "ID of the message type of the campaign.";
                readonly type: "string";
                readonly format: "uuid";
                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
            };
            readonly list_id: {
                readonly description: "ID of a list contacts sent the transactional campaign should be added to.";
                readonly type: "string";
                readonly format: "uuid";
                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
            };
            readonly ready: {
                readonly description: "Set to true to activate the campaign. The campaign cannot be sent until activated by setting ready to true.";
                readonly type: "boolean";
                readonly examples: readonly [true];
            };
        };
        readonly required: readonly ["name"];
        readonly type: "object";
        readonly $schema: "http://json-schema.org/draft-04/schema#";
    };
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to create a campaign in";
                };
            };
            readonly required: readonly ["brand_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "CreateTransactionalCampaignResult";
            readonly description: "Result of creating a transactional campaign";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the transactional campaign created.";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["3887bafa-1929-4065-8e0d-9684dabbe118"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "422": {
            readonly title: "Precondition failed error";
            readonly description: "The operation was rejected because the system is not in a state required for the operation's execution.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["failed_precondition"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The campaign cannot be sent in it's current state."];
                };
                readonly preconditions: {
                    readonly description: "A list of codes to aid in handling the error programatically.";
                    readonly items: {
                        readonly type: "string";
                        readonly examples: readonly ["subject.format"];
                    };
                    readonly type: "array";
                    readonly examples: readonly ["subject.format", "lists.length"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const CreateUser: {
    readonly body: {
        readonly title: "CreateUserPayload";
        readonly properties: {
            readonly role: {
                readonly description: "The user role determines what actions the user may perform. See our [description of user roles](https://docs.bigmailer.io/docs/user-types-and-permissions).";
                readonly type: "string";
                readonly enum: readonly ["admin", "account_manager", "brand_manager", "campaign_manager", "template_manager"];
                readonly examples: readonly ["brand_manager"];
            };
            readonly email: {
                readonly description: "User's email address";
                readonly type: "string";
                readonly format: "email";
                readonly examples: readonly ["chris@bigmailer.io"];
            };
            readonly allowed_brands: {
                readonly description: "A list of brand IDs the user is allowed to access. Only relevant if the role is brand_manager, campaign_manager, or template_manager.";
                readonly items: {
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                };
                readonly type: "array";
                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
            };
            readonly invitation_message: {
                readonly description: "A message to include in the invitation email.";
                readonly type: "string";
                readonly examples: readonly ["Please join our account."];
            };
        };
        readonly required: readonly ["email", "role"];
        readonly type: "object";
        readonly $schema: "http://json-schema.org/draft-04/schema#";
    };
    readonly response: {
        readonly "200": {
            readonly title: "CreateUserResult";
            readonly description: "Result of creating a user";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the user inserted";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["3887bafa-1929-4065-8e0d-9684dabbe118"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "422": {
            readonly title: "User Exists Error";
            readonly description: "The user already exists.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["User already exists with this email."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_already_exists"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const DeleteContact: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to delete the contact from";
                };
                readonly contact_id: {
                    readonly type: "string";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID or email address of the contact";
                };
            };
            readonly required: readonly ["brand_id", "contact_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "DeleteContactResult";
            readonly description: "Result of deleting a contact";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the contact deleted";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const DeleteField: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand";
                };
                readonly field_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the field";
                };
            };
            readonly required: readonly ["brand_id", "field_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "DeleteFieldResult";
            readonly description: "Result of deleting a field";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the field deleted";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const DeleteList: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand";
                };
                readonly list_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the list";
                };
            };
            readonly required: readonly ["brand_id", "list_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "DeleteListResult";
            readonly description: "Result of deleting a list";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the list deleted";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const DeleteUser: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly user_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the user";
                };
            };
            readonly required: readonly ["user_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "DeleteUserResult";
            readonly description: "Result of deleting a user";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the user deleted";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const GetBrand: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to get";
                };
            };
            readonly required: readonly ["brand_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "GetBrandResult";
            readonly description: "Result of getting a brand";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the brand";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                };
                readonly name: {
                    readonly description: "Name of the brand";
                    readonly type: "string";
                    readonly examples: readonly ["My Company Ltd"];
                };
                readonly from_name: {
                    readonly description: "Default name used in the \"From:\" header in campaigns sent from this brand.";
                    readonly type: "string";
                    readonly examples: readonly ["Christopher"];
                };
                readonly from_email: {
                    readonly description: "Default email used in the \"From:\" header in campaigns sent from this brand.";
                    readonly format: "email";
                    readonly type: "string";
                    readonly examples: readonly ["chris@example.com"];
                };
                readonly filter_soft_bounces: {
                    readonly description: "true if campaigns sent from this brand should exclude contacts with more than `max_soft_bounces` soft bounces, false otherwise.";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly max_soft_bounces: {
                    readonly description: "if filter_soft_bounces is true, the maximum number of times a contact can soft bounce before it is considered undeliverable.";
                    readonly type: "integer";
                    readonly examples: readonly [5];
                };
                readonly bounce_danger_percent: {
                    readonly description: "An integer percentage (0-100). If a bulk campaign in the brand reaches this threshold percent of bounces, it is paused automatically.";
                    readonly type: "integer";
                    readonly examples: readonly [15];
                };
                readonly unsubscribe_text: {
                    readonly description: "A message displayed to contacts on the brand unsubscribe page.";
                    readonly type: "string";
                    readonly examples: readonly ["Sorry to see you go!"];
                };
                readonly connection_id: {
                    readonly description: "ID of the connection used to send emails";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["2aef2dd2-ab14-453a-aadc-01f3699ed85a"];
                };
                readonly contact_limit: {
                    readonly description: "The maxmimum number of contacts the brand is allowed to contain.";
                    readonly type: "integer";
                    readonly examples: readonly [50000];
                };
                readonly url: {
                    readonly description: "URL of a website associated with the brand";
                    readonly type: "string";
                    readonly examples: readonly ["http://www.example.com/"];
                };
                readonly created: {
                    readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                    readonly type: "integer";
                    readonly examples: readonly [1592422352];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const GetBulkCampaign: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand";
                };
                readonly campaign_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the campaign";
                };
            };
            readonly required: readonly ["brand_id", "campaign_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "GetBulkCampaignResult";
            readonly description: "Result of getting a bulk campaign";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the campaign";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                };
                readonly name: {
                    readonly description: "Name of the campaign";
                    readonly type: "string";
                    readonly examples: readonly ["March 2022 Campaign"];
                };
                readonly created: {
                    readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                    readonly type: "integer";
                    readonly examples: readonly [1592422352];
                };
                readonly subject: {
                    readonly description: "Subject line for the campaign";
                    readonly type: "string";
                    readonly examples: readonly ["The January Newsletter"];
                };
                readonly from: {
                    readonly properties: {
                        readonly email: {
                            readonly description: "From email address";
                            readonly type: "string";
                            readonly format: "email";
                            readonly examples: readonly ["chris@bigmailer.io"];
                        };
                        readonly name: {
                            readonly description: "From name";
                            readonly type: "string";
                            readonly examples: readonly ["March 2022 Campaign"];
                        };
                    };
                    readonly type: "object";
                };
                readonly recipient_name: {
                    readonly description: "Name of the recipient. Use merge tags to make it more personal and avoid spam filters.";
                    readonly type: "string";
                    readonly examples: readonly ["*|FIRST_NAME|*"];
                };
                readonly reply_to: {
                    readonly properties: {
                        readonly email: {
                            readonly description: "Reply to email address";
                            readonly type: "string";
                            readonly format: "email";
                            readonly examples: readonly ["chris@bigmailer.io"];
                        };
                        readonly name: {
                            readonly description: "Reply to name";
                            readonly type: "string";
                            readonly examples: readonly ["March 2022 Campaign"];
                        };
                    };
                    readonly type: "object";
                };
                readonly link_params: {
                    readonly description: "Additional query string parameters to add to all links in the template.";
                    readonly type: "string";
                    readonly examples: readonly ["utm_campaign=spring_sale&utm_medium=cpc"];
                };
                readonly preview: {
                    readonly description: "Copy shown following your subject line in many email clients.";
                    readonly type: "string";
                    readonly examples: readonly ["Hurry, 50% Off for 2 Days Only!"];
                };
                readonly html: {
                    readonly description: "HTML body of the email.";
                    readonly type: "string";
                    readonly examples: readonly ["<p>This is the html body.</p>"];
                };
                readonly text: {
                    readonly description: "Text body of the email.";
                    readonly type: "string";
                    readonly examples: readonly ["This is the text body."];
                };
                readonly track_opens: {
                    readonly description: "True to enable open tracking (HTML campaigns only).";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly track_clicks: {
                    readonly description: "True to enable click tracking in HTML links.";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly track_text_clicks: {
                    readonly description: "True to enable click tracking in text links.";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly segment_id: {
                    readonly description: "ID of a segment used to filter the lists of contacts the campaign is sent to.";
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                };
                readonly message_type_id: {
                    readonly description: "ID of the message type of the campaign.";
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                };
                readonly list_ids: {
                    readonly description: "An array of list ids to send the campaign to.";
                    readonly items: {
                        readonly format: "uuid";
                        readonly type: "string";
                        readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                    };
                    readonly type: "array";
                    readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                };
                readonly excluded_list_ids: {
                    readonly description: "An array of list ids to exclude from the campaign. Any contacts on these lists will not be sent the campaign.";
                    readonly items: {
                        readonly format: "uuid";
                        readonly type: "string";
                        readonly examples: readonly ["9b480ee4-cddd-4f11-92d2-15f7d0f18f9c"];
                    };
                    readonly type: "array";
                    readonly examples: readonly ["9b480ee4-cddd-4f11-92d2-15f7d0f18f9c"];
                };
                readonly scheduled_for: {
                    readonly description: "Time at which to send the campaign. Measured in seconds since the UNIX epoch. Omit to send the campaign immediately.";
                    readonly type: "integer";
                    readonly examples: readonly [1568654293];
                };
                readonly throttling_type: {
                    readonly description: "Set to `none` to send the campaign as fast as possible. Set to `burst` to send the campaign in small batches over time.\n\n`none` `burst`";
                    readonly type: "string";
                    readonly enum: readonly ["none", "burst"];
                    readonly examples: readonly ["burst"];
                };
                readonly throttling_amount: {
                    readonly description: "Number of emails to send in each per batch. Must be a multiple of 1000. Required if `throttling_type` is `burst`.";
                    readonly type: "integer";
                    readonly multipleOf: 1000;
                    readonly minimum: 1000;
                    readonly maximum: 1000000;
                    readonly examples: readonly [1000];
                };
                readonly throttling_period: {
                    readonly description: "Time in seconds between sending each batch of emails. Required if `throttling_type` is `burst`.\n\n`900` `1800` `3600` `7200`";
                    readonly type: "integer";
                    readonly enum: readonly [900, 1800, 3600, 7200];
                    readonly examples: readonly [900];
                };
                readonly suppression_list_id: {
                    readonly description: "ID of a suppression list. Any emails in the suppression list will not be sent the campaign.";
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                };
                readonly num_sent: {
                    readonly description: "Number of emails sent.";
                    readonly type: "integer";
                    readonly examples: readonly [100];
                };
                readonly num_rejected: {
                    readonly description: "Number of emails rejected.";
                    readonly type: "integer";
                    readonly examples: readonly [10];
                };
                readonly num_clicks: {
                    readonly description: "Number of unique clicks.";
                    readonly type: "integer";
                    readonly examples: readonly [20];
                };
                readonly num_total_clicks: {
                    readonly description: "Number of total clicks (non-unique).";
                    readonly type: "integer";
                    readonly examples: readonly [30];
                };
                readonly num_opens: {
                    readonly description: "Number of unique opens.";
                    readonly type: "integer";
                    readonly examples: readonly [50];
                };
                readonly num_total_opens: {
                    readonly description: "Number of total opens (non-unique).";
                    readonly type: "integer";
                    readonly examples: readonly [60];
                };
                readonly num_hard_bounces: {
                    readonly description: "Number of emails sent that hard bounced.";
                    readonly type: "integer";
                    readonly examples: readonly [4];
                };
                readonly num_soft_bounces: {
                    readonly description: "Number of emails sent that soft bounced.";
                    readonly type: "integer";
                    readonly examples: readonly [8];
                };
                readonly num_complaints: {
                    readonly description: "Number of emails sent that complained.";
                    readonly type: "integer";
                    readonly examples: readonly [2];
                };
                readonly num_unsubscribes: {
                    readonly description: "Number of emails sent that unsubscribed.";
                    readonly type: "integer";
                    readonly examples: readonly [3];
                };
                readonly status: {
                    readonly description: "Status of the campaign.\n\n`draft` `pending` `in progress` `complete` `error` `paused` `archived` `active`";
                    readonly type: "string";
                    readonly enum: readonly ["draft", "pending", "in progress", "complete", "error", "paused", "archived", "active"];
                    readonly examples: readonly ["draft"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const GetConnection: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly connection_id: {
                    readonly type: "string";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the connection";
                };
            };
            readonly required: readonly ["connection_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "GetConnectionResult";
            readonly description: "Result of getting a connection";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the connection";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                };
                readonly type: {
                    readonly description: "Service type of the connection.\n\n`aws` `elastic_email` `spark_post` `green_arrow` `pro`";
                    readonly enum: readonly ["aws", "elastic_email", "spark_post", "green_arrow", "pro"];
                    readonly type: "string";
                    readonly examples: readonly ["aws"];
                };
                readonly name: {
                    readonly description: "Name of the connection";
                    readonly type: "string";
                    readonly examples: readonly ["AWS us-east-1"];
                };
                readonly created: {
                    readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                    readonly type: "integer";
                    readonly examples: readonly [1592422352];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const GetContact: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to get the contact from";
                };
                readonly contact_id: {
                    readonly type: "string";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID or email address of the contact";
                };
            };
            readonly required: readonly ["brand_id", "contact_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "GetContactResult";
            readonly description: "Result of getting a contact";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the contact";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                };
                readonly brand_id: {
                    readonly description: "ID of the brand the contact is in";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["2aef2dd2-ab14-453a-aadc-01f3699ed85a"];
                };
                readonly email: {
                    readonly description: "Email address of the contact";
                    readonly format: "email";
                    readonly type: "string";
                    readonly examples: readonly ["chris@bigmailer.io"];
                };
                readonly field_values: {
                    readonly description: "Field values associated with the contact.\n";
                    readonly items: {
                        readonly title: "FieldValuePayload";
                        readonly properties: {
                            readonly date: {
                                readonly format: "date";
                                readonly type: "string";
                                readonly examples: readonly ["2019-11-27"];
                            };
                            readonly integer: {
                                readonly format: "int64";
                                readonly type: "integer";
                                readonly examples: readonly [4995590933000642000];
                                readonly minimum: -9223372036854776000;
                                readonly maximum: 9223372036854776000;
                            };
                            readonly name: {
                                readonly type: "string";
                                readonly examples: readonly ["FIRST NAME"];
                            };
                            readonly string: {
                                readonly type: "string";
                                readonly examples: readonly ["Christopher"];
                            };
                        };
                        readonly required: readonly ["name"];
                        readonly type: "object";
                    };
                    readonly type: "array";
                };
                readonly list_ids: {
                    readonly description: "IDs of the lists the contact is part of.";
                    readonly items: {
                        readonly format: "uuid";
                        readonly type: "string";
                        readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                    };
                    readonly type: "array";
                    readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                };
                readonly unsubscribe_all: {
                    readonly description: "true if the contact has unsubscribed from all message types, false otherwise.";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly unsubscribe_ids: {
                    readonly description: "IDs of message types the contact has unsubscribed from.";
                    readonly items: {
                        readonly format: "uuid";
                        readonly type: "string";
                        readonly examples: readonly ["23f4c393-7556-4317-a38e-e0b0e60e6c8a"];
                    };
                    readonly type: "array";
                    readonly examples: readonly ["23f4c393-7556-4317-a38e-e0b0e60e6c8a"];
                };
                readonly num_soft_bounces: {
                    readonly description: "Number of times a campaign sent to contact's email has soft bounced.";
                    readonly type: "integer";
                    readonly examples: readonly [0];
                };
                readonly num_hard_bounces: {
                    readonly description: "Number of times a campaign sent to contact's email has hard bounced.";
                    readonly type: "integer";
                    readonly examples: readonly [0];
                };
                readonly num_complaints: {
                    readonly description: "Number of times a campaign sent to contact's email has triggered a complaint.";
                    readonly type: "integer";
                    readonly examples: readonly [0];
                };
                readonly created: {
                    readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                    readonly type: "integer";
                    readonly examples: readonly [1592422352];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const GetField: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand";
                };
                readonly field_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the field";
                };
            };
            readonly required: readonly ["brand_id", "field_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "GetFieldResult";
            readonly description: "Result of getting a field";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the field";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                };
                readonly name: {
                    readonly description: "Name of the field";
                    readonly type: "string";
                    readonly examples: readonly ["First Name"];
                };
                readonly type: {
                    readonly description: "Data type of the field.\n\n`date` `email` `integer` `text`";
                    readonly type: "string";
                    readonly enum: readonly ["date", "email", "integer", "text"];
                    readonly examples: readonly ["text"];
                };
                readonly merge_tag_name: {
                    readonly description: "Name used to reference a field's value via a template or the API. For example, if merge_tag_name is FIRST_NAME, the field can be referenced using `*|FIRST_NAME|*` in a template or `{\"name\": \"FIRST_NAME\", \"string\": \"\"}` via the API.\n";
                    readonly type: "string";
                    readonly examples: readonly ["FIRST_NAME"];
                };
                readonly sample_value: {
                    readonly description: "A value used for the field when sending test campaigns.";
                    readonly type: "string";
                    readonly examples: readonly ["Christopher"];
                };
                readonly created: {
                    readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                    readonly type: "integer";
                    readonly examples: readonly [1592422352];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const GetList: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand";
                };
                readonly list_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the list";
                };
            };
            readonly required: readonly ["brand_id", "list_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "GetListResult";
            readonly description: "Result of getting a list";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the list";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                };
                readonly name: {
                    readonly description: "Name of the list";
                    readonly type: "string";
                    readonly examples: readonly ["High Engagement Contacts"];
                };
                readonly all: {
                    readonly description: "true if this list is the special system created list containing all contacts within a brand, false otherwise.";
                    readonly type: "boolean";
                    readonly examples: readonly [false];
                };
                readonly created: {
                    readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                    readonly type: "integer";
                    readonly examples: readonly [1592422352];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const GetSegment: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand";
                };
                readonly segment_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the segment";
                };
            };
            readonly required: readonly ["brand_id", "segment_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "GetSegmentResult";
            readonly description: "Result of getting a segment";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the segment";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                };
                readonly name: {
                    readonly description: "Name of the segment";
                    readonly type: "string";
                    readonly examples: readonly ["Opened Campaign"];
                };
                readonly created: {
                    readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                    readonly type: "integer";
                    readonly examples: readonly [1592422352];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const GetSuppressionList: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand";
                };
                readonly suppression_list_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the suppression list";
                };
            };
            readonly required: readonly ["brand_id", "suppression_list_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "GetSuppressionListResult";
            readonly description: "Result of getting a suppression list";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the suppression list";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                };
                readonly file_name: {
                    readonly description: "File name of the suppression list";
                    readonly type: "string";
                    readonly examples: readonly ["suppressed_contacts.csv"];
                };
                readonly file_size: {
                    readonly description: "Size in bytes of the suppression list";
                    readonly type: "integer";
                    readonly examples: readonly [65536];
                };
                readonly created: {
                    readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                    readonly type: "integer";
                    readonly examples: readonly [1592422352];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const GetTransactionalCampaign: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand";
                };
                readonly campaign_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the campaign";
                };
            };
            readonly required: readonly ["brand_id", "campaign_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "GetTransactionalCampaignResult";
            readonly description: "Result of getting a transactional campaign";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the campaign";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                };
                readonly name: {
                    readonly description: "Name of the campaign";
                    readonly type: "string";
                    readonly examples: readonly ["March 2022 Campaign"];
                };
                readonly created: {
                    readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                    readonly type: "integer";
                    readonly examples: readonly [1592422352];
                };
                readonly subject: {
                    readonly description: "Subject line for the campaign";
                    readonly type: "string";
                    readonly examples: readonly ["The January Newsletter"];
                };
                readonly from: {
                    readonly properties: {
                        readonly email: {
                            readonly description: "From email address";
                            readonly type: "string";
                            readonly format: "email";
                            readonly examples: readonly ["chris@bigmailer.io"];
                        };
                        readonly name: {
                            readonly description: "From name";
                            readonly type: "string";
                            readonly examples: readonly ["March 2022 Campaign"];
                        };
                    };
                    readonly type: "object";
                };
                readonly recipient_name: {
                    readonly description: "Name of the recipient. Use merge tags to make it more personal and avoid spam filters.";
                    readonly type: "string";
                    readonly examples: readonly ["*|FIRST_NAME|*"];
                };
                readonly reply_to: {
                    readonly properties: {
                        readonly email: {
                            readonly description: "Reply to email address";
                            readonly type: "string";
                            readonly format: "email";
                            readonly examples: readonly ["chris@bigmailer.io"];
                        };
                        readonly name: {
                            readonly description: "Reply to name";
                            readonly type: "string";
                            readonly examples: readonly ["March 2022 Campaign"];
                        };
                    };
                    readonly type: "object";
                };
                readonly link_params: {
                    readonly description: "Additional query string parameters to add to all links in the template.";
                    readonly type: "string";
                    readonly examples: readonly ["utm_campaign=spring_sale&utm_medium=cpc"];
                };
                readonly preview: {
                    readonly description: "Copy shown following your subject line in many email clients.";
                    readonly type: "string";
                    readonly examples: readonly ["Hurry, 50% Off for 2 Days Only!"];
                };
                readonly html: {
                    readonly description: "HTML body of the email.";
                    readonly type: "string";
                    readonly examples: readonly ["<p>This is the html body.</p>"];
                };
                readonly text: {
                    readonly description: "Text body of the email.";
                    readonly type: "string";
                    readonly examples: readonly ["This is the text body."];
                };
                readonly track_opens: {
                    readonly description: "True to enable open tracking (HTML campaigns only).";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly track_clicks: {
                    readonly description: "True to enable click tracking in HTML links.";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly track_text_clicks: {
                    readonly description: "True to enable click tracking in text links.";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly message_type_id: {
                    readonly description: "ID of the message type of the campaign.";
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                };
                readonly list_id: {
                    readonly description: "ID of a list contacts sent the transactional campaign should be added to.";
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                };
                readonly num_sent: {
                    readonly description: "Number of emails sent.";
                    readonly type: "integer";
                    readonly examples: readonly [100];
                };
                readonly num_rejected: {
                    readonly description: "Number of emails rejected.";
                    readonly type: "integer";
                    readonly examples: readonly [10];
                };
                readonly num_clicks: {
                    readonly description: "Number of unique clicks.";
                    readonly type: "integer";
                    readonly examples: readonly [20];
                };
                readonly num_total_clicks: {
                    readonly description: "Number of total clicks (non-unique).";
                    readonly type: "integer";
                    readonly examples: readonly [30];
                };
                readonly num_opens: {
                    readonly description: "Number of unique opens.";
                    readonly type: "integer";
                    readonly examples: readonly [50];
                };
                readonly num_total_opens: {
                    readonly description: "Number of total opens (non-unique).";
                    readonly type: "integer";
                    readonly examples: readonly [60];
                };
                readonly num_hard_bounces: {
                    readonly description: "Number of emails sent that hard bounced.";
                    readonly type: "integer";
                    readonly examples: readonly [4];
                };
                readonly num_soft_bounces: {
                    readonly description: "Number of emails sent that soft bounced.";
                    readonly type: "integer";
                    readonly examples: readonly [8];
                };
                readonly num_complaints: {
                    readonly description: "Number of emails sent that complained.";
                    readonly type: "integer";
                    readonly examples: readonly [2];
                };
                readonly num_unsubscribes: {
                    readonly description: "Number of emails sent that unsubscribed.";
                    readonly type: "integer";
                    readonly examples: readonly [3];
                };
                readonly status: {
                    readonly description: "Status of the campaign.\n\n`draft` `pending` `in progress` `complete` `error` `paused` `archived` `active`";
                    readonly type: "string";
                    readonly enum: readonly ["draft", "pending", "in progress", "complete", "error", "paused", "archived", "active"];
                    readonly examples: readonly ["draft"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const GetUser: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly user_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the user";
                };
            };
            readonly required: readonly ["user_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "GetUserResult";
            readonly description: "Result of getting a user";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the user";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                };
                readonly role: {
                    readonly description: "The user role determines what actions the user may perform. See our [description of user roles](https://docs.bigmailer.io/docs/user-types-and-permissions).\n\n`admin` `account_manager` `brand_manager` `campaign_manager` `template_manager`";
                    readonly type: "string";
                    readonly enum: readonly ["admin", "account_manager", "brand_manager", "campaign_manager", "template_manager"];
                    readonly examples: readonly ["brand_manager"];
                };
                readonly email: {
                    readonly description: "User's email address";
                    readonly type: "string";
                    readonly format: "email";
                    readonly examples: readonly ["chris@bigmailer.io"];
                };
                readonly is_owner: {
                    readonly description: "true if the user is the account owner. An account owner cannot be deleted.";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly is_activated: {
                    readonly description: "true if the user is activated. A user becomes activated by clicking the link in the invitation email.";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly allowed_brands: {
                    readonly description: "A list of brand IDs the user is allowed to access. Only relevant if the role is brand_manager, campaign_manager, or template_manager.";
                    readonly items: {
                        readonly format: "uuid";
                        readonly type: "string";
                        readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                    };
                    readonly type: "array";
                    readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                };
                readonly activated: {
                    readonly description: "Time at which the user was activated. Measured in seconds since the UNIX epoch.";
                    readonly type: "integer";
                    readonly examples: readonly [1592422352];
                };
                readonly created: {
                    readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                    readonly type: "integer";
                    readonly examples: readonly [1592422352];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const ListBrands: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly limit: {
                    readonly type: "integer";
                    readonly default: 10;
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A limit on the number of objects to be returned, between 1 and 100.";
                };
                readonly cursor: {
                    readonly type: "string";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                };
            };
            readonly required: readonly [];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "ListBrandsResult";
            readonly properties: {
                readonly has_more: {
                    readonly description: "Whether or not there are more elements after this set. If `false`, this set comprises the end of the list.";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly cursor: {
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                    readonly type: "string";
                    readonly examples: readonly ["K5pwIGH3hgYrhytbDUY5eQ=="];
                };
                readonly data: {
                    readonly type: "array";
                    readonly items: {
                        readonly properties: {
                            readonly id: {
                                readonly description: "ID of the brand";
                                readonly format: "uuid";
                                readonly type: "string";
                                readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                            };
                            readonly name: {
                                readonly description: "Name of the brand";
                                readonly type: "string";
                                readonly examples: readonly ["My Company Ltd"];
                            };
                            readonly from_name: {
                                readonly description: "Default name used in the \"From:\" header in campaigns sent from this brand.";
                                readonly type: "string";
                                readonly examples: readonly ["Christopher"];
                            };
                            readonly from_email: {
                                readonly description: "Default email used in the \"From:\" header in campaigns sent from this brand.";
                                readonly format: "email";
                                readonly type: "string";
                                readonly examples: readonly ["chris@example.com"];
                            };
                            readonly filter_soft_bounces: {
                                readonly description: "true if campaigns sent from this brand should exclude contacts with more than `max_soft_bounces` soft bounces, false otherwise.";
                                readonly type: "boolean";
                                readonly examples: readonly [true];
                            };
                            readonly max_soft_bounces: {
                                readonly description: "if filter_soft_bounces is true, the maximum number of times a contact can soft bounce before it is considered undeliverable.";
                                readonly type: "integer";
                                readonly examples: readonly [5];
                            };
                            readonly bounce_danger_percent: {
                                readonly description: "An integer percentage (0-100). If a bulk campaign in the brand reaches this threshold percent of bounces, it is paused automatically.";
                                readonly type: "integer";
                                readonly examples: readonly [15];
                            };
                            readonly unsubscribe_text: {
                                readonly description: "A message displayed to contacts on the brand unsubscribe page.";
                                readonly type: "string";
                                readonly examples: readonly ["Sorry to see you go!"];
                            };
                            readonly connection_id: {
                                readonly description: "ID of the connection used to send emails";
                                readonly format: "uuid";
                                readonly type: "string";
                                readonly examples: readonly ["2aef2dd2-ab14-453a-aadc-01f3699ed85a"];
                            };
                            readonly contact_limit: {
                                readonly description: "The maxmimum number of contacts the brand is allowed to contain.";
                                readonly type: "integer";
                                readonly examples: readonly [50000];
                            };
                            readonly url: {
                                readonly description: "URL of a website associated with the brand";
                                readonly type: "string";
                                readonly examples: readonly ["http://www.example.com/"];
                            };
                            readonly created: {
                                readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                                readonly type: "integer";
                                readonly examples: readonly [1592422352];
                            };
                        };
                        readonly type: "object";
                    };
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const ListBulkCampaigns: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to retrieve bulk campaigns from";
                };
            };
            readonly required: readonly ["brand_id"];
        }, {
            readonly type: "object";
            readonly properties: {
                readonly limit: {
                    readonly type: "integer";
                    readonly default: 10;
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A limit on the number of objects to be returned, between 1 and 100.";
                };
                readonly cursor: {
                    readonly type: "string";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                };
            };
            readonly required: readonly [];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "ListBulkCampaignsResult";
            readonly properties: {
                readonly has_more: {
                    readonly description: "Whether or not there are more elements after this set. If `false`, this set comprises the end of the list.";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly cursor: {
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                    readonly type: "string";
                    readonly examples: readonly ["K5pwIGH3hgYrhytbDUY5eQ=="];
                };
                readonly data: {
                    readonly type: "array";
                    readonly items: {
                        readonly properties: {
                            readonly id: {
                                readonly description: "ID of the campaign";
                                readonly format: "uuid";
                                readonly type: "string";
                                readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                            };
                            readonly name: {
                                readonly description: "Name of the campaign";
                                readonly type: "string";
                                readonly examples: readonly ["March 2022 Campaign"];
                            };
                            readonly created: {
                                readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                                readonly type: "integer";
                                readonly examples: readonly [1592422352];
                            };
                            readonly subject: {
                                readonly description: "Subject line for the campaign";
                                readonly type: "string";
                                readonly examples: readonly ["The January Newsletter"];
                            };
                            readonly from: {
                                readonly properties: {
                                    readonly email: {
                                        readonly description: "From email address";
                                        readonly type: "string";
                                        readonly format: "email";
                                        readonly examples: readonly ["chris@bigmailer.io"];
                                    };
                                    readonly name: {
                                        readonly description: "From name";
                                        readonly type: "string";
                                        readonly examples: readonly ["Chris"];
                                    };
                                };
                                readonly type: "object";
                            };
                            readonly recipient_name: {
                                readonly description: "Name of the recipient. Use merge tags to make it more personal and avoid spam filters.";
                                readonly type: "string";
                                readonly examples: readonly ["*|FIRST_NAME|*"];
                            };
                            readonly reply_to: {
                                readonly properties: {
                                    readonly email: {
                                        readonly description: "Reply to email address";
                                        readonly type: "string";
                                        readonly format: "email";
                                        readonly examples: readonly ["chris@bigmailer.io"];
                                    };
                                    readonly name: {
                                        readonly description: "Reply to name";
                                        readonly type: "string";
                                        readonly examples: readonly ["Chris"];
                                    };
                                };
                                readonly type: "object";
                            };
                            readonly link_params: {
                                readonly description: "Additional query string parameters to add to all links in the template.";
                                readonly type: "string";
                                readonly examples: readonly ["utm_campaign=spring_sale&utm_medium=cpc"];
                            };
                            readonly preview: {
                                readonly description: "Copy shown following your subject line in many email clients.";
                                readonly type: "string";
                                readonly examples: readonly ["Hurry, 50% Off for 2 Days Only!"];
                            };
                            readonly track_opens: {
                                readonly description: "True to enable open tracking (HTML campaigns only).";
                                readonly type: "boolean";
                                readonly examples: readonly [true];
                            };
                            readonly track_clicks: {
                                readonly description: "True to enable click tracking in HTML links.";
                                readonly type: "boolean";
                                readonly examples: readonly [true];
                            };
                            readonly track_text_clicks: {
                                readonly description: "True to enable click tracking in text links.";
                                readonly type: "boolean";
                                readonly examples: readonly [true];
                            };
                            readonly segment_id: {
                                readonly description: "ID of a segment used to filter the lists of contacts the campaign is sent to.";
                                readonly type: "string";
                                readonly format: "uuid";
                                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                            };
                            readonly message_type_id: {
                                readonly description: "ID of the message type of the campaign.";
                                readonly type: "string";
                                readonly format: "uuid";
                                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                            };
                            readonly list_ids: {
                                readonly description: "An array of list ids to send the campaign to.";
                                readonly items: {
                                    readonly format: "uuid";
                                    readonly type: "string";
                                    readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                                };
                                readonly type: "array";
                                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                            };
                            readonly excluded_list_ids: {
                                readonly description: "An array of list ids to exclude from the campaign. Any contacts on these lists will not be sent the campaign.";
                                readonly items: {
                                    readonly format: "uuid";
                                    readonly type: "string";
                                    readonly examples: readonly ["9b480ee4-cddd-4f11-92d2-15f7d0f18f9c"];
                                };
                                readonly type: "array";
                                readonly examples: readonly ["9b480ee4-cddd-4f11-92d2-15f7d0f18f9c"];
                            };
                            readonly scheduled_for: {
                                readonly description: "Time at which to send the campaign. Measured in seconds since the UNIX epoch. Omit to send the campaign immediately.";
                                readonly type: "integer";
                                readonly examples: readonly [1568654293];
                            };
                            readonly throttling_type: {
                                readonly description: "Set to `none` to send the campaign as fast as possible. Set to `burst` to send the campaign in small batches over time.\n\n`none` `burst`";
                                readonly type: "string";
                                readonly enum: readonly ["none", "burst"];
                                readonly examples: readonly ["burst"];
                            };
                            readonly throttling_amount: {
                                readonly description: "Number of emails to send in each per batch. Must be a multiple of 1000. Required if `throttling_type` is `burst`.";
                                readonly type: "integer";
                                readonly multipleOf: 1000;
                                readonly minimum: 1000;
                                readonly maximum: 1000000;
                                readonly examples: readonly [1000];
                            };
                            readonly throttling_period: {
                                readonly description: "Time in seconds between sending each batch of emails. Required if `throttling_type` is `burst`.\n\n`900` `1800` `3600` `7200`";
                                readonly type: "integer";
                                readonly enum: readonly [900, 1800, 3600, 7200];
                                readonly examples: readonly [900];
                            };
                            readonly suppression_list_id: {
                                readonly description: "ID of a suppression list. Any emails in the suppression list will not be sent the campaign.";
                                readonly type: "string";
                                readonly format: "uuid";
                                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                            };
                            readonly num_sent: {
                                readonly description: "Number of emails sent.";
                                readonly type: "integer";
                                readonly examples: readonly [100];
                            };
                            readonly num_rejected: {
                                readonly description: "Number of emails rejected.";
                                readonly type: "integer";
                                readonly examples: readonly [10];
                            };
                            readonly num_clicks: {
                                readonly description: "Number of unique clicks.";
                                readonly type: "integer";
                                readonly examples: readonly [20];
                            };
                            readonly num_total_clicks: {
                                readonly description: "Number of total clicks (non-unique).";
                                readonly type: "integer";
                                readonly examples: readonly [30];
                            };
                            readonly num_opens: {
                                readonly description: "Number of unique opens.";
                                readonly type: "integer";
                                readonly examples: readonly [50];
                            };
                            readonly num_total_opens: {
                                readonly description: "Number of total opens (non-unique).";
                                readonly type: "integer";
                                readonly examples: readonly [60];
                            };
                            readonly num_hard_bounces: {
                                readonly description: "Number of emails sent that hard bounced.";
                                readonly type: "integer";
                                readonly examples: readonly [4];
                            };
                            readonly num_soft_bounces: {
                                readonly description: "Number of emails sent that soft bounced.";
                                readonly type: "integer";
                                readonly examples: readonly [8];
                            };
                            readonly num_complaints: {
                                readonly description: "Number of emails sent that complained.";
                                readonly type: "integer";
                                readonly examples: readonly [2];
                            };
                            readonly num_unsubscribes: {
                                readonly description: "Number of emails sent that unsubscribed.";
                                readonly type: "integer";
                                readonly examples: readonly [3];
                            };
                            readonly status: {
                                readonly description: "Status of the campaign.\n\n`draft` `pending` `in progress` `complete` `error` `paused` `archived` `active`";
                                readonly type: "string";
                                readonly enum: readonly ["draft", "pending", "in progress", "complete", "error", "paused", "archived", "active"];
                                readonly examples: readonly ["draft"];
                            };
                        };
                        readonly type: "object";
                    };
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const ListConnections: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly limit: {
                    readonly type: "integer";
                    readonly default: 10;
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A limit on the number of objects to be returned, between 1 and 100.";
                };
                readonly cursor: {
                    readonly type: "string";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                };
            };
            readonly required: readonly [];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "ListConnectionsResult";
            readonly properties: {
                readonly has_more: {
                    readonly description: "Whether or not there are more elements after this set. If `false`, this set comprises the end of the list.";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly cursor: {
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                    readonly type: "string";
                    readonly examples: readonly ["K5pwIGH3hgYrhytbDUY5eQ=="];
                };
                readonly data: {
                    readonly type: "array";
                    readonly items: {
                        readonly properties: {
                            readonly id: {
                                readonly description: "ID of the connection";
                                readonly format: "uuid";
                                readonly type: "string";
                                readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                            };
                            readonly type: {
                                readonly description: "Service type of the connection.\n\n`aws` `elastic_email` `spark_post` `green_arrow` `pro`";
                                readonly enum: readonly ["aws", "elastic_email", "spark_post", "green_arrow", "pro"];
                                readonly type: "string";
                                readonly examples: readonly ["aws"];
                            };
                            readonly name: {
                                readonly description: "Name of the connection";
                                readonly type: "string";
                                readonly examples: readonly ["AWS us-east-1"];
                            };
                            readonly created: {
                                readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                                readonly type: "integer";
                                readonly examples: readonly [1592422352];
                            };
                        };
                        readonly type: "object";
                    };
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const ListContacts: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to list contacts in";
                };
            };
            readonly required: readonly ["brand_id"];
        }, {
            readonly type: "object";
            readonly properties: {
                readonly limit: {
                    readonly type: "integer";
                    readonly default: 10;
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A limit on the number of objects to be returned, between 1 and 100.";
                };
                readonly cursor: {
                    readonly type: "string";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                };
                readonly list_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "The id of a list. Only contacts in this list are returned.";
                };
            };
            readonly required: readonly [];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "ListContactsResult";
            readonly properties: {
                readonly has_more: {
                    readonly description: "Whether or not there are more elements after this set. If `false`, this set comprises the end of the list.";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly cursor: {
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                    readonly type: "string";
                    readonly examples: readonly ["K5pwIGH3hgYrhytbDUY5eQ=="];
                };
                readonly total: {
                    readonly description: "The total number of items in the brand or list.";
                    readonly type: "integer";
                    readonly examples: readonly [100];
                };
                readonly data: {
                    readonly type: "array";
                    readonly items: {
                        readonly properties: {
                            readonly id: {
                                readonly description: "ID of the contact";
                                readonly format: "uuid";
                                readonly type: "string";
                                readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                            };
                            readonly brand_id: {
                                readonly description: "ID of the brand the contact is in";
                                readonly format: "uuid";
                                readonly type: "string";
                                readonly examples: readonly ["2aef2dd2-ab14-453a-aadc-01f3699ed85a"];
                            };
                            readonly email: {
                                readonly description: "Email address of the contact";
                                readonly format: "email";
                                readonly type: "string";
                                readonly examples: readonly ["chris@bigmailer.io"];
                            };
                            readonly field_values: {
                                readonly description: "Field values associated with the contact.\n";
                                readonly items: {
                                    readonly title: "FieldValuePayload";
                                    readonly properties: {
                                        readonly date: {
                                            readonly format: "date";
                                            readonly type: "string";
                                            readonly examples: readonly ["2019-11-27"];
                                        };
                                        readonly integer: {
                                            readonly format: "int64";
                                            readonly type: "integer";
                                            readonly examples: readonly [4995590933000642000];
                                            readonly minimum: -9223372036854776000;
                                            readonly maximum: 9223372036854776000;
                                        };
                                        readonly name: {
                                            readonly type: "string";
                                            readonly examples: readonly ["FIRST NAME"];
                                        };
                                        readonly string: {
                                            readonly type: "string";
                                            readonly examples: readonly ["Christopher"];
                                        };
                                    };
                                    readonly required: readonly ["name"];
                                    readonly type: "object";
                                };
                                readonly type: "array";
                            };
                            readonly list_ids: {
                                readonly description: "IDs of the lists the contact is part of.";
                                readonly items: {
                                    readonly format: "uuid";
                                    readonly type: "string";
                                    readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                                };
                                readonly type: "array";
                                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                            };
                            readonly unsubscribe_all: {
                                readonly description: "true if the contact has unsubscribed from all message types, false otherwise.";
                                readonly type: "boolean";
                                readonly examples: readonly [true];
                            };
                            readonly unsubscribe_ids: {
                                readonly description: "IDs of message types the contact has unsubscribed from.";
                                readonly items: {
                                    readonly format: "uuid";
                                    readonly type: "string";
                                    readonly examples: readonly ["23f4c393-7556-4317-a38e-e0b0e60e6c8a"];
                                };
                                readonly type: "array";
                                readonly examples: readonly ["23f4c393-7556-4317-a38e-e0b0e60e6c8a"];
                            };
                            readonly num_soft_bounces: {
                                readonly description: "Number of times a campaign sent to contact's email has soft bounced.";
                                readonly type: "integer";
                                readonly examples: readonly [0];
                            };
                            readonly num_hard_bounces: {
                                readonly description: "Number of times a campaign sent to contact's email has hard bounced.";
                                readonly type: "integer";
                                readonly examples: readonly [0];
                            };
                            readonly num_complaints: {
                                readonly description: "Number of times a campaign sent to contact's email has triggered a complaint.";
                                readonly type: "integer";
                                readonly examples: readonly [0];
                            };
                            readonly created: {
                                readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                                readonly type: "integer";
                                readonly examples: readonly [1592422352];
                            };
                        };
                        readonly type: "object";
                    };
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const ListFields: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to retrieve fields from";
                };
            };
            readonly required: readonly ["brand_id"];
        }, {
            readonly type: "object";
            readonly properties: {
                readonly limit: {
                    readonly type: "integer";
                    readonly default: 10;
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A limit on the number of objects to be returned, between 1 and 100.";
                };
                readonly cursor: {
                    readonly type: "string";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                };
            };
            readonly required: readonly [];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "ListFieldsResult";
            readonly properties: {
                readonly has_more: {
                    readonly description: "Whether or not there are more elements after this set. If `false`, this set comprises the end of the list.";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly cursor: {
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                    readonly type: "string";
                    readonly examples: readonly ["K5pwIGH3hgYrhytbDUY5eQ=="];
                };
                readonly data: {
                    readonly type: "array";
                    readonly items: {
                        readonly properties: {
                            readonly id: {
                                readonly description: "ID of the field";
                                readonly format: "uuid";
                                readonly type: "string";
                                readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                            };
                            readonly name: {
                                readonly description: "Name of the field";
                                readonly type: "string";
                                readonly examples: readonly ["First Name"];
                            };
                            readonly type: {
                                readonly description: "Data type of the field.\n\n`date` `email` `integer` `text`";
                                readonly type: "string";
                                readonly enum: readonly ["date", "email", "integer", "text"];
                                readonly examples: readonly ["text"];
                            };
                            readonly merge_tag_name: {
                                readonly description: "Name used to reference a field's value via a template or the API. For example, if merge_tag_name is FIRST_NAME, the field can be referenced using `*|FIRST_NAME|*` in a template or `{\"name\": \"FIRST_NAME\", \"string\": \"\"}` via the API.\n";
                                readonly type: "string";
                                readonly examples: readonly ["FIRST_NAME"];
                            };
                            readonly sample_value: {
                                readonly description: "A value used for the field when sending test campaigns.";
                                readonly type: "string";
                                readonly examples: readonly ["Christopher"];
                            };
                            readonly created: {
                                readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                                readonly type: "integer";
                                readonly examples: readonly [1592422352];
                            };
                        };
                        readonly type: "object";
                    };
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const ListLists: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to retrieve lists from";
                };
            };
            readonly required: readonly ["brand_id"];
        }, {
            readonly type: "object";
            readonly properties: {
                readonly limit: {
                    readonly type: "integer";
                    readonly default: 10;
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A limit on the number of objects to be returned, between 1 and 100.";
                };
                readonly cursor: {
                    readonly type: "string";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                };
            };
            readonly required: readonly [];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "ListListsResult";
            readonly properties: {
                readonly has_more: {
                    readonly description: "Whether or not there are more elements after this set. If `false`, this set comprises the end of the list.";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly cursor: {
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                    readonly type: "string";
                    readonly examples: readonly ["K5pwIGH3hgYrhytbDUY5eQ=="];
                };
                readonly data: {
                    readonly type: "array";
                    readonly items: {
                        readonly properties: {
                            readonly id: {
                                readonly description: "ID of the list";
                                readonly format: "uuid";
                                readonly type: "string";
                                readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                            };
                            readonly name: {
                                readonly description: "Name of the list";
                                readonly type: "string";
                                readonly examples: readonly ["High Engagement Contacts"];
                            };
                            readonly all: {
                                readonly description: "true if this list is the special system created list containing all contacts within a brand, false otherwise.";
                                readonly type: "boolean";
                                readonly examples: readonly [false];
                            };
                            readonly created: {
                                readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                                readonly type: "integer";
                                readonly examples: readonly [1592422352];
                            };
                        };
                        readonly type: "object";
                    };
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const ListMessageTypes: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to retrieve message types from";
                };
            };
            readonly required: readonly ["brand_id"];
        }, {
            readonly type: "object";
            readonly properties: {
                readonly limit: {
                    readonly type: "integer";
                    readonly default: 10;
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A limit on the number of objects to be returned, between 1 and 100.";
                };
                readonly cursor: {
                    readonly type: "string";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                };
                readonly type: {
                    readonly type: "string";
                    readonly enum: readonly ["all", "account", "user"];
                    readonly default: "user";
                    readonly description: "Limit results to a specific type.";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                };
            };
            readonly required: readonly [];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "ListMessageTypesResult";
            readonly properties: {
                readonly has_more: {
                    readonly description: "Whether or not there are more elements after this set. If `false`, this set comprises the end of the list.";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly cursor: {
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                    readonly type: "string";
                    readonly examples: readonly ["K5pwIGH3hgYrhytbDUY5eQ=="];
                };
                readonly data: {
                    readonly type: "array";
                    readonly items: {
                        readonly properties: {
                            readonly id: {
                                readonly description: "ID of the message type";
                                readonly format: "uuid";
                                readonly type: "string";
                                readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                            };
                            readonly type: {
                                readonly description: "The type of the message type\n\n`account` `all` `user`";
                                readonly type: "string";
                                readonly enum: readonly ["account", "all", "user"];
                                readonly examples: readonly ["user"];
                            };
                            readonly name: {
                                readonly description: "Name of the message type";
                                readonly type: "string";
                                readonly examples: readonly ["Newsletters"];
                            };
                            readonly created: {
                                readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                                readonly type: "integer";
                                readonly examples: readonly [1592422352];
                            };
                        };
                        readonly type: "object";
                    };
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const ListSegments: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to retrieve segments from";
                };
            };
            readonly required: readonly ["brand_id"];
        }, {
            readonly type: "object";
            readonly properties: {
                readonly limit: {
                    readonly type: "integer";
                    readonly default: 10;
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A limit on the number of objects to be returned, between 1 and 100.";
                };
                readonly cursor: {
                    readonly type: "string";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                };
            };
            readonly required: readonly [];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "ListSegmentsResult";
            readonly properties: {
                readonly has_more: {
                    readonly description: "Whether or not there are more elements after this set. If `false`, this set comprises the end of the list.";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly cursor: {
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                    readonly type: "string";
                    readonly examples: readonly ["K5pwIGH3hgYrhytbDUY5eQ=="];
                };
                readonly data: {
                    readonly type: "array";
                    readonly items: {
                        readonly properties: {
                            readonly id: {
                                readonly description: "ID of the segment";
                                readonly format: "uuid";
                                readonly type: "string";
                                readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                            };
                            readonly name: {
                                readonly description: "Name of the segment";
                                readonly type: "string";
                                readonly examples: readonly ["Opened Campaign"];
                            };
                            readonly created: {
                                readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                                readonly type: "integer";
                                readonly examples: readonly [1592422352];
                            };
                        };
                        readonly type: "object";
                    };
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const ListSuppressionLists: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to retrieve suppression lists from";
                };
            };
            readonly required: readonly ["brand_id"];
        }, {
            readonly type: "object";
            readonly properties: {
                readonly limit: {
                    readonly type: "integer";
                    readonly default: 10;
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A limit on the number of objects to be returned, between 1 and 100.";
                };
                readonly cursor: {
                    readonly type: "string";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                };
            };
            readonly required: readonly [];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "ListSuppressionListsResult";
            readonly properties: {
                readonly has_more: {
                    readonly description: "Whether or not there are more elements after this set. If `false`, this set comprises the end of the list.";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly cursor: {
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                    readonly type: "string";
                    readonly examples: readonly ["K5pwIGH3hgYrhytbDUY5eQ=="];
                };
                readonly data: {
                    readonly type: "array";
                    readonly items: {
                        readonly properties: {
                            readonly id: {
                                readonly description: "ID of the suppression list";
                                readonly format: "uuid";
                                readonly type: "string";
                                readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                            };
                            readonly file_name: {
                                readonly description: "File name of the suppression list";
                                readonly type: "string";
                                readonly examples: readonly ["suppressed_contacts.csv"];
                            };
                            readonly file_size: {
                                readonly description: "Size in bytes of the suppression list";
                                readonly type: "integer";
                                readonly examples: readonly [65536];
                            };
                            readonly created: {
                                readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                                readonly type: "integer";
                                readonly examples: readonly [1592422352];
                            };
                        };
                        readonly type: "object";
                    };
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const ListTransactionalCampaigns: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to retrieve transactional campaigns from";
                };
            };
            readonly required: readonly ["brand_id"];
        }, {
            readonly type: "object";
            readonly properties: {
                readonly limit: {
                    readonly type: "integer";
                    readonly default: 10;
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A limit on the number of objects to be returned, between 1 and 100.";
                };
                readonly cursor: {
                    readonly type: "string";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                };
            };
            readonly required: readonly [];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "ListTransactionalCampaignsResult";
            readonly properties: {
                readonly has_more: {
                    readonly description: "Whether or not there are more elements after this set. If `false`, this set comprises the end of the list.";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly cursor: {
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                    readonly type: "string";
                    readonly examples: readonly ["K5pwIGH3hgYrhytbDUY5eQ=="];
                };
                readonly data: {
                    readonly type: "array";
                    readonly items: {
                        readonly properties: {
                            readonly id: {
                                readonly description: "ID of the campaign";
                                readonly format: "uuid";
                                readonly type: "string";
                                readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                            };
                            readonly name: {
                                readonly description: "Name of the campaign";
                                readonly type: "string";
                                readonly examples: readonly ["March 2022 Campaign"];
                            };
                            readonly created: {
                                readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                                readonly type: "integer";
                                readonly examples: readonly [1592422352];
                            };
                            readonly subject: {
                                readonly description: "Subject line for the campaign";
                                readonly type: "string";
                                readonly examples: readonly ["The January Newsletter"];
                            };
                            readonly from: {
                                readonly properties: {
                                    readonly email: {
                                        readonly description: "From email address";
                                        readonly type: "string";
                                        readonly format: "email";
                                        readonly examples: readonly ["chris@bigmailer.io"];
                                    };
                                    readonly name: {
                                        readonly description: "From name";
                                        readonly type: "string";
                                        readonly examples: readonly ["Chris"];
                                    };
                                };
                                readonly type: "object";
                            };
                            readonly recipient_name: {
                                readonly description: "Name of the recipient. Use merge tags to make it more personal and avoid spam filters.";
                                readonly type: "string";
                                readonly examples: readonly ["*|FIRST_NAME|*"];
                            };
                            readonly reply_to: {
                                readonly properties: {
                                    readonly email: {
                                        readonly description: "Reply to email address";
                                        readonly type: "string";
                                        readonly format: "email";
                                        readonly examples: readonly ["chris@bigmailer.io"];
                                    };
                                    readonly name: {
                                        readonly description: "Reply to name";
                                        readonly type: "string";
                                        readonly examples: readonly ["Chris"];
                                    };
                                };
                                readonly type: "object";
                            };
                            readonly link_params: {
                                readonly description: "Additional query string parameters to add to all links in the template.";
                                readonly type: "string";
                                readonly examples: readonly ["utm_campaign=spring_sale&utm_medium=cpc"];
                            };
                            readonly preview: {
                                readonly description: "Copy shown following your subject line in many email clients.";
                                readonly type: "string";
                                readonly examples: readonly ["Hurry, 50% Off for 2 Days Only!"];
                            };
                            readonly track_opens: {
                                readonly description: "True to enable open tracking (HTML campaigns only).";
                                readonly type: "boolean";
                                readonly examples: readonly [true];
                            };
                            readonly track_clicks: {
                                readonly description: "True to enable click tracking in HTML links.";
                                readonly type: "boolean";
                                readonly examples: readonly [true];
                            };
                            readonly track_text_clicks: {
                                readonly description: "True to enable click tracking in text links.";
                                readonly type: "boolean";
                                readonly examples: readonly [true];
                            };
                            readonly message_type_id: {
                                readonly description: "ID of the message type of the campaign.";
                                readonly type: "string";
                                readonly format: "uuid";
                                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                            };
                            readonly list_id: {
                                readonly description: "ID of a list contacts sent the transactional campaign should be added to.";
                                readonly type: "string";
                                readonly format: "uuid";
                                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                            };
                            readonly num_sent: {
                                readonly description: "Number of emails sent.";
                                readonly type: "integer";
                                readonly examples: readonly [100];
                            };
                            readonly num_rejected: {
                                readonly description: "Number of emails rejected.";
                                readonly type: "integer";
                                readonly examples: readonly [10];
                            };
                            readonly num_clicks: {
                                readonly description: "Number of unique clicks.";
                                readonly type: "integer";
                                readonly examples: readonly [20];
                            };
                            readonly num_total_clicks: {
                                readonly description: "Number of total clicks (non-unique).";
                                readonly type: "integer";
                                readonly examples: readonly [30];
                            };
                            readonly num_opens: {
                                readonly description: "Number of unique opens.";
                                readonly type: "integer";
                                readonly examples: readonly [50];
                            };
                            readonly num_total_opens: {
                                readonly description: "Number of total opens (non-unique).";
                                readonly type: "integer";
                                readonly examples: readonly [60];
                            };
                            readonly num_hard_bounces: {
                                readonly description: "Number of emails sent that hard bounced.";
                                readonly type: "integer";
                                readonly examples: readonly [4];
                            };
                            readonly num_soft_bounces: {
                                readonly description: "Number of emails sent that soft bounced.";
                                readonly type: "integer";
                                readonly examples: readonly [8];
                            };
                            readonly num_complaints: {
                                readonly description: "Number of emails sent that complained.";
                                readonly type: "integer";
                                readonly examples: readonly [2];
                            };
                            readonly num_unsubscribes: {
                                readonly description: "Number of emails sent that unsubscribed.";
                                readonly type: "integer";
                                readonly examples: readonly [3];
                            };
                            readonly status: {
                                readonly description: "Status of the campaign.\n\n`draft` `pending` `in progress` `complete` `error` `paused` `archived` `active`";
                                readonly type: "string";
                                readonly enum: readonly ["draft", "pending", "in progress", "complete", "error", "paused", "archived", "active"];
                                readonly examples: readonly ["draft"];
                            };
                        };
                        readonly type: "object";
                    };
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const ListUsers: {
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly limit: {
                    readonly type: "integer";
                    readonly default: 10;
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A limit on the number of objects to be returned, between 1 and 100.";
                };
                readonly cursor: {
                    readonly type: "string";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                };
            };
            readonly required: readonly [];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "ListUsersResult";
            readonly properties: {
                readonly has_more: {
                    readonly description: "Whether or not there are more elements after this set. If `false`, this set comprises the end of the list.";
                    readonly type: "boolean";
                    readonly examples: readonly [true];
                };
                readonly cursor: {
                    readonly description: "A cursor for use in pagination. `cursor` defines your place in the list. For instance, if you make a list request and receive 100 objects along with cursor `xyz123`, your subsequent call can include `cursor=xyz123` in order to fetch the next page of the list.";
                    readonly type: "string";
                    readonly examples: readonly ["K5pwIGH3hgYrhytbDUY5eQ=="];
                };
                readonly data: {
                    readonly type: "array";
                    readonly items: {
                        readonly properties: {
                            readonly id: {
                                readonly description: "ID of the user";
                                readonly format: "uuid";
                                readonly type: "string";
                                readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                            };
                            readonly role: {
                                readonly description: "The user role determines what actions the user may perform. See our [description of user roles](https://docs.bigmailer.io/docs/user-types-and-permissions).\n\n`admin` `account_manager` `brand_manager` `campaign_manager` `template_manager`";
                                readonly type: "string";
                                readonly enum: readonly ["admin", "account_manager", "brand_manager", "campaign_manager", "template_manager"];
                                readonly examples: readonly ["brand_manager"];
                            };
                            readonly email: {
                                readonly description: "User's email address";
                                readonly type: "string";
                                readonly format: "email";
                                readonly examples: readonly ["chris@bigmailer.io"];
                            };
                            readonly is_owner: {
                                readonly description: "true if the user is the account owner. An account owner cannot be deleted.";
                                readonly type: "boolean";
                                readonly examples: readonly [true];
                            };
                            readonly is_activated: {
                                readonly description: "true if the user is activated. A user becomes activated by clicking the link in the invitation email.";
                                readonly type: "boolean";
                                readonly examples: readonly [true];
                            };
                            readonly allowed_brands: {
                                readonly description: "A list of brand IDs the user is allowed to access. Only relevant if the role is brand_manager, campaign_manager, or template_manager.";
                                readonly items: {
                                    readonly format: "uuid";
                                    readonly type: "string";
                                    readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                                };
                                readonly type: "array";
                                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                            };
                            readonly activated: {
                                readonly description: "Time at which the user was activated. Measured in seconds since the UNIX epoch.";
                                readonly type: "integer";
                                readonly examples: readonly [1592422352];
                            };
                            readonly created: {
                                readonly description: "Time at which the object was created. Measured in seconds since the UNIX epoch.";
                                readonly type: "integer";
                                readonly examples: readonly [1592422352];
                            };
                        };
                        readonly type: "object";
                    };
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const SendTransactionalCampaign: {
    readonly body: {
        readonly title: "SendTransactionalCampaignPayload";
        readonly properties: {
            readonly email: {
                readonly description: "Email address of the contact";
                readonly format: "email";
                readonly maxLength: 100;
                readonly minLength: 1;
                readonly type: "string";
                readonly examples: readonly ["chris@bigmailer.io"];
            };
            readonly field_values: {
                readonly description: "Field values are saved along with the email as part of the contact. Additionally, they are used as variables when generating the email content (body, subject, and recipient name).\n\nEach name must match the tag name of a field that exists in the brand.\n\nEach field value must have exactly one of string, integer, or date.\n\n";
                readonly items: {
                    readonly title: "FieldValuePayload";
                    readonly properties: {
                        readonly date: {
                            readonly format: "date";
                            readonly type: "string";
                            readonly examples: readonly ["2019-11-27"];
                        };
                        readonly integer: {
                            readonly format: "int64";
                            readonly type: "integer";
                            readonly examples: readonly [4995590933000642000];
                            readonly minimum: -9223372036854776000;
                            readonly maximum: 9223372036854776000;
                        };
                        readonly name: {
                            readonly type: "string";
                            readonly examples: readonly ["FIRST NAME"];
                        };
                        readonly string: {
                            readonly type: "string";
                            readonly examples: readonly ["Christopher"];
                        };
                    };
                    readonly required: readonly ["name"];
                    readonly type: "object";
                };
                readonly type: "array";
            };
            readonly variables: {
                readonly description: "Variables to substitute into the email content (body, subject, and recipient name). Unlike field_values, they are **NOT** saved as part of the contact.";
                readonly items: {
                    readonly title: "VariablePayload";
                    readonly properties: {
                        readonly name: {
                            readonly type: "string";
                            readonly examples: readonly ["FIRST NAME"];
                        };
                        readonly value: {
                            readonly type: "string";
                            readonly examples: readonly ["Christopher"];
                        };
                    };
                    readonly required: readonly ["name", "value"];
                    readonly type: "object";
                };
                readonly type: "array";
            };
        };
        readonly required: readonly ["email"];
        readonly type: "object";
        readonly $schema: "http://json-schema.org/draft-04/schema#";
    };
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "Id of the brand the campaign is part of";
                };
                readonly campaign_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the campaign";
                };
            };
            readonly required: readonly ["brand_id", "campaign_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "SendTransactionalCampaignResult";
            readonly description: "Result of sending a transactional email";
            readonly properties: {
                readonly contact_id: {
                    readonly description: "ID of the contact inserted or updated";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["38323da7-f824-4ada-8fcd-cd48a2f51fcf"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const UpdateBrand: {
    readonly body: {
        readonly title: "UpdateBrandPayload";
        readonly properties: {
            readonly name: {
                readonly description: "Name of the brand";
                readonly type: "string";
                readonly minLength: 1;
                readonly maxLength: 50;
                readonly examples: readonly ["BigMailer Co"];
            };
            readonly from_name: {
                readonly description: "Default name used in the \"From:\" header in campaigns sent from this brand.";
                readonly type: "string";
                readonly examples: readonly ["Chris"];
            };
            readonly from_email: {
                readonly description: "Default email used in the \"From:\" header in campaigns sent from this brand.";
                readonly type: "string";
                readonly format: "email";
                readonly examples: readonly ["chris@bigmailer.io"];
            };
            readonly bounce_danger_percent: {
                readonly description: "An integer percentage (0-100). If a bulk campaign in the brand reaches this threshold percent of bounces, it is paused automatically.";
                readonly type: "integer";
                readonly minimum: 1;
                readonly maximum: 15;
                readonly default: 8;
                readonly examples: readonly [15];
            };
            readonly max_soft_bounces: {
                readonly description: "The maximum number of times a contact can soft bounce before it is considered undeliverable. Set to 0 to remove the limit on soft bounces.";
                readonly type: "integer";
                readonly minimum: 0;
                readonly maximum: 20;
                readonly default: 12;
                readonly examples: readonly [5];
            };
            readonly url: {
                readonly description: "URL of a website associated with the brand";
                readonly type: "string";
                readonly format: "url";
                readonly examples: readonly ["https://www.bigmailer.io/"];
            };
            readonly unsubscribe_text: {
                readonly description: "A message displayed to contacts on the brand unsubscribe page.";
                readonly type: "string";
                readonly examples: readonly ["Sorry to see you go!"];
            };
            readonly contact_limit: {
                readonly description: "The maxmimum number of contacts the brand is allowed to contain.";
                readonly type: "integer";
                readonly minimum: 0;
                readonly maximum: 1000000000;
                readonly multipleOf: 1000;
                readonly examples: readonly [50000];
            };
            readonly logo: {
                readonly description: "A base64 encoded JPEG, PNG, or GIF image identified with the brand.";
                readonly type: "string";
                readonly format: "byte";
                readonly examples: readonly ["R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"];
            };
            readonly connection_id: {
                readonly description: "ID of the connection used to send emails";
                readonly type: "string";
                readonly format: "uuid";
                readonly examples: readonly ["562f699c-dbd0-4047-907c-218a2b482220"];
            };
        };
        readonly type: "object";
        readonly $schema: "http://json-schema.org/draft-04/schema#";
    };
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to update";
                };
            };
            readonly required: readonly ["brand_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "UpdateBrandResult";
            readonly description: "Result of updating a brand";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the brand updated";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["3887bafa-1929-4065-8e0d-9684dabbe118"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const UpdateBulkCampaign: {
    readonly body: {
        readonly title: "UpdateBulkCampaignPayload";
        readonly properties: {
            readonly name: {
                readonly description: "Name of the campaign";
                readonly type: "string";
                readonly examples: readonly ["March 2022 Campaign"];
            };
            readonly subject: {
                readonly description: "Subject line for the campaign";
                readonly type: "string";
                readonly examples: readonly ["The January Newsletter"];
            };
            readonly from: {
                readonly properties: {
                    readonly email: {
                        readonly description: "From email address";
                        readonly type: "string";
                        readonly format: "email";
                        readonly examples: readonly ["chris@bigmailer.io"];
                    };
                    readonly name: {
                        readonly description: "From name";
                        readonly type: "string";
                        readonly examples: readonly ["March 2022 Campaign"];
                    };
                };
                readonly type: "object";
            };
            readonly recipient_name: {
                readonly description: "Name of the recipient. Use merge tags to make it more personal and avoid spam filters.";
                readonly type: "string";
                readonly examples: readonly ["*|FIRST_NAME|*"];
            };
            readonly reply_to: {
                readonly properties: {
                    readonly email: {
                        readonly description: "Reply to email address";
                        readonly type: "string";
                        readonly format: "email";
                        readonly examples: readonly ["chris@bigmailer.io"];
                    };
                    readonly name: {
                        readonly description: "Reply to name";
                        readonly type: "string";
                        readonly examples: readonly ["March 2022 Campaign"];
                    };
                };
                readonly type: "object";
            };
            readonly link_params: {
                readonly description: "Additional query string parameters to add to all links in the template.";
                readonly type: "string";
                readonly examples: readonly ["utm_campaign=spring_sale&utm_medium=cpc"];
            };
            readonly preview: {
                readonly description: "Copy shown following your subject line in many email clients.";
                readonly type: "string";
                readonly examples: readonly ["Hurry, 50% Off for 2 Days Only!"];
            };
            readonly html: {
                readonly description: "HTML body of the email.";
                readonly type: "string";
                readonly examples: readonly ["<p>This is the html body.</p>"];
            };
            readonly text: {
                readonly description: "Text body of the email.";
                readonly type: "string";
                readonly examples: readonly ["This is the text body."];
            };
            readonly track_opens: {
                readonly description: "True to enable open tracking (HTML campaigns only).";
                readonly type: "boolean";
                readonly examples: readonly [true];
            };
            readonly track_clicks: {
                readonly description: "True to enable click tracking in HTML links.";
                readonly type: "boolean";
                readonly examples: readonly [true];
            };
            readonly track_text_clicks: {
                readonly description: "True to enable click tracking in text links.";
                readonly type: "boolean";
                readonly examples: readonly [true];
            };
            readonly segment_id: {
                readonly description: "ID of a segment used to filter the lists of contacts the campaign is sent to.";
                readonly type: "string";
                readonly format: "uuid";
                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
            };
            readonly message_type_id: {
                readonly description: "ID of the message type of the campaign.";
                readonly type: "string";
                readonly format: "uuid";
                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
            };
            readonly list_ids: {
                readonly description: "An array of list ids to send the campaign to.";
                readonly items: {
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                };
                readonly type: "array";
                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
            };
            readonly excluded_list_ids: {
                readonly description: "An array of list ids to exclude from the campaign. Any contacts on these lists will not be sent the campaign.";
                readonly items: {
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["9b480ee4-cddd-4f11-92d2-15f7d0f18f9c"];
                };
                readonly type: "array";
                readonly examples: readonly ["9b480ee4-cddd-4f11-92d2-15f7d0f18f9c"];
            };
            readonly scheduled_for: {
                readonly description: "Time at which to send the campaign. Measured in seconds since the UNIX epoch. Omit to send the campaign immediately.";
                readonly type: "integer";
                readonly examples: readonly [1568654293];
            };
            readonly throttling_type: {
                readonly description: "Set to `none` to send the campaign as fast as possible. Set to `burst` to send the campaign in small batches over time.";
                readonly type: "string";
                readonly enum: readonly ["none", "burst"];
                readonly examples: readonly ["burst"];
            };
            readonly throttling_amount: {
                readonly description: "Number of emails to send in each per batch. Must be a multiple of 1000. Required if `throttling_type` is `burst`.";
                readonly type: "integer";
                readonly multipleOf: 1000;
                readonly minimum: 1000;
                readonly maximum: 1000000;
                readonly examples: readonly [1000];
            };
            readonly throttling_period: {
                readonly description: "Time in seconds between sending each batch of emails. Required if `throttling_type` is `burst`.";
                readonly type: "integer";
                readonly enum: readonly [900, 1800, 3600, 7200];
                readonly examples: readonly [900];
            };
            readonly suppression_list_id: {
                readonly description: "ID of a suppression list. Any emails in the suppression list will not be sent the campaign.";
                readonly type: "string";
                readonly format: "uuid";
                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
            };
            readonly ready: {
                readonly description: "Set to true to send or schedule the campaign. The campaign will not be sent or scheduled until activated by setting ready to true.";
                readonly type: "boolean";
                readonly examples: readonly [true];
            };
        };
        readonly required: readonly ["name"];
        readonly type: "object";
        readonly $schema: "http://json-schema.org/draft-04/schema#";
    };
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to update a campaign in";
                };
                readonly campaign_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the campaign";
                };
            };
            readonly required: readonly ["brand_id", "campaign_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "UpdateBulkCampaignResult";
            readonly description: "Result of updating a bulk campaign";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the bulk campaign updated.";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["3887bafa-1929-4065-8e0d-9684dabbe118"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "422": {
            readonly title: "Precondition failed error";
            readonly description: "The operation was rejected because the system is not in a state required for the operation's execution.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["failed_precondition"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The campaign cannot be sent in it's current state."];
                };
                readonly preconditions: {
                    readonly description: "A list of codes to aid in handling the error programatically.";
                    readonly items: {
                        readonly type: "string";
                        readonly examples: readonly ["subject.format"];
                    };
                    readonly type: "array";
                    readonly examples: readonly ["subject.format", "lists.length"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const UpdateContact: {
    readonly body: {
        readonly title: "UpdateContactPayload";
        readonly properties: {
            readonly email: {
                readonly description: "Email address of the contact";
                readonly format: "email";
                readonly maxLength: 100;
                readonly minLength: 1;
                readonly type: "string";
                readonly examples: readonly ["chris@bigmailer.io"];
            };
            readonly field_values: {
                readonly description: "Field values are saved along with the email as part of the contact.\n\nEach name must match the tag name of a field that exists in the brand.\n\nEach field value must have exactly one of string, integer, or date.\n\n";
                readonly items: {
                    readonly title: "FieldValuePayload";
                    readonly properties: {
                        readonly date: {
                            readonly format: "date";
                            readonly type: "string";
                            readonly examples: readonly ["2019-11-27"];
                        };
                        readonly integer: {
                            readonly format: "int64";
                            readonly type: "integer";
                            readonly examples: readonly [4995590933000642000];
                            readonly minimum: -9223372036854776000;
                            readonly maximum: 9223372036854776000;
                        };
                        readonly name: {
                            readonly type: "string";
                            readonly examples: readonly ["FIRST NAME"];
                        };
                        readonly string: {
                            readonly type: "string";
                            readonly examples: readonly ["Christopher"];
                        };
                    };
                    readonly required: readonly ["name"];
                    readonly type: "object";
                };
                readonly type: "array";
            };
            readonly list_ids: {
                readonly description: "IDs of lists the contact should be added to";
                readonly items: {
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["42e0c094-7021-482e-a3a5-7d1479ff4687"];
                };
                readonly type: "array";
                readonly examples: readonly ["42e0c094-7021-482e-a3a5-7d1479ff4687"];
            };
            readonly unsubscribe_all: {
                readonly description: "Set to true to unsubscribe the contact from all future campaigns, regardless of message type.";
                readonly type: "boolean";
                readonly examples: readonly [true];
            };
            readonly unsubscribe_ids: {
                readonly description: "IDs of message types the contact should be unsubscribed from.";
                readonly items: {
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["6cd48292-e792-4fa1-afeb-7f2918f1d35d"];
                };
                readonly type: "array";
                readonly examples: readonly ["6cd48292-e792-4fa1-afeb-7f2918f1d35d"];
            };
        };
        readonly type: "object";
        readonly $schema: "http://json-schema.org/draft-04/schema#";
    };
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to update the contact in";
                };
                readonly contact_id: {
                    readonly type: "string";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID or email address of the contact";
                };
            };
            readonly required: readonly ["brand_id", "contact_id"];
        }, {
            readonly type: "object";
            readonly properties: {
                readonly field_values_op: {
                    readonly type: "string";
                    readonly enum: readonly ["add", "remove", "replace"];
                    readonly default: "replace";
                    readonly description: "Controls how the API uses the supplied `field_values` object.<br><br> `add` - Copy properties in the supplied `field_values` into the contact's `field_values`. Supplied field values overwrite contact field values with the same name. Field values not supplied are preserved.<br><br> `replace` - Replace the contact's `field_values` object with the supplied `field_values`. Field values not supplied are removed from the contact.<br><br> `remove` - Remove supplied `field_values` from the contact's `field_values`.\n";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                };
                readonly list_ids_op: {
                    readonly type: "string";
                    readonly enum: readonly ["add", "remove", "replace"];
                    readonly default: "replace";
                    readonly description: "Controls how the API uses the supplied `list_ids` array.<br><br> `add` - Append supplied `list_ids` to the contact's existing `list_ids` array.<br><br> `replace` - Replace the contact's `list_ids` array with the supplied `list_ids`.<br><br> `remove` - Remove supplied `list_ids` from the contact's existing `list_ids` array.\n";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                };
                readonly unsubscribe_ids_op: {
                    readonly type: "string";
                    readonly enum: readonly ["add", "remove", "replace"];
                    readonly default: "replace";
                    readonly description: "Controls how the API uses the supplied `unsubscribe_ids` array.<br><br> `add` - Append supplied `unsubscribe_ids` to the contact's existing `unsubscribe_ids` array.<br><br> `replace` - Replace the contact's `unsubscribe_ids` array with the supplied `unsubscribe_ids`.<br><br> `remove` - Remove supplied `unsubscribe_ids` from the contact's existing `unsubscribe_ids` array.\n";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                };
            };
            readonly required: readonly [];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "UpdateContactResult";
            readonly description: "Result of updating a contact";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the contact updated";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["66e60ece-d4e4-4286-8ea6-990cb500aa8e"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "422": {
            readonly title: "Contact Exists Error";
            readonly description: "The contact already exists.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Contact already exists with this email."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_already_exists"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const UpdateField: {
    readonly body: {
        readonly title: "CreateFieldPayload";
        readonly properties: {
            readonly name: {
                readonly description: "Name of the field";
                readonly type: "string";
                readonly minLength: 1;
                readonly maxLength: 50;
                readonly pattern: "^\\s*\\S.*$";
                readonly examples: readonly ["First Name"];
            };
            readonly merge_tag_name: {
                readonly description: "Name used to reference a field's value via a template or the API.  For example, if merge_tag_name is FIRST_NAME, the field can be  referenced using `*|FIRST_NAME|*` in a template or  `{\"name\": \"FIRST_NAME\", \"string\": \"\"}` via the API.\n";
                readonly type: "string";
                readonly maxLength: 50;
                readonly pattern: "^\\s*\\S.*$";
                readonly examples: readonly ["FIRST_NAME"];
            };
            readonly sample_value: {
                readonly description: "A value used for the field when sending test campaigns.";
                readonly type: "string";
                readonly maxLength: 50;
                readonly examples: readonly ["Christopher"];
            };
        };
        readonly type: "object";
        readonly $schema: "http://json-schema.org/draft-04/schema#";
    };
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to update a field in";
                };
                readonly field_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the field";
                };
            };
            readonly required: readonly ["brand_id", "field_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "UpdateFieldResult";
            readonly description: "Result of updating a field";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the field updated";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["3887bafa-1929-4065-8e0d-9684dabbe118"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "422": {
            readonly title: "Field Exists Error";
            readonly description: "A field already exists with the chosen merge tag name.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Field already exists with this merge_tag_name."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_already_exists"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const UpdateList: {
    readonly body: {
        readonly title: "UpdateListPayload";
        readonly properties: {
            readonly name: {
                readonly description: "Name of the list";
                readonly type: "string";
                readonly minLength: 1;
                readonly maxLength: 50;
                readonly examples: readonly ["High Engagement Contacts"];
            };
        };
        readonly type: "object";
        readonly $schema: "http://json-schema.org/draft-04/schema#";
    };
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to update a list in";
                };
                readonly list_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the list";
                };
            };
            readonly required: readonly ["brand_id", "list_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "UpdateListResult";
            readonly description: "Result of updating a list";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the list updated";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["3887bafa-1929-4065-8e0d-9684dabbe118"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const UpdateTransactionalCampaign: {
    readonly body: {
        readonly title: "UpdateTransactionalCampaignPayload";
        readonly properties: {
            readonly name: {
                readonly description: "Name of the campaign";
                readonly type: "string";
                readonly examples: readonly ["March 2022 Campaign"];
            };
            readonly subject: {
                readonly description: "Subject line for the campaign";
                readonly type: "string";
                readonly examples: readonly ["The January Newsletter"];
            };
            readonly from: {
                readonly properties: {
                    readonly email: {
                        readonly description: "From email address";
                        readonly type: "string";
                        readonly format: "email";
                        readonly examples: readonly ["chris@bigmailer.io"];
                    };
                    readonly name: {
                        readonly description: "From name";
                        readonly type: "string";
                        readonly examples: readonly ["March 2022 Campaign"];
                    };
                };
                readonly type: "object";
            };
            readonly recipient_name: {
                readonly description: "Name of the recipient. Use merge tags to make it more personal and avoid spam filters.";
                readonly type: "string";
                readonly examples: readonly ["*|FIRST_NAME|*"];
            };
            readonly reply_to: {
                readonly properties: {
                    readonly email: {
                        readonly description: "Reply to email address";
                        readonly type: "string";
                        readonly format: "email";
                        readonly examples: readonly ["chris@bigmailer.io"];
                    };
                    readonly name: {
                        readonly description: "Reply to name";
                        readonly type: "string";
                        readonly examples: readonly ["March 2022 Campaign"];
                    };
                };
                readonly type: "object";
            };
            readonly link_params: {
                readonly description: "Additional query string parameters to add to all links in the template.";
                readonly type: "string";
                readonly examples: readonly ["utm_campaign=spring_sale&utm_medium=cpc"];
            };
            readonly preview: {
                readonly description: "Copy shown following your subject line in many email clients.";
                readonly type: "string";
                readonly examples: readonly ["Hurry, 50% Off for 2 Days Only!"];
            };
            readonly html: {
                readonly description: "HTML body of the email.";
                readonly type: "string";
                readonly examples: readonly ["<p>This is the html body.</p>"];
            };
            readonly text: {
                readonly description: "Text body of the email.";
                readonly type: "string";
                readonly examples: readonly ["This is the text body."];
            };
            readonly track_opens: {
                readonly description: "True to enable open tracking (HTML campaigns only).";
                readonly type: "boolean";
                readonly examples: readonly [true];
            };
            readonly track_clicks: {
                readonly description: "True to enable click tracking in HTML links.";
                readonly type: "boolean";
                readonly examples: readonly [true];
            };
            readonly track_text_clicks: {
                readonly description: "True to enable click tracking in text links.";
                readonly type: "boolean";
                readonly examples: readonly [true];
            };
            readonly message_type_id: {
                readonly description: "ID of the message type of the campaign.";
                readonly type: "string";
                readonly format: "uuid";
                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
            };
            readonly list_id: {
                readonly description: "ID of a list contacts sent the transactional campaign should be added to.";
                readonly type: "string";
                readonly format: "uuid";
                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
            };
            readonly ready: {
                readonly description: "Set to true to activate the campaign. The campaign cannot be sent until activated by setting ready to true.";
                readonly type: "boolean";
                readonly examples: readonly [true];
            };
        };
        readonly required: readonly ["name"];
        readonly type: "object";
        readonly $schema: "http://json-schema.org/draft-04/schema#";
    };
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to update a campaign in";
                };
                readonly campaign_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the campaign";
                };
            };
            readonly required: readonly ["brand_id", "campaign_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "UpdateTransactionalCampaignResult";
            readonly description: "Result of updating a transactional campaign";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the transactional campaign updated.";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["3887bafa-1929-4065-8e0d-9684dabbe118"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "422": {
            readonly title: "Precondition failed error";
            readonly description: "The operation was rejected because the system is not in a state required for the operation's execution.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["failed_precondition"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The campaign cannot be sent in it's current state."];
                };
                readonly preconditions: {
                    readonly description: "A list of codes to aid in handling the error programatically.";
                    readonly items: {
                        readonly type: "string";
                        readonly examples: readonly ["subject.format"];
                    };
                    readonly type: "array";
                    readonly examples: readonly ["subject.format", "lists.length"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const UpdateUser: {
    readonly body: {
        readonly title: "UpdateUserPayload";
        readonly properties: {
            readonly role: {
                readonly description: "The user role determines what actions the user may perform. See our [description of user roles](https://docs.bigmailer.io/docs/user-types-and-permissions).";
                readonly type: "string";
                readonly enum: readonly ["admin", "account_manager", "brand_manager", "campaign_manager", "template_manager"];
                readonly examples: readonly ["brand_manager"];
            };
            readonly email: {
                readonly description: "User's email address";
                readonly type: "string";
                readonly format: "email";
                readonly examples: readonly ["chris@bigmailer.io"];
            };
            readonly allowed_brands: {
                readonly description: "A list of brand IDs the user is allowed to access. Only relevant if the role is brand_manager, campaign_manager, or template_manager.";
                readonly items: {
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                };
                readonly type: "array";
                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
            };
        };
        readonly type: "object";
        readonly $schema: "http://json-schema.org/draft-04/schema#";
    };
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly user_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the user";
                };
            };
            readonly required: readonly ["user_id"];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "UpdateUserResult";
            readonly description: "Result of updating a user";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the user updated";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["3887bafa-1929-4065-8e0d-9684dabbe118"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "422": {
            readonly title: "User Exists Error";
            readonly description: "The user already exists.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["User already exists with this email."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_already_exists"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
declare const UpsertContact: {
    readonly body: {
        readonly title: "CreateContactPayload";
        readonly properties: {
            readonly email: {
                readonly description: "Email address of the contact";
                readonly format: "email";
                readonly maxLength: 100;
                readonly minLength: 1;
                readonly type: "string";
                readonly examples: readonly ["chris@bigmailer.io"];
            };
            readonly field_values: {
                readonly description: "Field values are saved along with the email as part of the contact.\n\nEach name must match the tag name of a field that exists in the brand.\n\nEach field value must have exactly one of string, integer, or date.\n\n";
                readonly items: {
                    readonly title: "FieldValuePayload";
                    readonly properties: {
                        readonly date: {
                            readonly format: "date";
                            readonly type: "string";
                            readonly examples: readonly ["2019-11-27"];
                        };
                        readonly integer: {
                            readonly format: "int64";
                            readonly type: "integer";
                            readonly examples: readonly [4995590933000642000];
                            readonly minimum: -9223372036854776000;
                            readonly maximum: 9223372036854776000;
                        };
                        readonly name: {
                            readonly type: "string";
                            readonly examples: readonly ["FIRST NAME"];
                        };
                        readonly string: {
                            readonly type: "string";
                            readonly examples: readonly ["Christopher"];
                        };
                    };
                    readonly required: readonly ["name"];
                    readonly type: "object";
                };
                readonly type: "array";
            };
            readonly list_ids: {
                readonly description: "IDs of lists the contact should be added to";
                readonly items: {
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
                };
                readonly type: "array";
                readonly examples: readonly ["b4326936-9e08-4cf9-95fe-c44c8cf4e4ef"];
            };
            readonly unsubscribe_all: {
                readonly default: false;
                readonly description: "Set to true to unsubscribe the contact from all future campaigns, regardless of message type.";
                readonly type: "boolean";
                readonly examples: readonly [true];
            };
            readonly unsubscribe_ids: {
                readonly description: "IDs of message types the contact should be unsubscribed from.";
                readonly items: {
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["23f4c393-7556-4317-a38e-e0b0e60e6c8a"];
                };
                readonly type: "array";
                readonly examples: readonly ["23f4c393-7556-4317-a38e-e0b0e60e6c8a"];
            };
        };
        readonly required: readonly ["email"];
        readonly type: "object";
        readonly $schema: "http://json-schema.org/draft-04/schema#";
    };
    readonly metadata: {
        readonly allOf: readonly [{
            readonly type: "object";
            readonly properties: {
                readonly brand_id: {
                    readonly type: "string";
                    readonly format: "uuid";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                    readonly description: "ID of the brand to create or update the contact in";
                };
            };
            readonly required: readonly ["brand_id"];
        }, {
            readonly type: "object";
            readonly properties: {
                readonly validate: {
                    readonly type: "string";
                    readonly enum: readonly [true, false];
                    readonly default: false;
                    readonly description: "Set to true to validate the email for deliverability before adding the contact. Validation credits must be purchased before using this feature. The API does not add the contact and returns an error if the email is undeliverable.";
                    readonly $schema: "http://json-schema.org/draft-04/schema#";
                };
            };
            readonly required: readonly [];
        }];
    };
    readonly response: {
        readonly "200": {
            readonly title: "CreateContactResult";
            readonly description: "Result of creating a contact";
            readonly properties: {
                readonly id: {
                    readonly description: "ID of the contact inserted";
                    readonly format: "uuid";
                    readonly type: "string";
                    readonly examples: readonly ["3887bafa-1929-4065-8e0d-9684dabbe118"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "400": {
            readonly title: "InvalidRequestError";
            readonly description: "Object containing error information.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Email address is invalid."];
                };
                readonly param: {
                    readonly description: "If the error is parameter-specific, the parameter related to the error. For example, you can use this to display a message near the correct form field.";
                    readonly type: "string";
                    readonly examples: readonly ["email"];
                };
                readonly code: {
                    readonly description: "For some errors that could be handled programmatically, a short string indicating the error code reported.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_format"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "401": {
            readonly title: "Unauthorized Error";
            readonly description: "The API key does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["authentication_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Unknown API key"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "403": {
            readonly title: "Forbidden Error";
            readonly description: "The system understands the request but refuses to authorize it.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["The API is only accessible over HTTPS."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "404": {
            readonly title: "Resource Missing Error";
            readonly description: "A requested resource does not exist.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["invalid_request_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Item does not exist in this brand."];
                };
                readonly param: {
                    readonly description: "The parameter related to the error.";
                    readonly type: "string";
                    readonly examples: readonly ["brand_id"];
                };
                readonly code: {
                    readonly description: "Code to aid in handling the error programatically.";
                    readonly type: "string";
                    readonly examples: readonly ["resource_missing"];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "429": {
            readonly title: "Too Many Requests Error";
            readonly description: "The client has made too many requests.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["rate_limit_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["API request limit has been exceeded."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "500": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "502": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "503": {
            readonly title: "Under maintenance error";
            readonly description: "The system is under maintenance. Please try again later.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["server_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["Service temporarily unavailable. Please try again after date in Retry-After header."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
        readonly "504": {
            readonly title: "Server Error";
            readonly description: "The server encountered an unexpected error.";
            readonly properties: {
                readonly type: {
                    readonly description: "The type of error returned.";
                    readonly type: "string";
                    readonly examples: readonly ["api_error"];
                };
                readonly message: {
                    readonly description: "A human-readable message providing more details about the error.";
                    readonly type: "string";
                    readonly examples: readonly ["An unexpected error occurred."];
                };
            };
            readonly type: "object";
            readonly $schema: "http://json-schema.org/draft-04/schema#";
        };
    };
};
export { CreateBrand, CreateBulkCampaign, CreateContact, CreateField, CreateList, CreateSuppressionList, CreateTransactionalCampaign, CreateUser, DeleteContact, DeleteField, DeleteList, DeleteUser, GetBrand, GetBulkCampaign, GetConnection, GetContact, GetField, GetList, GetSegment, GetSuppressionList, GetTransactionalCampaign, GetUser, ListBrands, ListBulkCampaigns, ListConnections, ListContacts, ListFields, ListLists, ListMessageTypes, ListSegments, ListSuppressionLists, ListTransactionalCampaigns, ListUsers, SendTransactionalCampaign, UpdateBrand, UpdateBulkCampaign, UpdateContact, UpdateField, UpdateList, UpdateTransactionalCampaign, UpdateUser, UpsertContact };
