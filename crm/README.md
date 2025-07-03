# Mautic CRM Tools

Tools for pulling data from Mautic CRM API.

## Setup

1. **Enable Basic Authentication in Mautic:**
   - Log into your Mautic instance (crm.trainerday.com)
   - Go to Configuration → API Settings
   - Enable Mautic's API
   - Select "Basic Auth" as the authentication method
   - Save configuration

2. **Install Python dependencies:**
   ```bash
   pip install requests
   ```

3. **Set up credentials:**
   - Copy `.env.example` to `.env`
   - Add your Mautic username and password
   - Or run the script and enter credentials when prompted

## Usage

```bash
python mautic_email_fetcher.py
```

The script will:
- Connect to your Mautic instance
- Fetch email campaigns with statistics
- Display campaign names, subjects, sent/read counts
- Save data to timestamped JSON files
- Optionally get detailed stats for specific campaigns

## Features

- Basic authentication (simpler than OAuth)
- Fetches email campaigns and statistics
- Saves data to JSON files for analysis
- Shows read rates and engagement metrics
- Can filter by date ranges

## Security Note

Keep your `.env` file secure and never commit it to version control.