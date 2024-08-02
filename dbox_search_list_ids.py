"""
Script: Dropbox Files Export Based on Search Query

Description:
This script searches for files in Dropbox accounts based on a specified search query. It imports Dropbox user IDs from a CSV file and performs a recursive search for files in each user's Dropbox account. The results are exported to both CSV and JSON files on the Desktop.

Functions:
- search_files_recursively: Recursively searches for files in Dropbox folders and writes matching results to the CSV file.
- export_files_to_csv: Reads Dropbox IDs from a CSV file, connects to Dropbox, and performs file searches based on the provided search query. Exports results to a CSV file.

Usage:
1. Run the script.
2. Enter the path to the Dropbox token file when prompted.
3. Provide the CSV file containing Dropbox user IDs (with 'dbmid' as the header).
4. Enter the search query for file search.
5. The script will export the search results to 'dropbox_files_search.csv' on the Desktop.

Notes:
- Ensure the API token has the necessary permissions to search for files across user accounts.
- Handle the API token securely and do not expose it in the code.
- Customize the search logic and file export format as needed for your use case.

Author: Chad Ramey
Date: August 2, 2024
"""

import csv
import dropbox
import os

def search_files_recursively(folder_path, csv_writer, dbx, search_query, dbmid):
    """
    Recursively searches for files in Dropbox folders and writes matching results to the CSV file.

    Args:
        folder_path (str): The path of the folder to search in.
        csv_writer (csv.writer): The CSV writer object for writing results.
        dbx (dropbox.Dropbox): The Dropbox API client object.
        search_query (str): The search query to match against file names.
        dbmid (str): The Dropbox user ID.
    """
    results = dbx.files_search(folder_path, search_query).matches
    for result in results:
        entry = result.metadata
        if isinstance(entry, dropbox.files.FolderMetadata):
            search_files_recursively(entry.path_lower, csv_writer, dbx, search_query, dbmid)
        else:
            csv_writer.writerow([entry.name, entry.path_lower, dbmid])

def export_files_to_csv(token, dbmid_file, search_query):
    """
    Reads Dropbox IDs from a CSV file, connects to Dropbox, performs file searches, and exports results to CSV.

    Args:
        token (str): The Dropbox API token.
        dbmid_file (str): The CSV file containing Dropbox user IDs.
        search_query (str): The search query for file search.
    """
    # Read the CSV file containing Dropbox IDs
    with open(dbmid_file, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        dbmid_list = [row['dbmid'] for row in csv_reader]

    # Connect to Dropbox
    dbx = dropbox.Dropbox(token)

    # Prepare CSV file
    csv_file = open(os.path.expanduser("~/Desktop/dropbox_files_search.csv"), 'w', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['File Name', 'Path', 'Dropbox ID'])

    for dbmid in dbmid_list:
        # Set the 'Dropbox-API-Select-User' header
        dbx._session.headers['Dropbox-API-Select-User'] = dbmid

        # Recursively search for files with the given query
        search_files_recursively('', csv_writer, dbx, search_query, dbmid)

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
dbmid_file = input("Enter the CSV file name containing Dropbox IDs: ")
search_query = input("Enter the search query: ")

# Call the function to export files to CSV
export_files_to_csv(token, dbmid_file, search_query)
