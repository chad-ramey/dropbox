### Dropbox License Monitor Script
# This script monitors Dropbox team licenses by comparing the number of used licenses
# to the total licenses allocated. If the number of used licenses exceeds the total,
# it sends an alert to a configured Slack channel via an Incoming Webhook.
#
# The script uses Dropbox's API with a short-lived access token, refreshed using a
# long-lived refresh token. The total licenses are manually configured.
#
# Required Environment Variables:
#   DROPBOX_REFRESH_TOKEN  - Long-lived Dropbox refresh token for offline access.
#   DROPBOX_CLIENT_ID      - Client ID of the Dropbox app.
#   DROPBOX_CLIENT_SECRET  - Client secret of the Dropbox app.
#   SLACK_WEBHOOK_URL      - Webhook URL to send Slack alerts.
#
# Author: Chad Ramey
# Last Updated: December 11, 2024

import os
import requests

# Dropbox API URLs
dropbox_token_url = "https://api.dropboxapi.com/oauth2/token"
dropbox_api_base_url = "https://api.dropboxapi.com/2"

# Load secrets from environment variables
client_id = os.getenv("DROPBOX_CLIENT_ID")
client_secret = os.getenv("DROPBOX_CLIENT_SECRET")
refresh_token = os.getenv("DROPBOX_REFRESH_TOKEN")
slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")

# Total licenses (manually set based on your Dropbox plan)
total_licenses = 425

# Function to refresh the access token
def get_access_token():
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(dropbox_token_url, data=payload)
    if response.status_code == 200:
        token_data = response.json()
        print("Access token refreshed successfully.")
        return token_data.get("access_token")
    else:
        print(f"Error refreshing token: {response.text}")
        return None

# Function to fetch team members and calculate used licenses
def get_team_members(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    members_url = f"{dropbox_api_base_url}/team/members/list"
    response = requests.post(members_url, headers=headers, json={"limit": 1000})
    if response.status_code == 200:
        members_data = response.json()
        return len(members_data.get("members", []))
    else:
        print(f"Error fetching team members: {response.text}")
        return None

# Function to send a Slack alert
def send_slack_alert(message):
    payload = {"text": message}
    response = requests.post(slack_webhook_url, json=payload)
    if response.status_code == 200:
        print("Slack alert sent successfully.")
    else:
        print(f"Failed to send Slack alert: {response.status_code}, {response.text}")

# Main function
def main():
    access_token = get_access_token()
    if not access_token:
        print("Failed to retrieve access token. Exiting.")
        return

    used_licenses = get_team_members(access_token)
    if used_licenses is not None:
        print(f"Used Licenses: {used_licenses}")
        available_licenses = total_licenses - used_licenses
        print(f"Total Licenses: {total_licenses}")
        print(f"Available Licenses: {available_licenses}")

        if used_licenses > total_licenses:
            alert_message = (
                f":rotating_light::dropbox: *Dropbox License Alert* :dropbox::rotating_light:\n"
                f"Used Licenses: {used_licenses}\n"
                f"Total Licenses: {total_licenses}\n"
                f"Overage: {used_licenses - total_licenses}\n"
                f"*Immediate action required to resolve the overage.*"
            )
        else:
            alert_message = (
                f":dropbox: *Dropbox License Report* :dropbox:\n"
                f"Used Licenses: {used_licenses}\n"
                f"Total Licenses: {total_licenses}\n"
                f"Available Licenses: {available_licenses}\n"
                f"*All licenses are within the allocated limit.*"
            )
        
        send_slack_alert(alert_message)
    else:
        print("Could not retrieve used licenses due to errors.")

if __name__ == "__main__":
    main()
