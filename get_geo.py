import os
import requests
import time
import json
from pyairtable import Api
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API keys and IDs from environment variables
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Initialize Airtable client
airtable = Api(AIRTABLE_API_KEY)
table = airtable.table(AIRTABLE_BASE_ID, 'Vacants')

def geocode_address(address):
    """Geocode an address using Google Maps API"""
    full_address = f"{address}, Jersey City, NJ"
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={full_address}&key={GOOGLE_API_KEY}"
    
    response = requests.get(url)
    data = response.json()
    
    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        return {
            'lat': location['lat'],
            'lng': location['lng']
        }
    else:
        print(f"Geocoding error for {address}: {data['status']}")
        return None

def get_geojson(block, lot):
    """Fetch GeoJSON data from NJ Parcels API"""
    url = f"https://njparcels.com/api/v1.0/property/0906_{block}_{lot}.json"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching GeoJSON for Block {block}, Lot {lot}: Status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception fetching GeoJSON for Block {block}, Lot {lot}: {str(e)}")
        return None

def main():
    # Get all records from the Vacants table
    records = table.all()
    print(f"Found {len(records)} records in Vacants table")
    
    for record in records:
        record_id = record['id']
        fields = record['fields']
        
        address = fields.get('Address')
        block = fields.get('Block')
        lot = fields.get('Lot')
        
        if not address:
            print(f"No address found for record {record_id}")
            continue
            
        if not block or not lot:
            print(f"No block or lot found for record {record_id}")
            continue
            
        print(f"Processing: {address}, Block {block}, Lot {lot}")
        
        # Initialize updates dictionary
        updates = {}
        
        # Check if lat and lng are missing
        if 'lat' not in fields or 'lng' not in fields:
            print(f"Geocoding address for {address}")
            geocode_data = geocode_address(address)
            if geocode_data:
                updates['lat'] = geocode_data['lat']
                updates['lng'] = geocode_data['lng']
        else:
            print(f"Lat/lng already exists for {address}, skipping geocoding")
            
        # Check if geojson is missing
        if 'geojson' not in fields:
            print(f"Fetching GeoJSON for Block {block}, Lot {lot}")
            geojson_data = get_geojson(block, lot)
            if geojson_data:
                updates['geojson'] = json.dumps(geojson_data)
        else:
            print(f"GeoJSON already exists for {address}, skipping")
            
        # Update the record only if we have updates to make
        if updates:
            try:
                table.update(record_id, updates)
                print(f"Updated record for {address} with: {', '.join(updates.keys())}")
            except Exception as e:
                print(f"Error updating record for {address}: {str(e)}")
        else:
            print(f"No updates needed for {address}")
            
        # Avoid rate limiting
        time.sleep(1)
        
if __name__ == "__main__":
    main()
