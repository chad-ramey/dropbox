"""
Script: Dropbox File Export Based on Search Query for One Account

Description:
This script searches for files in a single Dropbox account based on a specified search query. It requires a Dropbox API token, the Dropbox user ID, and the search term. The results are exported to a CSV file on the Desktop.

Functions:
- search_files_recursively: Recursively searches for files in Dropbox folders and writes matching results to the CSV file.
- export_files_to_csv: Connects to Dropbox, performs file searches based on the provided query, and exports results to a CSV file.

Usage:
1. Run the script.
2. Enter the path to the Dropbox token file when prompted.
3. Provide the Dropbox user ID for the account to search.
4. Enter the search term to use in the file search.
5. The script will export the search results to 'dropbox_files_search.csv' on the Desktop.

Notes:
- Ensure the API token has the necessary permissions to search for files in the specified Dropbox account.
- Handle the API token securely and do not expose it in the code.
- Customize the search logic and file export format as needed for your use case.

Author: Chad Ramey
Date: August 3, 2024
"""

import csv
import dropbox
import os

def search_files_recursively(folder_path, csv_writer, dbx, search_query):
    """
    Recursively searches for files in Dropbox folders and writes matching results to the CSV file.

    Args:
        folder_path (str): The path of the folder to search in.
        csv_writer (csv.writer): The CSV writer object for writing results.
        dbx (dropbox.Dropbox): The Dropbox API client object.
        search_query (str): The search query to match against file names.
    """
    results = dbx.files_search(folder_path, search_query).matches
    for result in results:
        entry = result.metadata
        if isinstance(entry, dropbox.files.FolderMetadata):
            search_files_recursively(entry.path_lower, csv_writer, dbx, search_query)
        else:
            csv_writer.writerow([entry.name, entry.path_lower])

def export_files_to_csv(token, selected_user, search_query):
    """
    Connects to Dropbox, performs file searches, and exports results to a CSV file.

    Args:
        token (str): The Dropbox API token.
        selected_user (str): The Dropbox user ID to perform the search on.
        search_query (str): The search query for file search.
    """
    # Connect to Dropbox
    dbx = dropbox.Dropbox(token)

    # Set the 'Dropbox-API-Select-User' header
    dbx._session.headers['Dropbox-API-Select-User'] = selected_user

    # Prepare CSV file
    csv_file = open(os.path.expanduser("~/Desktop/dropbox_files_search.csv"), 'w', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['File Name', 'Path'])

    # Recursively search for files with the given query
    search_files_recursively('', csv_writer, dbx, search_query)

    csv_file.close()
    print("CSV export complete!")

# Ask for user input for the path to the Dropbox token file
token_file_path = input("Enter the path to the Dropbox token file: ")

# Read the Dropbox token from the specified file
try:
    with open(token_file_path, "r") as file:
        token = file.read().strip()
except FileNotFoundError:
    print(f"Error: The file {token_file_path} was not found.")
    exit(1)

# Ask for other user inputs
selected_user = input("Enter the selected user: ")
search_query = input("Enter the search query: ")

# Call the function to export files to CSV
export_files_to_csv(token, selected_user, search_query)
