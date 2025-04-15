import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import time

# Load environment variables
load_dotenv()

# Airtable configuration
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = "Vacants"

# Set up Airtable API
AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

def get_airtable_records():
    """Retrieve all records from the Vacants table in Airtable."""
    records = []
    params = {"pageSize": 100}
    
    while True:
        response = requests.get(AIRTABLE_URL, headers=HEADERS, params=params)
        response_data = response.json()
        
        if "records" in response_data:
            records.extend(response_data["records"])
        
        if "offset" in response_data:
            params["offset"] = response_data["offset"]
        else:
            break
    
    return records

def get_tax_account_info(block_id, lot_id, qualifier=""):
    """Scrape tax account information from Jersey City tax website using block and lot IDs."""
    form_url = "http://taxes.cityofjerseycity.com/ViewPay?accountNumber=115998"
    
    try:
        # Start a session to maintain cookies
        session = requests.Session()
        
        # Get the initial page
        initial_response = session.get(form_url)
        
        if initial_response.status_code != 200:
            return {
                "url": form_url,
                "status": "Failed",
                "error": f"Initial page load failed with HTTP Status: {initial_response.status_code}"
            }
        
        # Revert form data: Reinstate "CurrentAccountNumber" and remove "sAccountNumber"
        form_data = {
            "CurrentAccountNumber": "115998",
            "sAccountNumber": "",
            "MinimumPaymentAmount": "0",
            "Block": block_id,
            "Lot": lot_id,
            "Qualifier": "",
            "NInterestThruDate": "",
            "paymentAmount": "0.00",
            "SearchRecalc": "Search/Recalc."
        }
        
        # Submit the form
        response = session.post(form_url, data=form_data)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check if we got a valid response
        if response.status_code == 200:
            account_data = {
                # Store the submitted block/lot for verification
                "submitted_block": block_id,
                "submitted_lot": lot_id
            }
            
            # Look for account information
            account_info = soup.find('input', {'id': 'sAccountNumber'})
            if account_info and account_info.get('value'):
                account_data["account_number"] = account_info.get('value')
            
            # Extract the Account# and other data from the response
            account_rows = soup.find_all('div', class_='row')
            for row in account_rows:
                # Account number extraction (backup method)
                if not account_data.get("account_number") and row.find('div', string=lambda text: text and 'Account#:' in text):
                    account_div = row.find('div', class_='col-md-2')
                    if account_div and account_div.find('span', class_='red'):
                        account_number = account_div.find('span', class_='red').get_text(strip=True)
                        account_data["account_number"] = account_number
                
                # Property location extraction
                if row.find('div', string=lambda text: text and 'Location:' in text):
                    location_div = row.find('div', class_='col-md-2')
                    if location_div and location_div.find('span', class_='red'):
                        location = location_div.find('span', class_='red').get_text(strip=True)
                        account_data["location"] = location
                
                # Extract address
                if row.find('div', string=lambda text: text and 'Address:' in text):
                    address_div = row.find('div', class_='col-md-2')
                    if address_div and address_div.find('span', class_='red'):
                        address = address_div.find('span', class_='red').get_text(strip=True)
                        account_data["address"] = address
                
                # Extract City/State
                if row.find('div', string=lambda text: text and 'City/State:' in text):
                    city_div = row.find('div', class_='col-md-2')
                    if city_div and city_div.find('span', class_='red'):
                        city_state = city_div.find('span', class_='red').get_text(strip=True)
                        account_data["city_state"] = city_state
                
                # Extract financial amounts
                if row.find('div', string=lambda text: text and 'Principal:' in text):
                    amount_div = row.find('div', class_='col-md-1', style="text-align:right")
                    if amount_div and amount_div.find('span', class_='red'):
                        principal = amount_div.find('span', class_='red').get_text(strip=True)
                        account_data["principal"] = principal
                
                if row.find('div', string=lambda text: text and 'Total:' in text):
                    total_div = row.find('div', class_='col-md-1', style="text-align:right")
                    if total_div and total_div.find('span', class_='red'):
                        total = total_div.find('span', class_='red').get_text(strip=True)
                        account_data["total"] = total
            
            # Check if we got an error message
            error_messages = soup.find('div', {'class': 'validation-summary-errors'})
            if error_messages:
                errors = [li.text for li in error_messages.find_all('li')]
                error_text = ', '.join(errors)
                return {
                    "url": response.url,
                    "status": "Failed",
                    "error": f"Form submission returned errors: {error_text}"
                }
            
            # Verify if we found the account info or got a no-results page
            has_account = "account_number" in account_data
            
            # Create the return data
            tax_data = {
                "url": response.url,
                "status": "Success" if has_account else "No Account Found",
                **account_data  # Include all the extracted data
            }
            
            return tax_data
        else:
            return {
                "url": form_url,
                "status": "Failed",
                "error": f"Form submission failed with HTTP Status: {response.status_code}"
            }
    except Exception as e:
        return {
            "url": form_url,
            "status": "Error",
            "error": str(e)
        }

