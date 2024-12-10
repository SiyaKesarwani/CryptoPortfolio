import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def download_google_sheet(sheet_id, gid, output_file):
    """
    Downloads a Google Sheet as a CSV and saves it locally.
    
    Args:
        sheet_id (str): The ID of the Google Sheet (from the URL).
        gid (str): The GID of the specific sheet/tab to download.
        output_file (str): Path to save the downloaded CSV.
    """
    # URL to export Google Sheet to CSV
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Save the content to the file
        with open(output_file, "wb") as file:
            file.write(response.content)
        print(f"Sheet downloaded and saved as '{output_file}'")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download the sheet: {e}")

# Example usage
sheet_id = os.getenv('GOOGLE_SHEET_ID')  # Replace with your Google Sheet ID
gid = "0"  # Replace with the GID of the specific tab (default is usually 0)
output_file = "investment_data.csv"  # Path to save the file
download_google_sheet(sheet_id, gid, output_file)
