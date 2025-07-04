# Google Play Console API Setup - WORKING METHOD

## ✅ Successful Setup Process

This documents the **working method** that successfully granted Google Play Console API access.

### Step 1: Google Cloud Console Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project: `claude-play-store-api-access`
3. Enable **Google Play Developer API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Play Developer API"
   - Click "Enable"

### Step 2: Create Service Account
1. Go to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Name: `claude-access`
4. Download JSON credentials as: `claude-play-store-api-access-11ea33fdf086.json`

### Step 3: Google Play Console Access (THE KEY STEP)
**THIS IS THE WORKING METHOD:**

1. **Go to Google Play Console** (not Google Cloud Console)
2. **Stay at organization/account level** (do NOT click into a specific app)
3. **Click "Users and permissions"** in the left sidebar
4. **Click "Invite new user"**
5. **Enter the service account email:**
   ```
   claude-access@claude-play-store-api-access.iam.gserviceaccount.com
   ```
6. **Grant permissions:**
   - ✅ View app information and download bulk reports
   - ✅ (Other permissions as needed)
7. **Send invitation**
8. **Status should show "Active"**

### Step 4: Configuration
1. **Package name:** `trainerday.turbo`
2. **Update `.env` file:**
   ```env
   SERVICE_ACCOUNT_FILE=claude-play-store-api-access-11ea33fdf086.json
   PACKAGE_NAME=trainerday.turbo
   TRACK=production
   ```

### Step 5: Test
```bash
python3 play_console_api.py
```

## 🎯 Key Success Factors

1. **Account Level Access:** The invitation must be done at the **Play Console account level**, not at the individual app level
2. **Users and Permissions:** This was the correct location, not "Settings" > "Linked services"
3. **Service Account Email:** The Google Cloud service account email is directly invitable as a "user"
4. **Personal Account:** This worked on a personal Google Play Console account (not organization)

## ✅ Working Results

After setup, the API provides:
- ✅ App details and metadata
- ✅ App information (title, description, contact email)
- ✅ Package verification
- ✅ Basic app management access
- 📊 Reviews API (configured, may need time to populate)
- ⚠️ Statistics API (requires additional permissions)

## 🔧 File Structure

```
app-store-google/
├── SETUP.md (this file)
├── .env (configuration)
├── claude-play-store-api-access-11ea33fdf086.json (credentials)
├── play_console_api.py (main API client)
├── requirements.txt (dependencies)
└── test_setup.py (setup verification)
```

## 📧 Service Account Details

- **Email:** `claude-access@claude-play-store-api-access.iam.gserviceaccount.com`
- **Project:** `claude-play-store-api-access`
- **Status:** Active in Google Play Console
- **Permissions:** View app information and download bulk reports

## 🚀 Usage

```python
# Test connection
python3 play_console_api.py

# Check setup
python3 test_setup.py
```

## 📝 Notes

- **No "API Access" menu required:** The traditional "API Access" or "Linked Services" approach was not needed
- **Direct user invitation worked:** Treating the service account as a regular user was the solution
- **Account-level permissions:** Organization/account level access, not app-specific
- **Immediate activation:** Permissions were active immediately after invitation

## 🔍 Troubleshooting

If API access fails:
1. Verify service account shows "Active" status in Play Console > Users and permissions
2. Check package name is correct: `trainerday.turbo`
3. Ensure Google Play Developer API is enabled in Google Cloud Console
4. Wait 2-3 minutes for permissions to propagate

---

**Success Method:** Users and Permissions > Invite new user > Service account email  
**Date:** July 3, 2025  
**Status:** ✅ Working