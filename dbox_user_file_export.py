"""
Script: Dropbox Export User Files to CSV and JSON

Description:
This script exports a user's Dropbox files from a specified folder (or the root if left blank) to CSV and JSON formats.
The exported files are saved on the user's Desktop as 'merged_data.csv' and 'merged_data.json'.

Functions:
- get_monday_token: Reads the Monday.com SCIM authentication token from a specified file.
- make_request: Makes API requests with retries and exponential backoff for handling rate limits and temporary failures.

Usage:
1. Run the script.
2. Enter the Dropbox user ID when prompted.
3. Enter the path to the Dropbox token file when prompted.
4. Enter the path of the Dropbox folder to export (leave blank for root) when prompted.
5. The script will export the user's Dropbox files to the Desktop in both CSV and JSON formats.

Notes:
- Ensure the API token has the necessary permissions to access and export user files.
- Handle the API token securely and do not expose it in the code.
- Customize the input prompts and error handling as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

import requests
import json
import csv
import os
from time import sleep

# Get user input for Dropbox user and token file path
dropbox_user = input("Enter the Dropbox user: ")
token_file_path = input("Enter the path to the Dropbox token file: ")

# Read the Dropbox token from the specified file
try:
    with open(token_file_path, "r") as file:
        token_info = file.read().strip()
except FileNotFoundError:
    print(f"Error: The file {token_file_path} was not found.")
    exit(1)

# Get user input for Dropbox folder path
dropbox_folder_path = input("Enter the path of the Dropbox folder (leave blank for root): ")

url = "https://api.dropboxapi.com/2/files/list_folder"
continue_url = "https://api.dropboxapi.com/2/files/list_folder/continue"

payload = json.dumps({
  "path": dropbox_folder_path,
  "recursive": True,
  "include_media_info": False,
  "include_deleted": False,
  "include_has_explicit_shared_members": False,
  "include_mounted_folders": True,
  "include_non_downloadable_files": True
})

headers = {
  'Content-Type': 'application/json',
  'Dropbox-API-Select-User': dropbox_user,
  'Authorization': f'Bearer {token_info}'
}

# Function to make API requests with retries
def make_request(url, headers, payload, retries=3, timeout=10):
    for i in range(retries):
        try:
            response = requests.post(url, headers=headers, data=payload, timeout=timeout)
            response.raise_for_status()  # Raise an error for bad status codes
            return response
        except requests.exceptions.RequestException as e:
            print(f"Attempt {i+1} failed: {e}")
            if i < retries - 1:
                sleep(2 ** i)  # Exponential backoff
            else:
                raise

response = make_request(url, headers, payload)

try:
    data = response.json()
except json.JSONDecodeError as e:
    print("Error decoding JSON:", e)
    print("Response content was not valid JSON.")
    exit(1)

entries = data.get('entries', [])

while data.get('has_more', False):
    cursor = data['cursor']
    payload = json.dumps({"cursor": cursor})

    response = make_request(continue_url, headers, payload)
    
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        print("Response content was not valid JSON.")
        exit(1)
    
    entries.extend(data.get('entries', []))

# Write the merged data to a JSON file at the default location
json_export_location = os.path.expanduser("~/Desktop/merged_data.json")
with open(json_export_location, "w") as file:
    json.dump(entries, file)

# Determine the CSV headers dynamically based on the entries
csv_headers = set()
for entry in entries:
    csv_headers.update(entry.keys())

csv_headers = list(csv_headers)

# Write the data to a CSV file at the default location
csv_file = os.path.expanduser("~/Desktop/merged_data.csv")
with open(csv_file, "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()
    
    for entry in entries:
        writer.writerow(entry)

print(f"Data exported to {csv_file} and {json_export_location}.")
