from hubspot import HubSpot
from hubspot.crm.contacts import PublicObjectSearchRequest, ApiException
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
API_URL = os.getenv('API_URL')
api_client = HubSpot(access_token=ACCESS_TOKEN)

def searchNewlyImportedContacts():
    public_object_search_request = PublicObjectSearchRequest(
        filter_groups=[
            {
                "filters": [
                    {
                        "value": 'lead',
                        "propertyName": "lifecyclestage",
                        "operator": "EQ"
                    },
                    {
                        "values": ['EMAIL', 'EVENT', 'REFERRAl', 'PARTNER', 'LINKEDIN'],
                        "propertyName": "source_channel",
                        "operator": "NOT_IN"
                    },
                    {
                        "values": ['NEW', 'OPEN', 'LI_CONNECT_SENT', 'LI_CONNECT_OK', 'LI_1ST_MSG', 'IN_PROGRESS', 'OPEN_DEAL', 'UNQUALIFIED', 'ATTEMPTED_TO_CONTACT', 'CONNECTED'],
                        "propertyName": "hs_lead_status",
                        "operator": "NOT_IN"
                    }
                ]
            }
        ], limit=10
    )

    try:
        contacts = api_client.crm.contacts.search_api.do_search(public_object_search_request=public_object_search_request)
        print(contacts)
    except ApiException as e: 
        print(f'Error: ${e}')

def getAllContacts():
    try:
        contacts = api_client.crm.contacts.get_all(properties=['firstname', 'lastname', 'jobtitle', 'company', 'lifecyclestage', 'source_channel', 'hs_lead_status', 'hublead_linkedin_profile_url'])
        
        for contact in contacts: 
            if(contact.properties):
                print(contact)
    except ApiException as e: 
        print(f'Error: ${e}')

def getAllProperties():
    try:
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }

        print(f'Headers: {headers}')

        response = requests.get(url=f'{API_URL}/properties/v1/contacts/properties', headers=headers)
        jsonResponse = json.loads(response.content)

        for r in jsonResponse:      
            print(f'Name: ${r["name"]}')

        # print(response.content)
    except Exception as e: 
        print(f'Error: ${e}')

searchNewlyImportedContacts()
# getAllContacts()
# getAllProperties()