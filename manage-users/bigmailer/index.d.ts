import type * as types from './types';
import type { ConfigOptions, FetchResponse } from 'api/dist/core';
import Oas from 'oas';
import APICore from 'api/dist/core';
declare class SDK {
    spec: Oas;
    core: APICore;
    constructor();
    /**
     * Optionally configure various options that the SDK allows.
     *
     * @param config Object of supported SDK options and toggles.
     * @param config.timeout Override the default `fetch` request timeout of 30 seconds. This number
     * should be represented in milliseconds.
     */
    config(config: ConfigOptions): void;
    /**
     * If the API you're using requires authentication you can supply the required credentials
     * through this method and the library will magically determine how they should be used
     * within your API request.
     *
     * With the exception of OpenID and MutualTLS, it supports all forms of authentication
     * supported by the OpenAPI specification.
     *
     * @example <caption>HTTP Basic auth</caption>
     * sdk.auth('username', 'password');
     *
     * @example <caption>Bearer tokens (HTTP or OAuth 2)</caption>
     * sdk.auth('myBearerToken');
     *
     * @example <caption>API Keys</caption>
     * sdk.auth('myApiKey');
     *
     * @see {@link https://spec.openapis.org/oas/v3.0.3#fixed-fields-22}
     * @see {@link https://spec.openapis.org/oas/v3.1.0#fixed-fields-22}
     * @param values Your auth credentials for the API; can specify up to two strings or numbers.
     */
    auth(...values: string[] | number[]): this;
    /**
     * If the API you're using offers alternate server URLs, and server variables, you can tell
     * the SDK which one to use with this method. To use it you can supply either one of the
     * server URLs that are contained within the OpenAPI definition (along with any server
     * variables), or you can pass it a fully qualified URL to use (that may or may not exist
     * within the OpenAPI definition).
     *
     * @example <caption>Server URL with server variables</caption>
     * sdk.server('https://{region}.api.example.com/{basePath}', {
     *   name: 'eu',
     *   basePath: 'v14',
     * });
     *
     * @example <caption>Fully qualified server URL</caption>
     * sdk.server('https://eu.api.example.com/v14');
     *
     * @param url Server URL
     * @param variables An object of variables to replace into the server URL.
     */
    server(url: string, variables?: {}): void;
    /**
     * List brands in your account.
     *
     * @summary List brands
     * @throws FetchError<400, types.ListBrandsResponse400> The request was invalid.
     * @throws FetchError<401, types.ListBrandsResponse401> The API key does not exist.
     * @throws FetchError<403, types.ListBrandsResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<429, types.ListBrandsResponse429> The client has made too many requests.
     * @throws FetchError<500, types.ListBrandsResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.ListBrandsResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.ListBrandsResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.ListBrandsResponse504> The system timed out processing your request.
     */
    listBrands(metadata?: types.ListBrandsMetadataParam): Promise<FetchResponse<200, types.ListBrandsResponse200>>;
    /**
     * Create a brand.
     *
     * @summary Create brand
     * @throws FetchError<400, types.CreateBrandResponse400> The request was invalid.
     * @throws FetchError<401, types.CreateBrandResponse401> The API key does not exist.
     * @throws FetchError<403, types.CreateBrandResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<429, types.CreateBrandResponse429> The client has made too many requests.
     * @throws FetchError<500, types.CreateBrandResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.CreateBrandResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.CreateBrandResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.CreateBrandResponse504> The system timed out processing your request.
     */
    createBrand(body: types.CreateBrandBodyParam): Promise<FetchResponse<200, types.CreateBrandResponse200>>;
    /**
     * Get a brand.
     *
     * @summary Get brand
     * @throws FetchError<400, types.GetBrandResponse400> The request was invalid.
     * @throws FetchError<401, types.GetBrandResponse401> The API key does not exist.
     * @throws FetchError<403, types.GetBrandResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.GetBrandResponse404> Brand does not exist
     * @throws FetchError<429, types.GetBrandResponse429> The client has made too many requests.
     * @throws FetchError<500, types.GetBrandResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.GetBrandResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.GetBrandResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.GetBrandResponse504> The system timed out processing your request.
     */
    getBrand(metadata: types.GetBrandMetadataParam): Promise<FetchResponse<200, types.GetBrandResponse200>>;
    /**
     * Update a brand.
     *
     * @summary Update brand
     * @throws FetchError<400, types.UpdateBrandResponse400> The request was invalid.
     * @throws FetchError<401, types.UpdateBrandResponse401> The API key does not exist.
     * @throws FetchError<403, types.UpdateBrandResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.UpdateBrandResponse404> Brand does not exist
     * @throws FetchError<429, types.UpdateBrandResponse429> The client has made too many requests.
     * @throws FetchError<500, types.UpdateBrandResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.UpdateBrandResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.UpdateBrandResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.UpdateBrandResponse504> The system timed out processing your request.
     */
    updateBrand(body: types.UpdateBrandBodyParam, metadata: types.UpdateBrandMetadataParam): Promise<FetchResponse<200, types.UpdateBrandResponse200>>;
    /**
     * List connections in your account.
     *
     * @summary List connections
     * @throws FetchError<400, types.ListConnectionsResponse400> The request was invalid.
     * @throws FetchError<401, types.ListConnectionsResponse401> The API key does not exist.
     * @throws FetchError<403, types.ListConnectionsResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<429, types.ListConnectionsResponse429> The client has made too many requests.
     * @throws FetchError<500, types.ListConnectionsResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.ListConnectionsResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.ListConnectionsResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.ListConnectionsResponse504> The system timed out processing your request.
     */
    listConnections(metadata?: types.ListConnectionsMetadataParam): Promise<FetchResponse<200, types.ListConnectionsResponse200>>;
    /**
     * Get a connection.
     *
     * @summary Get connection
     * @throws FetchError<400, types.GetConnectionResponse400> Invalid request
     * @throws FetchError<401, types.GetConnectionResponse401> The API key does not exist.
     * @throws FetchError<403, types.GetConnectionResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.GetConnectionResponse404> Connection does not exist
     * @throws FetchError<429, types.GetConnectionResponse429> The client has made too many requests.
     * @throws FetchError<500, types.GetConnectionResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.GetConnectionResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.GetConnectionResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.GetConnectionResponse504> The system timed out processing your request.
     */
    getConnection(metadata: types.GetConnectionMetadataParam): Promise<FetchResponse<200, types.GetConnectionResponse200>>;
    /**
     * List contacts in a brand.
     *
     * @summary List contacts
     * @throws FetchError<400, types.ListContactsResponse400> The request was invalid.
     * @throws FetchError<401, types.ListContactsResponse401> The API key does not exist.
     * @throws FetchError<403, types.ListContactsResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.ListContactsResponse404> Brand does not exist
     * @throws FetchError<429, types.ListContactsResponse429> The client has made too many requests.
     * @throws FetchError<500, types.ListContactsResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.ListContactsResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.ListContactsResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.ListContactsResponse504> The system timed out processing your request.
     */
    listContacts(metadata: types.ListContactsMetadataParam): Promise<FetchResponse<200, types.ListContactsResponse200>>;
    /**
     * Create a contact.
     *
     * @summary Create contact
     * @throws FetchError<400, types.CreateContactResponse400> The request was invalid.
     * @throws FetchError<401, types.CreateContactResponse401> The API key does not exist.
     * @throws FetchError<403, types.CreateContactResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.CreateContactResponse404> Brand does not exist
     * @throws FetchError<422, types.CreateContactResponse422> Contact already exists with email
     * @throws FetchError<429, types.CreateContactResponse429> The client has made too many requests.
     * @throws FetchError<500, types.CreateContactResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.CreateContactResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.CreateContactResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.CreateContactResponse504> The system timed out processing your request.
     */
    createContact(body: types.CreateContactBodyParam, metadata: types.CreateContactMetadataParam): Promise<FetchResponse<200, types.CreateContactResponse200>>;
    /**
     * Create or update a contact. If the specified email does not exist, a new contact is
     * created. If the specified email exists, the existing contact is updated.
     *
     * @summary Create or update contact
     * @throws FetchError<400, types.UpsertContactResponse400> The request was invalid.
     * @throws FetchError<401, types.UpsertContactResponse401> The API key does not exist.
     * @throws FetchError<403, types.UpsertContactResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.UpsertContactResponse404> Brand does not exist
     * @throws FetchError<429, types.UpsertContactResponse429> The client has made too many requests.
     * @throws FetchError<500, types.UpsertContactResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.UpsertContactResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.UpsertContactResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.UpsertContactResponse504> The system timed out processing your request.
     */
    upsertContact(body: types.UpsertContactBodyParam, metadata: types.UpsertContactMetadataParam): Promise<FetchResponse<200, types.UpsertContactResponse200>>;
    /**
     * Get a contact.
     *
     * @summary Get contact
     * @throws FetchError<400, types.GetContactResponse400> The request was invalid.
     * @throws FetchError<401, types.GetContactResponse401> The API key does not exist.
     * @throws FetchError<403, types.GetContactResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.GetContactResponse404> Brand or contact does not exist
     * @throws FetchError<429, types.GetContactResponse429> The client has made too many requests.
     * @throws FetchError<500, types.GetContactResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.GetContactResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.GetContactResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.GetContactResponse504> The system timed out processing your request.
     */
    getContact(metadata: types.GetContactMetadataParam): Promise<FetchResponse<200, types.GetContactResponse200>>;
    /**
     * Update a contact. Any parameters not provided are left unchanged.
     *
     * @summary Update contact
     * @throws FetchError<400, types.UpdateContactResponse400> The request was invalid.
     * @throws FetchError<401, types.UpdateContactResponse401> The API key does not exist.
     * @throws FetchError<403, types.UpdateContactResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.UpdateContactResponse404> Brand or contact does not exist
     * @throws FetchError<422, types.UpdateContactResponse422> Contact already exists with email
     * @throws FetchError<429, types.UpdateContactResponse429> The client has made too many requests.
     * @throws FetchError<500, types.UpdateContactResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.UpdateContactResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.UpdateContactResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.UpdateContactResponse504> The system timed out processing your request.
     */
    updateContact(body: types.UpdateContactBodyParam, metadata: types.UpdateContactMetadataParam): Promise<FetchResponse<200, types.UpdateContactResponse200>>;
    /**
     * Delete a contact.
     *
     * @summary Delete contact
     * @throws FetchError<400, types.DeleteContactResponse400> The request was invalid.
     * @throws FetchError<401, types.DeleteContactResponse401> The API key does not exist.
     * @throws FetchError<403, types.DeleteContactResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.DeleteContactResponse404> Brand or contact does not exist
     * @throws FetchError<429, types.DeleteContactResponse429> The client has made too many requests.
     * @throws FetchError<500, types.DeleteContactResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.DeleteContactResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.DeleteContactResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.DeleteContactResponse504> The system timed out processing your request.
     */
    deleteContact(metadata: types.DeleteContactMetadataParam): Promise<FetchResponse<200, types.DeleteContactResponse200>>;
    /**
     * Retrieve lists in a brand.
     *
     * @summary List lists
     * @throws FetchError<400, types.ListListsResponse400> The request was invalid.
     * @throws FetchError<401, types.ListListsResponse401> The API key does not exist.
     * @throws FetchError<403, types.ListListsResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<429, types.ListListsResponse429> The client has made too many requests.
     * @throws FetchError<500, types.ListListsResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.ListListsResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.ListListsResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.ListListsResponse504> The system timed out processing your request.
     */
    listLists(metadata: types.ListListsMetadataParam): Promise<FetchResponse<200, types.ListListsResponse200>>;
    /**
     * Create a list.
     *
     * @summary Create list
     * @throws FetchError<400, types.CreateListResponse400> The request was invalid.
     * @throws FetchError<401, types.CreateListResponse401> The API key does not exist.
     * @throws FetchError<403, types.CreateListResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<429, types.CreateListResponse429> The client has made too many requests.
     * @throws FetchError<500, types.CreateListResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.CreateListResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.CreateListResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.CreateListResponse504> The system timed out processing your request.
     */
    createList(body: types.CreateListBodyParam, metadata: types.CreateListMetadataParam): Promise<FetchResponse<200, types.CreateListResponse200>>;
    /**
     * Get a list.
     *
     * @summary Get list
     * @throws FetchError<400, types.GetListResponse400> The request was invalid.
     * @throws FetchError<401, types.GetListResponse401> The API key does not exist.
     * @throws FetchError<403, types.GetListResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.GetListResponse404> List does not exist
     * @throws FetchError<429, types.GetListResponse429> The client has made too many requests.
     * @throws FetchError<500, types.GetListResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.GetListResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.GetListResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.GetListResponse504> The system timed out processing your request.
     */
    getList(metadata: types.GetListMetadataParam): Promise<FetchResponse<200, types.GetListResponse200>>;
    /**
     * Update a list.
     *
     * @summary Update list
     * @throws FetchError<400, types.UpdateListResponse400> The request was invalid.
     * @throws FetchError<401, types.UpdateListResponse401> The API key does not exist.
     * @throws FetchError<403, types.UpdateListResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.UpdateListResponse404> List does not exist
     * @throws FetchError<429, types.UpdateListResponse429> The client has made too many requests.
     * @throws FetchError<500, types.UpdateListResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.UpdateListResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.UpdateListResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.UpdateListResponse504> The system timed out processing your request.
     */
    updateList(body: types.UpdateListBodyParam, metadata: types.UpdateListMetadataParam): Promise<FetchResponse<200, types.UpdateListResponse200>>;
    /**
     * Delete a list. Contacts in the list are NOT deleted.
     *
     * @summary Delete list
     * @throws FetchError<400, types.DeleteListResponse400> The request was invalid.
     * @throws FetchError<401, types.DeleteListResponse401> The API key does not exist.
     * @throws FetchError<403, types.DeleteListResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.DeleteListResponse404> List does not exist
     * @throws FetchError<429, types.DeleteListResponse429> The client has made too many requests.
     * @throws FetchError<500, types.DeleteListResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.DeleteListResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.DeleteListResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.DeleteListResponse504> The system timed out processing your request.
     */
    deleteList(metadata: types.DeleteListMetadataParam): Promise<FetchResponse<200, types.DeleteListResponse200>>;
    /**
     * List fields in a brand.
     *
     * @summary List fields
     * @throws FetchError<400, types.ListFieldsResponse400> The request was invalid.
     * @throws FetchError<401, types.ListFieldsResponse401> The API key does not exist.
     * @throws FetchError<403, types.ListFieldsResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<429, types.ListFieldsResponse429> The client has made too many requests.
     * @throws FetchError<500, types.ListFieldsResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.ListFieldsResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.ListFieldsResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.ListFieldsResponse504> The system timed out processing your request.
     */
    listFields(metadata: types.ListFieldsMetadataParam): Promise<FetchResponse<200, types.ListFieldsResponse200>>;
    /**
     * Create a field.
     *
     * @summary Create field
     * @throws FetchError<400, types.CreateFieldResponse400> The request was invalid.
     * @throws FetchError<401, types.CreateFieldResponse401> The API key does not exist.
     * @throws FetchError<403, types.CreateFieldResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<422, types.CreateFieldResponse422> Field already exists with the merge_tag_name.
     * @throws FetchError<429, types.CreateFieldResponse429> The client has made too many requests.
     * @throws FetchError<500, types.CreateFieldResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.CreateFieldResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.CreateFieldResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.CreateFieldResponse504> The system timed out processing your request.
     */
    createField(body: types.CreateFieldBodyParam, metadata: types.CreateFieldMetadataParam): Promise<FetchResponse<200, types.CreateFieldResponse200>>;
    /**
     * Get a field.
     *
     * @summary Get field
     * @throws FetchError<400, types.GetFieldResponse400> The request was invalid.
     * @throws FetchError<401, types.GetFieldResponse401> The API key does not exist.
     * @throws FetchError<403, types.GetFieldResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.GetFieldResponse404> Field does not exist
     * @throws FetchError<429, types.GetFieldResponse429> The client has made too many requests.
     * @throws FetchError<500, types.GetFieldResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.GetFieldResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.GetFieldResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.GetFieldResponse504> The system timed out processing your request.
     */
    getField(metadata: types.GetFieldMetadataParam): Promise<FetchResponse<200, types.GetFieldResponse200>>;
    /**
     * Update a field.
     *
     * @summary Update field
     * @throws FetchError<400, types.UpdateFieldResponse400> The request was invalid.
     * @throws FetchError<401, types.UpdateFieldResponse401> The API key does not exist.
     * @throws FetchError<403, types.UpdateFieldResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.UpdateFieldResponse404> Field does not exist
     * @throws FetchError<422, types.UpdateFieldResponse422> Field already exists with the merge_tag_name.
     * @throws FetchError<429, types.UpdateFieldResponse429> The client has made too many requests.
     * @throws FetchError<500, types.UpdateFieldResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.UpdateFieldResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.UpdateFieldResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.UpdateFieldResponse504> The system timed out processing your request.
     */
    updateField(body: types.UpdateFieldBodyParam, metadata: types.UpdateFieldMetadataParam): Promise<FetchResponse<200, types.UpdateFieldResponse200>>;
    /**
     * Delete a field.
     *
     * @summary Delete field
     * @throws FetchError<400, types.DeleteFieldResponse400> The request was invalid.
     * @throws FetchError<401, types.DeleteFieldResponse401> The API key does not exist.
     * @throws FetchError<403, types.DeleteFieldResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.DeleteFieldResponse404> Field does not exist
     * @throws FetchError<429, types.DeleteFieldResponse429> The client has made too many requests.
     * @throws FetchError<500, types.DeleteFieldResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.DeleteFieldResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.DeleteFieldResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.DeleteFieldResponse504> The system timed out processing your request.
     */
    deleteField(metadata: types.DeleteFieldMetadataParam): Promise<FetchResponse<200, types.DeleteFieldResponse200>>;
    /**
     * List message types in a brand.
     *
     * @summary List message types
     * @throws FetchError<400, types.ListMessageTypesResponse400> The request was invalid.
     * @throws FetchError<401, types.ListMessageTypesResponse401> The API key does not exist.
     * @throws FetchError<403, types.ListMessageTypesResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<429, types.ListMessageTypesResponse429> The client has made too many requests.
     * @throws FetchError<500, types.ListMessageTypesResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.ListMessageTypesResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.ListMessageTypesResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.ListMessageTypesResponse504> The system timed out processing your request.
     */
    listMessageTypes(metadata: types.ListMessageTypesMetadataParam): Promise<FetchResponse<200, types.ListMessageTypesResponse200>>;
    /**
     * Retrieve segments in a brand.
     *
     * @summary List segments
     * @throws FetchError<400, types.ListSegmentsResponse400> The request was invalid.
     * @throws FetchError<401, types.ListSegmentsResponse401> The API key does not exist.
     * @throws FetchError<403, types.ListSegmentsResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<429, types.ListSegmentsResponse429> The client has made too many requests.
     * @throws FetchError<500, types.ListSegmentsResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.ListSegmentsResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.ListSegmentsResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.ListSegmentsResponse504> The system timed out processing your request.
     */
    listSegments(metadata: types.ListSegmentsMetadataParam): Promise<FetchResponse<200, types.ListSegmentsResponse200>>;
    /**
     * Get a segment.
     *
     * @summary Get segment
     * @throws FetchError<400, types.GetSegmentResponse400> The request was invalid.
     * @throws FetchError<401, types.GetSegmentResponse401> The API key does not exist.
     * @throws FetchError<403, types.GetSegmentResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.GetSegmentResponse404> Segment does not exist
     * @throws FetchError<429, types.GetSegmentResponse429> The client has made too many requests.
     * @throws FetchError<500, types.GetSegmentResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.GetSegmentResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.GetSegmentResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.GetSegmentResponse504> The system timed out processing your request.
     */
    getSegment(metadata: types.GetSegmentMetadataParam): Promise<FetchResponse<200, types.GetSegmentResponse200>>;
    /**
     * Retrieve suppression lists in a brand.
     *
     * @summary List suppression lists
     * @throws FetchError<400, types.ListSuppressionListsResponse400> The request was invalid.
     * @throws FetchError<401, types.ListSuppressionListsResponse401> The API key does not exist.
     * @throws FetchError<403, types.ListSuppressionListsResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<429, types.ListSuppressionListsResponse429> The client has made too many requests.
     * @throws FetchError<500, types.ListSuppressionListsResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.ListSuppressionListsResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.ListSuppressionListsResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.ListSuppressionListsResponse504> The system timed out processing your request.
     */
    listSuppressionLists(metadata: types.ListSuppressionListsMetadataParam): Promise<FetchResponse<200, types.ListSuppressionListsResponse200>>;
    /**
     * Upload a suppression list.
     *
     * @summary Upload suppression list
     * @throws FetchError<400, types.CreateSuppressionListResponse400> The request was invalid.
     * @throws FetchError<401, types.CreateSuppressionListResponse401> The API key does not exist.
     * @throws FetchError<403, types.CreateSuppressionListResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<429, types.CreateSuppressionListResponse429> The client has made too many requests.
     * @throws FetchError<500, types.CreateSuppressionListResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.CreateSuppressionListResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.CreateSuppressionListResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.CreateSuppressionListResponse504> The system timed out processing your request.
     */
    createSuppressionList(body: types.CreateSuppressionListBodyParam, metadata: types.CreateSuppressionListMetadataParam): Promise<FetchResponse<200, types.CreateSuppressionListResponse200>>;
    /**
     * Get a suppression list.
     *
     * @summary Get suppression list
     * @throws FetchError<400, types.GetSuppressionListResponse400> The request was invalid.
     * @throws FetchError<401, types.GetSuppressionListResponse401> The API key does not exist.
     * @throws FetchError<403, types.GetSuppressionListResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.GetSuppressionListResponse404> Suppression list does not exist
     * @throws FetchError<429, types.GetSuppressionListResponse429> The client has made too many requests.
     * @throws FetchError<500, types.GetSuppressionListResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.GetSuppressionListResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.GetSuppressionListResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.GetSuppressionListResponse504> The system timed out processing your request.
     */
    getSuppressionList(metadata: types.GetSuppressionListMetadataParam): Promise<FetchResponse<200, types.GetSuppressionListResponse200>>;
    /**
     * Retrieve bulk campaigns in a brand.
     *
     * @summary List bulk campaigns
     * @throws FetchError<400, types.ListBulkCampaignsResponse400> The request was invalid.
     * @throws FetchError<401, types.ListBulkCampaignsResponse401> The API key does not exist.
     * @throws FetchError<403, types.ListBulkCampaignsResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<429, types.ListBulkCampaignsResponse429> The client has made too many requests.
     * @throws FetchError<500, types.ListBulkCampaignsResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.ListBulkCampaignsResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.ListBulkCampaignsResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.ListBulkCampaignsResponse504> The system timed out processing your request.
     */
    listBulkCampaigns(metadata: types.ListBulkCampaignsMetadataParam): Promise<FetchResponse<200, types.ListBulkCampaignsResponse200>>;
    /**
     * Create a bulk campaign.
     *
     * @summary Create a bulk campaign
     * @throws FetchError<400, types.CreateBulkCampaignResponse400> The request was invalid.
     * @throws FetchError<401, types.CreateBulkCampaignResponse401> The API key does not exist.
     * @throws FetchError<403, types.CreateBulkCampaignResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<422, types.CreateBulkCampaignResponse422> The campaign cannot be sent in it's current state. See
     * https://docs.bigmailer.io/docs/campaign-api-precondition-codes for more information.
     * @throws FetchError<429, types.CreateBulkCampaignResponse429> The client has made too many requests.
     * @throws FetchError<500, types.CreateBulkCampaignResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.CreateBulkCampaignResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.CreateBulkCampaignResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.CreateBulkCampaignResponse504> The system timed out processing your request.
     */
    createBulkCampaign(body: types.CreateBulkCampaignBodyParam, metadata: types.CreateBulkCampaignMetadataParam): Promise<FetchResponse<200, types.CreateBulkCampaignResponse200>>;
    /**
     * Get a bulk campaign.
     *
     * @summary Get bulk campaign
     * @throws FetchError<400, types.GetBulkCampaignResponse400> Invalid request
     * @throws FetchError<401, types.GetBulkCampaignResponse401> The API key does not exist.
     * @throws FetchError<403, types.GetBulkCampaignResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.GetBulkCampaignResponse404> Campaign does not exist
     * @throws FetchError<429, types.GetBulkCampaignResponse429> The client has made too many requests.
     * @throws FetchError<500, types.GetBulkCampaignResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.GetBulkCampaignResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.GetBulkCampaignResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.GetBulkCampaignResponse504> The system timed out processing your request.
     */
    getBulkCampaign(metadata: types.GetBulkCampaignMetadataParam): Promise<FetchResponse<200, types.GetBulkCampaignResponse200>>;
    /**
     * Update a bulk campaign.
     *
     * @summary Update a bulk campaign
     * @throws FetchError<400, types.UpdateBulkCampaignResponse400> The request was invalid.
     * @throws FetchError<401, types.UpdateBulkCampaignResponse401> The API key does not exist.
     * @throws FetchError<403, types.UpdateBulkCampaignResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.UpdateBulkCampaignResponse404> Campaign does not exist
     * @throws FetchError<422, types.UpdateBulkCampaignResponse422> The campaign cannot be sent in it's current state. See
     * https://docs.bigmailer.io/docs/campaign-api-precondition-codes for more information.
     * @throws FetchError<429, types.UpdateBulkCampaignResponse429> The client has made too many requests.
     * @throws FetchError<500, types.UpdateBulkCampaignResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.UpdateBulkCampaignResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.UpdateBulkCampaignResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.UpdateBulkCampaignResponse504> The system timed out processing your request.
     */
    updateBulkCampaign(body: types.UpdateBulkCampaignBodyParam, metadata: types.UpdateBulkCampaignMetadataParam): Promise<FetchResponse<200, types.UpdateBulkCampaignResponse200>>;
    /**
     * Retrieve transactional campaigns in a brand.
     *
     * @summary List transactional campaigns
     * @throws FetchError<400, types.ListTransactionalCampaignsResponse400> The request was invalid.
     * @throws FetchError<401, types.ListTransactionalCampaignsResponse401> The API key does not exist.
     * @throws FetchError<403, types.ListTransactionalCampaignsResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<429, types.ListTransactionalCampaignsResponse429> The client has made too many requests.
     * @throws FetchError<500, types.ListTransactionalCampaignsResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.ListTransactionalCampaignsResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.ListTransactionalCampaignsResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.ListTransactionalCampaignsResponse504> The system timed out processing your request.
     */
    listTransactionalCampaigns(metadata: types.ListTransactionalCampaignsMetadataParam): Promise<FetchResponse<200, types.ListTransactionalCampaignsResponse200>>;
    /**
     * Create a transactional campaign.
     *
     * @summary Create a transactional campaign
     * @throws FetchError<400, types.CreateTransactionalCampaignResponse400> The request was invalid.
     * @throws FetchError<401, types.CreateTransactionalCampaignResponse401> The API key does not exist.
     * @throws FetchError<403, types.CreateTransactionalCampaignResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<422, types.CreateTransactionalCampaignResponse422> The campaign cannot be sent in it's current state. See
     * https://docs.bigmailer.io/docs/campaign-api-precondition-codes for more information.
     * @throws FetchError<429, types.CreateTransactionalCampaignResponse429> The client has made too many requests.
     * @throws FetchError<500, types.CreateTransactionalCampaignResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.CreateTransactionalCampaignResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.CreateTransactionalCampaignResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.CreateTransactionalCampaignResponse504> The system timed out processing your request.
     */
    createTransactionalCampaign(body: types.CreateTransactionalCampaignBodyParam, metadata: types.CreateTransactionalCampaignMetadataParam): Promise<FetchResponse<200, types.CreateTransactionalCampaignResponse200>>;
    /**
     * Get a transactional campaign.
     *
     * @summary Get transactional campaign
     * @throws FetchError<400, types.GetTransactionalCampaignResponse400> Invalid request
     * @throws FetchError<401, types.GetTransactionalCampaignResponse401> The API key does not exist.
     * @throws FetchError<403, types.GetTransactionalCampaignResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.GetTransactionalCampaignResponse404> Campaign does not exist
     * @throws FetchError<429, types.GetTransactionalCampaignResponse429> The client has made too many requests.
     * @throws FetchError<500, types.GetTransactionalCampaignResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.GetTransactionalCampaignResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.GetTransactionalCampaignResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.GetTransactionalCampaignResponse504> The system timed out processing your request.
     */
    getTransactionalCampaign(metadata: types.GetTransactionalCampaignMetadataParam): Promise<FetchResponse<200, types.GetTransactionalCampaignResponse200>>;
    /**
     * Update a transactional campaign.
     *
     * @summary Update a transactional campaign
     * @throws FetchError<400, types.UpdateTransactionalCampaignResponse400> The request was invalid.
     * @throws FetchError<401, types.UpdateTransactionalCampaignResponse401> The API key does not exist.
     * @throws FetchError<403, types.UpdateTransactionalCampaignResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.UpdateTransactionalCampaignResponse404> Campaign does not exist
     * @throws FetchError<422, types.UpdateTransactionalCampaignResponse422> The campaign cannot be sent in it's current state. See
     * https://docs.bigmailer.io/docs/campaign-api-precondition-codes for more information.
     * @throws FetchError<429, types.UpdateTransactionalCampaignResponse429> The client has made too many requests.
     * @throws FetchError<500, types.UpdateTransactionalCampaignResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.UpdateTransactionalCampaignResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.UpdateTransactionalCampaignResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.UpdateTransactionalCampaignResponse504> The system timed out processing your request.
     */
    updateTransactionalCampaign(body: types.UpdateTransactionalCampaignBodyParam, metadata: types.UpdateTransactionalCampaignMetadataParam): Promise<FetchResponse<200, types.UpdateTransactionalCampaignResponse200>>;
    /**
     * Send an email as part of a transactional campaign.
     *
     * @summary Send a transactional email
     * @throws FetchError<400, types.SendTransactionalCampaignResponse400> The request was invalid.
     * @throws FetchError<401, types.SendTransactionalCampaignResponse401> The API key does not exist.
     * @throws FetchError<403, types.SendTransactionalCampaignResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.SendTransactionalCampaignResponse404> Campaign does not exist
     * @throws FetchError<429, types.SendTransactionalCampaignResponse429> The client has made too many requests.
     * @throws FetchError<500, types.SendTransactionalCampaignResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.SendTransactionalCampaignResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.SendTransactionalCampaignResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.SendTransactionalCampaignResponse504> The system timed out processing your request.
     */
    sendTransactionalCampaign(body: types.SendTransactionalCampaignBodyParam, metadata: types.SendTransactionalCampaignMetadataParam): Promise<FetchResponse<200, types.SendTransactionalCampaignResponse200>>;
    /**
     * Retrieve users.
     *
     * @summary List users
     * @throws FetchError<400, types.ListUsersResponse400> The request was invalid.
     * @throws FetchError<401, types.ListUsersResponse401> The API key does not exist.
     * @throws FetchError<403, types.ListUsersResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<429, types.ListUsersResponse429> The client has made too many requests.
     * @throws FetchError<500, types.ListUsersResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.ListUsersResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.ListUsersResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.ListUsersResponse504> The system timed out processing your request.
     */
    listUsers(metadata?: types.ListUsersMetadataParam): Promise<FetchResponse<200, types.ListUsersResponse200>>;
    /**
     * Create a user.
     *
     * @summary Create user
     * @throws FetchError<400, types.CreateUserResponse400> The request was invalid.
     * @throws FetchError<401, types.CreateUserResponse401> The API key does not exist.
     * @throws FetchError<403, types.CreateUserResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<422, types.CreateUserResponse422> User already exists with email
     * @throws FetchError<429, types.CreateUserResponse429> The client has made too many requests.
     * @throws FetchError<500, types.CreateUserResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.CreateUserResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.CreateUserResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.CreateUserResponse504> The system timed out processing your request.
     */
    createUser(body: types.CreateUserBodyParam): Promise<FetchResponse<200, types.CreateUserResponse200>>;
    /**
     * Get a user.
     *
     * @summary Get user
     * @throws FetchError<400, types.GetUserResponse400> The request was invalid.
     * @throws FetchError<401, types.GetUserResponse401> The API key does not exist.
     * @throws FetchError<403, types.GetUserResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.GetUserResponse404> User does not exist
     * @throws FetchError<429, types.GetUserResponse429> The client has made too many requests.
     * @throws FetchError<500, types.GetUserResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.GetUserResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.GetUserResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.GetUserResponse504> The system timed out processing your request.
     */
    getUser(metadata: types.GetUserMetadataParam): Promise<FetchResponse<200, types.GetUserResponse200>>;
    /**
     * Update a user.
     *
     * @summary Update user
     * @throws FetchError<400, types.UpdateUserResponse400> The request was invalid.
     * @throws FetchError<401, types.UpdateUserResponse401> The API key does not exist.
     * @throws FetchError<403, types.UpdateUserResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.UpdateUserResponse404> User does not exist
     * @throws FetchError<422, types.UpdateUserResponse422> User already exists with email
     * @throws FetchError<429, types.UpdateUserResponse429> The client has made too many requests.
     * @throws FetchError<500, types.UpdateUserResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.UpdateUserResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.UpdateUserResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.UpdateUserResponse504> The system timed out processing your request.
     */
    updateUser(body: types.UpdateUserBodyParam, metadata: types.UpdateUserMetadataParam): Promise<FetchResponse<200, types.UpdateUserResponse200>>;
    /**
     * Delete a user.
     *
     * @summary Delete user
     * @throws FetchError<400, types.DeleteUserResponse400> The request was invalid.
     * @throws FetchError<401, types.DeleteUserResponse401> The API key does not exist.
     * @throws FetchError<403, types.DeleteUserResponse403> The system understands the request but refuses to authorize it.
     * @throws FetchError<404, types.DeleteUserResponse404> User does not exist
     * @throws FetchError<429, types.DeleteUserResponse429> The client has made too many requests.
     * @throws FetchError<500, types.DeleteUserResponse500> An unexpected error occurred.
     * @throws FetchError<502, types.DeleteUserResponse502> The system is under heavy load or is down temporarily.
     * @throws FetchError<503, types.DeleteUserResponse503> The system is under maintenance. Please try again later.
     * @throws FetchError<504, types.DeleteUserResponse504> The system timed out processing your request.
     */
    deleteUser(metadata: types.DeleteUserMetadataParam): Promise<FetchResponse<200, types.DeleteUserResponse200>>;
}
declare const createSDK: SDK;
export = createSDK;
