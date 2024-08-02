"""
Script: Dropbox Users Export to CSV

Description:
This script exports the list of team members from a Dropbox account to a CSV file.
The exported CSV file includes details such as Team Member ID, Account ID, Email, Status, Membership Type, Joined On, Groups, Member Folder ID, and Root Folder ID.

Functions:
- get_members: Fetches members from the Dropbox team using the API, with support for pagination.
- export_to_csv: Exports the fetched member data to a CSV file.

Usage:
1. Run the script.
2. Enter the path to the Dropbox token file when prompted.
3. Indicate whether to include removed accounts in the export when prompted.
4. The script will export the member data to 'dropbox_users.csv'.

Notes:
- Ensure the API token has the necessary permissions to access and export user information.
- Handle the API token securely and do not expose it in the code.
- Customize the input prompts and error handling as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

import requests
import json
import csv

def get_members(token, include_removed=False, cursor=None):
    """
    Fetches members from the Dropbox team using the API, with support for pagination.

    Args:
        token (str): The Dropbox API token.
        include_removed (bool): Whether to include removed accounts.
        cursor (str): The cursor for pagination.

    Returns:
        tuple: A tuple containing the list of members, the next cursor, and a boolean indicating if there are more members.
    """
    url = "https://api.dropboxapi.com/2/team/members/list_v2"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    data = {
        "limit": 1000,
        "include_removed": include_removed  # Use the include_removed parameter
    }

    if cursor:
        data["cursor"] = cursor

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        raise Exception(f"API Request Failed: {response.text}")

    result = response.json()
    members = result.get('members', [])
    cursor = result.get('cursor')
    has_more = result.get('has_more', False)

    return members, cursor, has_more

def export_to_csv(members, filename):
    """
    Exports the fetched member data to a CSV file.

    Args:
        members (list): List of members to export.
        filename (str): The name of the CSV file to create.
    """
    fields = ['Team Member ID', 'Account ID', 'Email', 'Status', 'Membership Type', 'Joined On', 'Groups', 'Member Folder ID', 'Root Folder ID']

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for member in members:
            profile = member.get('profile', {})
            data = {
                'Team Member ID': profile.get('team_member_id'),
                'Account ID': profile.get('account_id'),
                'Email': profile.get('email'),
                'Status': profile.get('status', {}).get('.tag'),
                'Membership Type': profile.get('membership_type', {}).get('.tag'),
                'Joined On': profile.get('joined_on'),
                'Groups': ", ".join(profile.get('groups', [])),
                'Member Folder ID': profile.get('member_folder_id'),
                'Root Folder ID': profile.get('root_folder_id')
            }
            writer.writerow(data)

def main():
    """
    Main function to read the Dropbox token, fetch member data, and export it to CSV.
    """
    # Prompt the user for the path to the Dropbox token file
    token_file_path = input("Please enter the path to the Dropbox token file: ")

    # Read the Dropbox token from the specified file
    try:
        with open(token_file_path, "r") as file:
            token = file.read().strip()
    except FileNotFoundError:
        print(f"Error: The file {token_file_path} was not found.")
        return

    include_removed_input = input("Include removed accounts? (yes/no): ").strip().lower()
    include_removed = include_removed_input == 'yes'

    all_members = []
    cursor = None
    has_more = True

    while has_more:
        members, cursor, has_more = get_members(token, include_removed, cursor)
        all_members.extend(members)

    export_to_csv(all_members, 'dropbox_users.csv')
    print("Data exported to dropbox_users.csv")

if __name__ == "__main__":
    main()
