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

def get_tax_account_info(block_id, lot_id):
    """Scrape tax account information from Jersey City tax website using block and lot IDs."""
    url = "http://taxes.cityofjerseycity.com/ViewPay?accountNumber=115998"
    
    # Form data to submit
    form_data = {
        "Block": block_id,
        "Lot": lot_id
    }
    
    try:
        # Submit the form with block and lot IDs
        response = requests.post(url, data=form_data)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check if we got a valid response
        if response.status_code == 200:
            # Extract the Account# from the response
            account_div = soup.find('div', string=lambda text: text and 'Account#:' in text)
            account_number = None
            
            if account_div:
                # Try to find the account number in the next sibling or parent container
                next_div = account_div.find_next('div')
                if next_div:
                    account_number = next_div.get_text(strip=True)
            
            tax_data = {
                "url": response.url,
                "status": "Success" if account_number else "No Account Found",
                "account_number": account_number
            }
            
            # Extract any additional property information if needed
            property_info = soup.find('div', class_='property-info')
            if property_info:
                tax_data["property_info"] = property_info.get_text(strip=True)
            
            return tax_data
        else:
            return {
                "url": url,
                "status": "Failed",
                "error": f"HTTP Status: {response.status_code}"
            }
    except Exception as e:
        return {
            "url": url,
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
