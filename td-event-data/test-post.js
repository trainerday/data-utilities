const sampleData = {
  "event": "Install",
  "properties": {
    "time": 1746473430,
    "distinct_id": "77473",
    "$app_build_number": "4077",
    "$app_release": "4077",
    "$app_version": "5.2.5",
    "$app_version_string": "5.2.5",
    "$bluetooth_enabled": true,
    "$bluetooth_version": "ble",
    "$brand": "samsung",
    "$carrier": "O2 - UK",
    "$city": "Scunthorpe",
    "$device_id": "cb95b742-e130-4eab-80a3-081051291893",
    "$had_persisted_distinct_id": false,
    "$has_nfc": true,
    "$has_telephone": true,
    "$insert_id": "9cc62d387de6241f",
    "$is_reshuffled": true,
    "$lib_version": "3.0.8",
    "$manufacturer": "samsung",
    "$model": "SM-A266B",
    "$mp_api_endpoint": "api.mixpanel.com",
    "$mp_api_timestamp_ms": 1746473491120,
    "$os": "Android",
    "$os_version": "15",
    "$region": "North Lincolnshire",
    "$screen_dpi": 420,
    "$screen_height": 2118,
    "$screen_width": 1080,
    "$user_id": "77473",
    "$wifi": true,
    "Source": "APP",
    "mp_country_code": "GB",
    "mp_lib": "react-native",
    "mp_processing_time_ms": 1746473491213
  }
};

// Test with local worker (update URL when deployed)
const WORKER_URL = 'http://localhost:8787'; // Change to your deployed URL
const API_TOKEN = 'GpsaJK5hiDA2z51Lrn0VIzzi8gfumkTLPVGqWgCq';

async function testPost() {
  try {
    const response = await fetch(WORKER_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_TOKEN}`
      },
      body: JSON.stringify(sampleData)
    });

    const result = await response.json();
    console.log('Response status:', response.status);
    console.log('Response body:', result);
    
    if (result.fileName) {
      console.log('\nData stored at:', result.fileName);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

testPost();