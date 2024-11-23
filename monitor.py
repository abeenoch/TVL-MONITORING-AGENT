import time
import logging
from typing import Annotated, TypedDict
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("tvl_monitor.log"),
        logging.StreamHandler()
    ]
)

class TVLMonitorState(TypedDict):
    """State representing the TVL monitoring system."""
    messages: Annotated[list, list]  # Store email messages sent
    tvl: float  # The latest Total Value Locked value
    threshold: float  # The threshold for TVL change detection
    alert_sent: bool  # Flag indicating if an alert has been sent


def get_email_list(api_url: str) -> list[str]:
    """
    Fetch the email list from the deployed Apps Script API.

    Args:
        api_url (str): The URL of the deployed Apps Script.

    Returns:
        list[str]: List of email addresses excluding the header row.
    """
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        email_list = response.json()
        return email_list[1:]  # Skip the first item (header)
    except requests.RequestException as e:
        logging.error(f"Error fetching email list: {e}")
        return []


def fetch_tvl_from_defillama(protocol: str = "base-bridge", retries: int = 3) -> float:
    """
    Fetch the latest Total Value Locked (TVL) data for a given protocol using DeFiLlama API.
    Includes retries for handling failures.
    """
    url = f"https://api.llama.fi/protocol/{protocol}"
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "tvl" in data:
                tvl = data["tvl"]
                if isinstance(tvl, list) and len(tvl) > 0:
                    # Extract the most recent 'totalLiquidityUSD' from the last entry
                    latest_entry = tvl[-1]
                    if isinstance(latest_entry, dict) and "totalLiquidityUSD" in latest_entry:
                        return float(latest_entry["totalLiquidityUSD"])
                    else:
                        raise ValueError(f"Unexpected TVL entry format: {latest_entry}")
                elif isinstance(tvl, (float, int)):
                    return float(tvl)
                else:
                    raise ValueError(f"Unexpected 'tvl' format: {tvl}")
            else:
                raise ValueError("Invalid TVL data format: 'tvl' field is missing")
        except requests.RequestException as e:
            logging.error(f"Attempt {attempt + 1} failed to fetch TVL: {e}")
            time.sleep(2)  # Retry delay
    raise RuntimeError("Failed to fetch TVL after multiple attempts")



def send_email_update(to_addresses: list[str], subject: str, body: str):
    """
    Send an email with the given subject and body to the specified addresses.
    """
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")

    if not to_addresses:
        logging.warning("No email addresses found. Skipping email alert.")
        return

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(to_addresses)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL(os.getenv("SMTP_SERVER", "smtp.gmail.com"), int(os.getenv("SMTP_PORT", 465))) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_addresses, msg.as_string())
        logging.info(f"Email sent successfully to: {to_addresses}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")


def save_state(state: TVLMonitorState, filename="state.json"):
    """
    Save the current state to a JSON file.
    """
    with open(filename, "w") as f:
        json.dump(state, f)


def load_state(filename="state.json") -> TVLMonitorState:
    """
    Load the saved state from a JSON file. Initialize default state if file doesn't exist.
    """
    if Path(filename).exists():
        with open(filename, "r") as f:
            return json.load(f)
    return TVLMonitorState(
        messages=[],
        tvl=0.0,
        threshold=3.0,
        alert_sent=False,
    )


def tvl_monitor_logic(state: TVLMonitorState, api_url: str):
    """
    Monitor TVL changes and send email updates.

    Args:
        state (TVLMonitorState): The current state containing TVL, messages, and threshold.
        api_url (str): The URL of the deployed Apps Script to fetch the email list.

    Returns:
        TVLMonitorState: Updated state.
    """
    try:
        current_tvl = fetch_tvl_from_defillama()  # Fetch current TVL
    except RuntimeError as e:
        error_message = f"Error fetching TVL: {e}"
        logging.error(error_message)
        state["messages"].append({"content": error_message})
        save_state(state)
        return state

    previous_tvl = state["tvl"]
    tvl_change = ((current_tvl - previous_tvl) / previous_tvl) * 100 if previous_tvl != 0 else 0

    if abs(tvl_change) >= state["threshold"]:
        trend = "increased" if tvl_change > 0 else "decreased"
        subject = f"TVL Alert: {trend.capitalize()} by {abs(tvl_change):.2f}%"
        body = (
            f"The Total Value Locked (TVL) has {trend} by {abs(tvl_change):.2f}%.\n"
            f"Previous TVL: ${previous_tvl:,.2f}\n"
            f"Current TVL: ${current_tvl:,.2f}\n"
        )
    else:
        subject = "TVL Update: No Significant Change"
        body = (
            f"The Total Value Locked (TVL) is stable at ${current_tvl:,.2f}.\n"
            f"No significant change from the previous value of ${previous_tvl:,.2f}.\n"
        )

    # Fetch the email list using the API URL
    email_list = get_email_list(api_url)
    send_email_update(email_list, subject, body)

    # Update the state
    state["tvl"] = current_tvl
    state["messages"].append({"content": body})
    state["alert_sent"] = True
    save_state(state)

    return state



# Initialize monitoring state
state = load_state()

# Initialize monitoring state
state = load_state()

# Load the API URL from the .env file
api_url = os.getenv("APPS_SCRIPT_API_URL")
if not api_url:
    logging.error("APPS_SCRIPT_API_URL is not defined in the environment variables.")
    exit(1)

# Initialize monitoring state
try:
    initial_tvl = fetch_tvl_from_defillama()  # Fetch the real-time TVL at the start
    state = TVLMonitorState(
        messages=[],
        tvl=initial_tvl,  # Use the real-time fetched TVL
        threshold=3.0,  # Threshold in percentage
        alert_sent=False
    )
    logging.info(f"Initial TVL retrieved: ${initial_tvl:,.2f}")
except RuntimeError as e:
    logging.error(f"Failed to initialize TVL state: {e}")
    exit(1)

# Continuous monitoring loop
try:
    while True:
        state = tvl_monitor_logic(state, api_url)
        logging.info("TVL Monitoring completed. Waiting for the next cycle...")
        time.sleep(60)  # Wait 1 minute (for testing purposes)
except KeyboardInterrupt:
    logging.info("TVL Monitoring stopped by the user.")