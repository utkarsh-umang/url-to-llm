import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_parser.log'),
        logging.StreamHandler()
    ]
)

def get_linkedin_profiles(service, spreadsheet_id):
    """
    Get LinkedIn profile data from the specified sheet
    
    Args:
        service: Google Sheets service instance
        spreadsheet_id (str): ID of the spreadsheet
        
    Returns:
        list: List of dictionaries containing profile data
    """
    try:
        # Get entire range of data
        range_name = "Sheet1!A:O"  # Assuming data is in columns A through O
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            logging.warning("No data found in sheet")
            return []
            
        # Skip header row and process data
        profiles = []
        for i, row in enumerate(values[1:], start=2):  # start=2 because we want actual row numbers (1 is header)
            # Ensure row has enough columns
            row_data = row + [''] * (5 - len(row))  # Pad with empty strings if row is short
            
            # Extract data from columns
            first_name = row_data[0].strip()
            last_name = row_data[1].strip()
            linkedin_url = row_data[3].strip()
            
            # Only add profiles with valid LinkedIn URLs
            if linkedin_url and linkedin_url.startswith('https://www.linkedin.com/'):
                profiles.append({
                    'first_name': first_name,
                    'last_name': last_name,
                    'url': linkedin_url,
                    'row_index': i
                })
            else:
                logging.warning(f"Skipping row {i} due to invalid or missing LinkedIn URL")
                
        logging.info(f"Successfully processed {len(profiles)} profiles from sheet")
        return profiles
        
    except Exception as e:
        logging.error(f"Error fetching LinkedIn profile data: {str(e)}")
        return []

def update_linkedin_status(service, spreadsheet_id, row, status):
    """
    Update the LinkedIn connection request status in the sheet
    
    Args:
        service: Google Sheets service instance
        spreadsheet_id (str): ID of the spreadsheet
        row (int): Row number to update
        status (str): Status to write
    """
    try:
        # Assuming we're writing status to column F
        range_name = f"Sheet1!O{row}"
        body = {
            'values': [[status]]
        }
        
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        logging.info(f"Updated status for row {row}: {status}")
        
    except Exception as e:
        logging.error(f"Error updating LinkedIn status: {str(e)}")
        raise