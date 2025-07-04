# Quick Google Play Console API Setup

## 🚀 Fast Track Setup (5 minutes)

### Step 1: Google Cloud Console
1. **Go to:** https://console.cloud.google.com/
2. **Select/Create Project** (top dropdown)
3. **Enable API:**
   - Search bar → "Google Play Developer API"
   - Click on it → "Enable"

### Step 2: Create Service Account
1. **Left menu:** "IAM & Admin" → "Service Accounts"
2. **Click:** "Create Service Account"
3. **Fill:**
   - Name: `trainerday-play-api`
   - ID: `trainerday-play-api` (auto-filled)
   - Description: `API access for TrainerDay app`
4. **Click:** "Create and Continue"
5. **Skip:** Role assignment → "Continue"
6. **Skip:** Grant users access → "Done"

### Step 3: Generate JSON Key
1. **Click** on the service account you just created
2. **Go to:** "Keys" tab
3. **Click:** "Add Key" → "Create new key"
4. **Select:** JSON format
5. **Click:** "Create"
6. **Save** the downloaded file as `service-account.json` in this directory

### Step 4: Google Play Console
1. **Go to:** https://play.google.com/console/
2. **Select** your TrainerDay app
3. **Go to:** "Setup" → "API access"
4. **If needed:** Link your Google Cloud project
5. **Find** your service account in the list (trainerday-play-api@...)
6. **Grant access** with permissions:
   - ✅ View app information and download bulk reports
   - ✅ View financial data (optional)

### Step 5: Find Package Name
1. **In Play Console:** Go to "App information" → "App details"
2. **Copy** the "Package name" (like `com.trainerday.app`)
3. **Update** `.env` file in this directory with the correct package name

### Step 6: Test
```bash
python3 test_setup.py
python3 play_console_api.py
```

## 🔧 Troubleshooting

**"Service account not found"** → Check you're in the right Google Cloud project

**"API not enabled"** → Make sure Google Play Developer API is enabled

**"Permission denied"** → Verify service account has access in Play Console

**"Package not found"** → Double-check package name in .env file

## 📧 Need Help?
- Service account email format: `name@project-id.iam.gserviceaccount.com`
- Make sure the Google Cloud project matches the one linked in Play Console