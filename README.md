# TVL-MONITORING-AGENT
The TVL Monitoring Agent is a Python-based automation script that monitors the Total Value Locked (TVL) of a specified blockchain protocol (via the DeFiLlama API). It sends periodic email updates with insights on TVL changes or stability, ensuring you stay informed about significant movements in blockchain metrics.


Features
Real-Time TVL Monitoring: Fetches the current TVL value of a protocol in real-time using DeFiLlama's API.
Email Notifications: Sends alerts via email to a list of recipients fetched from a Google Sheet.
Threshold-Based Alerts: Sends TVL change alerts if the percentage change exceeds a specified threshold (default: 3%).
Periodic Updates: Sends updates every set interval (e.g., 8 hours, or 1 minute for testing).
Google Sheets Integration: Retrieves the list of email recipients dynamically from a Google Sheet via an Apps Script API


Setup Instructions
Prerequisites
Python: Install Python 3.8 or higher.
Google Sheet: Create a Google Sheet containing the email list (one email per row, starting from the second row).
Apps Script Deployment:
Use Google Apps Script to expose the email list via an API.
Gmail: Enable App Passwords for your Gmail account.


Installation
Clone the repository:
git clone https://github.com/your-repo/tvl-monitor-agent.git
cd tvl-monitor-agent

Install dependencies:
pip install -r requirements.txt

Create a .env file in the project root and define the following variables:
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
TVL_THRESHOLD=3.0
APPS_SCRIPT_API_URL=https://script.google.com/macros/s/<YOUR_DEPLOYED_SCRIPT_ID>/exec

Set up the required Google credentials (if you plan to enhance it with additional Google API calls).

Code Overview
Key Functions
fetch_tvl_from_defillama(protocol: str): Fetches the latest TVL for a specified protocol (default: base-bridge) from DeFiLlama.
get_email_list(api_url: str): Retrieves the email list from a Google Sheet using the provided Apps Script API URL.
send_email_update(to_addresses: list[str], subject: str, body: str): Sends emails using SMTP with Gmail's app password.
tvl_monitor_logic(state: TVLMonitorState, api_url: str): Contains the main logic to monitor TVL changes and send alerts or updates.
State Persistence
The script uses a state.json file to persist monitoring state across restarts, including:

Last fetched TVL (tvl).
Threshold for TVL change detection (threshold).
Whether an alert has been sent (alert_sent).
Logging
Logs are saved in tvl_monitor.log for debugging and monitoring purposes.





