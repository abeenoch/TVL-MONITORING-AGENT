# TVL Monitoring Agent

The **TVL Monitoring Agent** is a Python-based automation script designed to monitor the Total Value Locked (TVL) of a specified blockchain protocol (via the DeFiLlama API). It sends periodic email updates about TVL changes or stability, ensuring users stay informed about significant movements in blockchain metrics.

---

## Features

- **Real-Time TVL Monitoring**: Retrieves the latest TVL value from DeFiLlama's API.
- **Email Notifications**: Sends email alerts to a list of recipients fetched dynamically from a Google Sheet.
- **Threshold-Based Alerts**: Sends alerts if the percentage change in TVL exceeds a user-defined threshold (default: 3%).
- **Periodic Updates**: Sends TVL updates at regular intervals, even if no significant change is detected.
- **Google Sheets Integration**: Dynamically fetches email recipients from a Google Sheet via an Apps Script API.

---

## Setup Instructions

### Prerequisites

1. **Python**: Install Python 3.8 or higher.
2. **Google Sheet**: Create a Google Sheet with the email list. The first column should contain email addresses, starting from the second row.
3. **Apps Script Deployment**:
   - Use Google Apps Script to expose the email list via an API.
   - Example Apps Script code:
     ```javascript
     function doGet() {
       var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Sheet1");
       var data = sheet.getRange(1, 1, sheet.getLastRow(), 1).getValues();
       return ContentService.createTextOutput(JSON.stringify(data)).setMimeType(ContentService.MimeType.JSON);
     }
     ```
   - Deploy the Apps Script as a Web App and copy the deployment URL.
4. **Gmail**: Enable [App Passwords](https://support.google.com/accounts/answer/185833?hl=en) in your Gmail account.

---
**Create a .env file in the project root and define the following variables:**
**SMTP_EMAIL=your-email@gmail.com**
**SMTP_PASSWORD=your-app-password**
**SMTP_SERVER=smtp.gmail.com**
**SMTP_PORT=465**
**TVL_THRESHOLD=3.0**
**APPS_SCRIPT_API_URL=https://script.google.com/macros/s/<YOUR_DEPLOYED_SCRIPT_ID>/exec**



**Key Functions**
-fetch_tvl_from_defillama(protocol: str): Fetches the latest TVL for a specified protocol (default: base-bridge) from DeFiLlama.

-get_email_list(api_url: str): Retrieves the email list from a Google Sheet using the provided Apps Script API URL.

-send_email_update(to_addresses: list[str], subject: str, body: str): Sends emails using SMTP with Gmail's app password.

-tvl_monitor_logic(state: TVLMonitorState, api_url: str): Contains the main logic to monitor TVL changes and send alerts or updates.

**State Persistence**
-The script uses a state.json file to persist monitoring state across restarts, including:

-tvl: Last fetched TVL value.
-threshold: Threshold for TVL change detection.
-alert_sent: A boolean flag to indicate if an alert has been sent

**Logging**
-Log File: Logs are saved in tvl_monitor.log for debugging and monitoring purposes







