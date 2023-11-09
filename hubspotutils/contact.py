import requests
import json
import os
from datetime import datetime, time
from dotenv import load_dotenv
from hubspotutils.task import Task
from hubspot import HubSpot
from hubspot.crm.contacts import PublicObjectSearchRequest, ApiException
from hubspot.crm.associations.v4 import BatchInputPublicFetchAssociationsBatchRequest, ApiException

class Contact():
    load_dotenv()
    ENV = ''
    ACCESS_TOKEN = ''
    OWNER_ID = ''
    API_URL = os.getenv('HUBSPOT_API_URL')
    hubspotTask = None

    def __init__(self, env):
        ENV = env
        self.hubspotTask = Task(env)

        if ENV == 'prod':
            self.ACCESS_TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN')
            self.OWNER_ID = os.getenv('HUBSPOT_OWNER_ID')
        if ENV == 'test':
            self.ACCESS_TOKEN = os.getenv('TEST_HUBSPOT_ACCESS_TOKEN')
            self.OWNER_ID = os.getenv('TEST_HUBSPOT_OWNER_ID')

    def getAllContacts(self):
        try:
            api_client = HubSpot(access_token=self.ACCESS_TOKEN)
            contacts = api_client.crm.contacts.get_all(properties=['firstname', 'lastname', 'jobtitle', 'company', 'lifecyclestage', 'source_channel', 'hs_lead_status', 'hublead_linkedin_profile_url'])
            
            return contacts
        except ApiException as e: 
            print(f'Error: ${e}')
            return {f'Exception: {e}'} 

    def updateContactProperties(self, contact):
        try:
            if(contact.properties['lifecyclestage'] == 'lead' and (contact.properties['source_channel'] == None or contact.properties['source_channel'] == '') and (contact.properties['hs_lead_status'] == None or contact.properties['hs_lead_status'] == '')):
                print(f'Updating contact: {contact.properties["firstname"]} {contact.properties["lastname"]}')
                vid = contact.id

                headers = {
                    'Authorization': f'Bearer {self.ACCESS_TOKEN}',
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

                response = requests.post(url=f'{self.API_URL}/contacts/v1/contact/vid/{vid}/profile', headers=headers, data=data)

                if(response.status_code == 204):
                    self.hubspotTask.createLinkedInMessageTask(vid)
                else: 
                    print(f'Could not updated contact {contact.properties["firstname"]} {contact.properties["lastname"]} with status code: {response.status_code}: \n{response.content}')
                    
        except Exception as e:
            print(f'Exception: {e}')

    def getContactLinkedInURL(self, vid):
        print(f'Getting contact {vid} LinkedIn URL')
        try:
            api_client = HubSpot(access_token=self.ACCESS_TOKEN)
            contact = api_client.crm.contacts.basic_api.get_by_id(contact_id=vid, properties=['hublead_linkedin_profile_url'])
            return contact
        except Exception as e:
            print(f'Error getting contact {vid}: {e}')

    def updateContactMessageSent(self, vid):
        print(f'Updating contact after LinkedIn message sent at {datetime.now().isoformat()}')

        try:
            print(f'Updating contact: {vid}')

            headers = {
                'Authorization': f'Bearer {self.ACCESS_TOKEN}',
                'Content-Type': 'application/json'
            }

            data=json.dumps({
                "properties": [
                    {
                        'property': 'hs_lead_status',
                        'value': 'LI_1ST_MSG'
                    }
                ]
            })

            response = requests.post(url=f'{self.API_URL}/contacts/v1/contact/vid/{vid}/profile', headers=headers, data=data)

            if(response.status_code == 204):
                print(f'Updated contact {vid}')
            else: 
                print(f'Could not update contact {vid} with status code: {response.status_code}: \n{response.content}')
                    
        except Exception as e:
            print(f'Exception: {e}')

    def getContactProperties(self):
        return None
    
    def searchNewlyImportedContacts(self):
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
            api_client = HubSpot(access_token=self.ACCESS_TOKEN)
            contacts = api_client.crm.contacts.search_api.do_search(public_object_search_request=public_object_search_request)
            # print(contacts)
            return contacts
        except ApiException as e: 
            print(f'Error: {e}')
            return {f'Exception: {e}'}