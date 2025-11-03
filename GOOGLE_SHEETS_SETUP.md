# Google Sheets Setup Guide

## Quick Setup

### 1. Configure Spreadsheet URL

The spreadsheet URL is stored as an **environment variable** for security.

**Option A: Using `.streamlit/secrets.toml` (Recommended for local development)**

1. Copy the example file:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

2. Edit `.streamlit/secrets.toml` and add your spreadsheet URL:
   ```toml
   GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/YOUR-SHEET-ID/edit"
   ```

3. Restart the Streamlit app

**Option B: Using environment variable**

```bash
export GOOGLE_SHEETS_URL="https://docs.google.com/spreadsheets/d/YOUR-SHEET-ID/edit"
streamlit run app.py
```

### 2. Configure Worksheet Names

1. Go to **Settings** → **📊 Google Sheets** tab
2. Update the worksheet names if needed:
   - Default expenses worksheet: `expenses_taras`
   - Default income worksheet: `income_taras`
3. Click **Update Worksheet Names**

Or edit `config.toml` directly:

```toml
[google_sheets]
expenses_worksheet = "your_expenses_sheet"
income_worksheet = "your_income_sheet"
```

## How to Get Your Google Sheets URL

1. Open your Google Sheet in your browser
2. Copy the entire URL from the address bar
3. It should look like:
   ```
   https://docs.google.com/spreadsheets/d/1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t/edit
   ```

## Google Sheets Connection Methods

### Method 1: Public Sheet (Read-Only)

If your sheet is public, just set the `GOOGLE_SHEETS_URL` and you're done!

### Method 2: Service Account (Full Access)

For full read/write access, set up a Google Service Account:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Sheets API
4. Create a Service Account
5. Download the JSON key file
6. Share your Google Sheet with the service account email

Then add to `.streamlit/secrets.toml`:

```toml
[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/YOUR-SHEET-ID/edit"
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

## Security Best Practices

✅ **DO:**
- Use environment variables for sensitive data
- Use `.streamlit/secrets.toml` for local development
- Add `.streamlit/secrets.toml` to `.gitignore` (already done)
- Keep service account keys secure

❌ **DON'T:**
- Commit spreadsheet URLs to git
- Share service account keys publicly
- Commit `.streamlit/secrets.toml`

## Troubleshooting

### "Could not load data from Google Sheets. Error: Spreadsheet must be specified"

**Solution:** Set the `GOOGLE_SHEETS_URL` environment variable as described above.

### "Permission denied" errors

**Solution:** Make sure your Google Sheet is either:
- Public (anyone with link can view), OR
- Shared with your service account email

### "Worksheet not found" errors

**Solution:** Check that the worksheet names in Settings → Google Sheets match your actual worksheet names in the spreadsheet.

### Check connection status

Go to **Settings** → **📊 Google Sheets** to see:
- Current worksheet names
- Connection status
- Setup instructions

## Example Worksheet Structure

### Expenses Worksheet (`expenses_taras`)

| Date | Amount | Store | Category | Payment Option | Card |
|------|--------|-------|----------|----------------|------|
| 01-11-2025 | 50.00 | Supermarket | Food | Card | ****1234 |
| 02-11-2025 | 30.00 | Gas Station | Transport | Card | ****1234 |

### Income Worksheet (`income_taras`)

| Date | Amount | Source | Payment Option |
|------|--------|--------|----------------|
| 01-11-2025 | 2000.00 | Salary | Bank Transfer |

## Need Help?

Check the Settings → Google Sheets tab for:
- Connection status
- Setup guide
- Security best practices
- Example configurations

