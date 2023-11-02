from hubspot import HubSpot
from hubspot.crm.contacts import PublicObjectSearchRequest, ApiException
from hubspot.crm.associations.v4 import BatchInputPublicFetchAssociationsBatchRequest, ApiException
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
    except ApiException as e: 
        print(f'Error: ${e}')
        return {f'Exception: {e}'} 

def getTasksDue():
    try:
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }

        response = requests.get(url=f'{API_URL}/crm/v3/objects/tasks?limit=100&properties=hs_timestamp,hs_task_status,hs_queue_membership_ids', headers=headers)
        jsonResponse = json.loads(response.content)
        tasks_due = []

        for resp in jsonResponse['results']:
            if(resp['properties']['hs_queue_membership_ids'] == '18772971' and resp['properties']['hs_task_status'] == 'NOT_STARTED'):
                task_due_date = datetime.strptime(resp['properties']['hs_timestamp'], '%Y-%m-%dT%H:%M:%SZ')
                # if(task_due_date <= datetime.now()):
                tasks_due.append(resp)
                
        return tasks_due
    except Exception as e: 
        print(f'Error: ${e}')

def getTaskAssociation(task_id):
    try:
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }

        data = json.dumps({
            "inputs": [
                {
                    "id": task_id
                }
            ]
        })

        response = requests.post(url=f'{API_URL}/crm/v4/associations/0-27/0-1/batch/read', headers=headers, data=data)                
        return response.json()
    except Exception as e: 
        print(f'Error: ${e}')

def getContactLinkedInURL(vid):
    contact = api_client.crm.contacts.basic_api.get_by_id(contact_id=vid, properties=['hublead_linkedin_profile_url'])
    return contact

def generateLinkedInPersonalisedMessage(name, title, about):
    prompt = 'At ProfessionalPulse, we\'re passionate about leveraging technology to transform the operations of Business Services teams within Professional Services Firms. Our journey began in the dynamic realm of IT and ' \
                    'consultancy, and was inspired by real-life challenges faced by these teams. Today, we use our expertise and unique approach to help these teams navigate their challenges, boost efficiency, and strike a balance ' \
                    'between their professional and personal lives. Discover more about our ethos, our journey, and how we can help you. \n' \
                    'You are tasked with writing a LinkedIn message based on this profile: \n' + \
                    'Name: ' + name + '\n' + \
                    'Title: ' + title + '\n' + \
                    'About: ' + about + '\n' + \
                    'The message must be personalised using their first name, it must be short, written in UK English and sound professional (but using simple language) as the target audience are professionals, and finish with a call to action to ' \
                    'book a free 30 minutes audit consultation via the following link: https://tinyurl.com/4f79etr4. Add something around that even if they are not interested in a professional collaboration, ' \
                    'I\'d love to speak to them as a subject matter expert in legal operations. \n' \
                    'Sign with Jean-Philippe Chenot \n' + \
                    'Here is an example of personalisation: \n' \
                    'Your impressive tenure as the COO at rradar, especially your expertise in Legal Technology and Process Improvement, resonates with the core ethos of our consultancy. ' \
                    'It\'s evident that we share a common goal - refining operational workflows to unlock a higher degree of efficiency. \n' \
                    'Do not add a subject, and do not add my title in the signature. Only use my name.'

    api_url = 'https://api.openai.com/v1/chat/completions'
    request_data = {
        "model": "gpt-4",
        "temperature": 0.3,
        "n": 1,
        "messages": [
            {
                "role": "system",
                "content": "You are a sales manager for a consultancy called ProfessionalPulse."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + os.getenv('OPENAI_API_KEY')
    }

    response = requests.post(api_url, headers=headers, json=request_data)
    data = response.json()
    message = data['choices'][0]['message']['content']
    print(message)

def generateLinkedInMessage():
    tasks_due = getTasksDue()

    for task in tasks_due:
        association = getTaskAssociation(task['id'])
        vid = association['results'][0]['to'][0]['toObjectId']
        contact = getContactLinkedInURL(vid)
        
        liprofile = liProfile()
        try:
            profileName = str(contact.properties['hublead_linkedin_profile_url']).removeprefix('https://www.linkedin.com/in/')
            profileData = liprofile.getLIProfileDetails(profileName)
            message = generateLinkedInPersonalisedMessage(profileData[0], profileData[1], profileData[2])
            print(message)
        except Exception as e:
            print(f'Exception: {e}')

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