def update_airtable_record(record_id, fields):
    """Update an Airtable record with new information."""
    update_url = f"{AIRTABLE_URL}/{record_id}"
    payload = {"fields": fields}
    
    try:
        print(f"Updating Airtable record {record_id} with fields: {fields}")
        response = requests.patch(update_url, headers=HEADERS, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            print(f"Successfully updated record {record_id}")
            return response.json()
        else:
            print(f"ERROR: Failed to update record {record_id}. Status code: {response.status_code}")
            print(f"Response text: {response.text}")
            return {"error": f"Failed to update: {response.status_code}", "details": response.text}
    except Exception as e:
        print(f"EXCEPTION during Airtable update: {str(e)}")
        return {"error": f"Exception: {str(e)}"}

def find_block_lot(fields):
    """Try to find the block and lot fields in the record."""
    block = None
    lot = None
    
    # Check common field names for Block
    block_fields = ["Block", "Block #", "Block Number", "BlockNumber"]
    for field in block_fields:
        if field in fields and fields[field]:
            block = fields[field]
            break
    
    # Check common field names for Lot
    lot_fields = ["Lot", "Lot #", "Lot Number", "LotNumber"]
    for field in lot_fields:
        if field in fields and fields[field]:
            lot = fields[field]
            break
    
    return block, lot

def main():
    # Get all records from Airtable
    records = get_airtable_records()
    print(f"Retrieved {len(records)} records from Airtable")
    
    for record in records:
        record_id = record["id"]
        fields = record["fields"]
        
        # Find the block and lot numbers
        block_id, lot_id = find_block_lot(fields)
        
        if block_id and lot_id:
            print(f"Processing Block: {block_id}, Lot: {lot_id}")
            
            # Get tax account information
            tax_info = get_tax_account_info(block_id, lot_id)
            
            # Update Airtable record with the tax information
            update_fields = {
                "Tax Account Status": tax_info["status"],
                "Tax Account URL": tax_info["url"]
            }
            
            # If account number was found, add it to the update
            if "account_number" in tax_info and tax_info["account_number"]:
                update_fields["tax_account_no"] = tax_info["account_number"]
            
            if tax_info["status"] != "Success":
                update_fields["Tax Account Error"] = tax_info.get("error", "Unknown error")
            
            # Update the record in Airtable
            update_result = update_airtable_record(record_id, update_fields)
            
            # Check if the update was successful
            if "error" in update_result:
                print(f"Failed to update record {record_id}: {update_result.get('error')}")
            else:
                print(f"Successfully updated record {record_id}")
            
            # Add a delay to avoid hitting rate limits
            time.sleep(1)
        else:
            print(f"No block/lot found for record {record_id}")

if __name__ == "__main__":
    main()
