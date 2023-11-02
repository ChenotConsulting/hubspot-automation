from hubspot import HubSpot
from hubspot.crm.contacts import PublicObjectSearchRequest, ApiException
import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime, timedelta, timezone
import time
from liProfile import liProfile

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
        # print(contacts)
        return contacts
    except ApiException as e: 
        print(f'Error: {e}')
        return {f'Exception: {e}'}

def getAllContacts():
    try:
        contacts = api_client.crm.contacts.get_all(properties=['firstname', 'lastname', 'jobtitle', 'company', 'lifecyclestage', 'source_channel', 'hs_lead_status', 'hublead_linkedin_profile_url'])
        
        return contacts
        # for contact in contacts: 
        #     if(contact.properties):
        #         print(contact)
    except ApiException as e: 
        print(f'Error: ${e}')
        return {f'Exception: {e}'} 

def getAllProperties():
    try:
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }

        response = requests.get(url=f'{API_URL}/properties/v1/contacts/properties', headers=headers)
        jsonResponse = json.loads(response.content)

        for r in jsonResponse:      
            print(f'Name: ${r["name"]}')

        # print(response.content)
    except Exception as e: 
        print(f'Error: ${e}')

def generateLinkedInMessage():
    # TODO: get all tasks due and generate a linkedin message for each one then send it via LinkedIn
    print('TODO')

    # liprofile = liProfile()
    # contacts = getAllContacts()

    # for contact in contacts:
    #     try:
    #         if(contact.properties['lifecyclestage'] == 'lead' and contact.properties['source_channel'] == None and contact.properties['hs_lead_status'] == None):
    #             profileName = str(contact.properties['hublead_linkedin_profile_url']).removeprefix('https://www.linkedin.com/in/')
    #             profileData = liprofile.getLIProfileDetails(profileName)
    #             print(profileData)
    #     except Exception as e:
    #         print(f'Exception: {e}')

def createLinkedInMessageTask(vid):
    try:
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }

        now = datetime.now()
        target_date = now + timedelta(days=2)
        target_datetime = target_date.replace(hour=9, minute=0, second=0, microsecond=0)
        ts = time.mktime(target_datetime.timetuple()) * 1000

        data=json.dumps({
            "properties": {
                "hs_timestamp": int(ts),
                "hs_task_body": "",
                "hubspot_owner_id": os.getenv('OWNER_ID'),
                "hs_task_subject": "Send personalised LI message",
                "hs_task_status": "NOT_STARTED",
                "hs_task_priority": "HIGH",
                "hs_task_type":"TODO",
                "hs_queue_membership_ids": "18772971"
            },
            "associations": [
                {
                    "to": {
                        "id": vid
                    },
                    "types": [
                        {
                            "associationCategory": "HUBSPOT_DEFINED",
                            "associationTypeId": 204
                        } 
                    ]
                }
            ]
        })

        requests.post(url=f'{API_URL}/crm/v3/objects/tasks', headers=headers, data=data)
    except Exception as e:
        print(f'Exception: {e}')

def updateNewlyImportedContacts():
    contacts = getAllContacts()

    for contact in contacts:
        try:
            if(contact.properties['lifecyclestage'] == 'lead' and (contact.properties['source_channel'] == None or contact.properties['source_channel'] == '') and (contact.properties['hs_lead_status'] == None or contact.properties['hs_lead_status'] == '')):
                print(contact)
                vid = contact.id

                headers = {
                    'Authorization': f'Bearer {ACCESS_TOKEN}',
                    'Content-Type': 'application/json'
                }

                data=json.dumps({
                    "properties": [
                        {
                            'property': 'source_channel',
                            'value': 'LINKEDIN'
                        },
                        {
                            'property': 'hs_lead_status',
                            'value': 'LI_CONNECT_OK'
                        }
                    ]
                })

                response = requests.post(url=f'{API_URL}/contacts/v1/contact/vid/{vid}/profile', headers=headers, data=data)

                if(response.status_code == 204):
                    createLinkedInMessageTask(vid)
                    
        except Exception as e:
            print(f'Exception: {e}')

def main(args):
    print(args)
    if args == 'Generate LinkedIn Message':
        generateLinkedInMessage()
    if args == 'Update newly imported contacts':
        updateNewlyImportedContacts()

if __name__ == "__main__":
        options = ['Generate LinkedIn Message', 'Update newly imported contacts']
        print("Select an option:")
        for index, option in enumerate(options):
            print(f"{index+1}) {option}")

        selection = input("Enter the number of your choice: ")
        if selection.isdigit() and 1 <= int(selection) <= len(options):
            selected_option = options[int(selection) - 1]

        main(selected_option)