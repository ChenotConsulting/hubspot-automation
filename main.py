from hubspot import HubSpot
from hubspot.crm.contacts import PublicObjectSearchRequest, ApiException
from hubspot.crm.associations.v4 import BatchInputPublicFetchAssociationsBatchRequest, ApiException
import os
from dotenv import load_dotenv
import requests
import json
import sys
from datetime import datetime, timedelta, timezone
import time
from liProfile import liProfile

class Main():
    load_dotenv()
    ENV = ''
    ACCESS_TOKEN = ''
    OWNER_ID = ''
    API_URL = os.getenv('API_URL')

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

    def getAllContacts(self):
        try:
            api_client = HubSpot(access_token=self.ACCESS_TOKEN)
            contacts = api_client.crm.contacts.get_all(properties=['firstname', 'lastname', 'jobtitle', 'company', 'lifecyclestage', 'source_channel', 'hs_lead_status', 'hublead_linkedin_profile_url'])
            
            return contacts
        except ApiException as e: 
            print(f'Error: ${e}')
            return {f'Exception: {e}'} 

    def getTasksDue(self):
        try:
            headers = {
                'Authorization': f'Bearer {self.ACCESS_TOKEN}',
                'Content-Type': 'application/json'
            }

            response = requests.get(url=f'{self.API_URL}/crm/v3/objects/tasks?limit=100&properties=hs_timestamp,hs_task_status,hs_queue_membership_ids', headers=headers)
            jsonResponse = json.loads(response.content)
            tasks_due = []

            for resp in jsonResponse['results']:
                if(resp['properties']['hs_queue_membership_ids'] == '18772971' and resp['properties']['hs_task_status'] == 'NOT_STARTED'):
                    task_due_date = datetime.strptime(resp['properties']['hs_timestamp'], '%Y-%m-%dT%H:%M:%SZ')
                    if(task_due_date <= datetime.now()):
                        tasks_due.append(resp)
                    
            return tasks_due
        except Exception as e: 
            print(f'Error: ${e}')

    def getTaskAssociation(self, task_id):
        print(f'Getting task association for task {task_id}')

        try:
            headers = {
                'Authorization': f'Bearer {self.ACCESS_TOKEN}',
                'Content-Type': 'application/json'
            }

            data = json.dumps({
                "inputs": [
                    {
                        "id": task_id
                    }
                ]
            })

            response = requests.post(url=f'{self.API_URL}/crm/v4/associations/0-27/0-1/batch/read', headers=headers, data=data)                
            return response.json()
        except Exception as e: 
            print(f'Task {task_id} association error: ${e}')

    def getContactLinkedInURL(self, vid):
        print(f'Getting contact {vid} LinkedIn URL')
        try:
            api_client = HubSpot(access_token=self.ACCESS_TOKEN)
            contact = api_client.crm.contacts.basic_api.get_by_id(contact_id=vid, properties=['hublead_linkedin_profile_url'])
            return contact
        except Exception as e:
            print(f'Error getting contact {vid}: {e}')

    def generateLinkedInPersonalisedMessage(self, name, title, about):
        print(f'Generating LinkedIn personalised message for {name} with OpenAI at {datetime.now().isoformat()}')
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

        print(f'Message for {name} generated at {datetime.now().isoformat()}')
        return message

    def markTaskCompleted(self, task_id):
        print(f'Updating task {task_id}')
        try:
            headers = {
                'Authorization': f'Bearer {self.ACCESS_TOKEN}',
                'Content-Type': 'application/json'
            }

            now = datetime.now()
            ts = time.mktime(now.timetuple()) * 1000

            data = json.dumps({
                "properties": {
                    "hs_timestamp": int(ts),
                    "hs_task_status": "COMPLETED",
                }
            })

            response = requests.patch(url=f'{self.API_URL}/crm/v3/objects/tasks/{task_id}', headers=headers, data=data)
            
            if(response.status_code == 200):
                print(f'Task {task_id} has been marked as completed.')
            else:
                print(f'Task {task_id} was not completed. Status code: {response.status_code}')
        except Exception as e: 
            print(f'Error: ${e}')

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

    def generateLinkedInMessage(self):
        print(f'Starting generating LinkedInMessages at {datetime.now().isoformat()}')
        tasks_due = self.getTasksDue()

        for task in tasks_due:
            association = self.getTaskAssociation(task['id'])
            vid = association['results'][0]['to'][0]['toObjectId']
            contact = self.getContactLinkedInURL(vid)
            
            liprofile = liProfile()
            try:            
                profileName = str(contact.properties['hublead_linkedin_profile_url']).removeprefix('https://www.linkedin.com/in/')
                print(f'Starting generating LinkedIn message for {profileName} at {datetime.now().isoformat()}')
                profileData = liprofile.getLIProfileDetails(profileName, 'profile_data')
                message = self.generateLinkedInPersonalisedMessage(profileData[0], profileData[1], profileData[2])
                if(liprofile.sendLinkedInMessage(profileName, 'send_message', message)):
                    self.markTaskCompleted(task['id'])
                    self.updateContactMessageSent(vid)
                    print(f'Completed sending LinkedIn Message for {profileData[0]} at {datetime.now().isoformat()}')
                else:
                    print(f'Could not send LinkedIn message for {profileData[0]}')
            except Exception as e:
                print(f'Error generating LinkedIn message for {profileData[0]}: {e}')

    def testGenerateLinkedInMessage(self):
        print(f'Starting generating LinkedInMessages at {datetime.now().isoformat()}')
        tasks_due = self.getTasksDue()

        for task in tasks_due:
            association = self.getTaskAssociation(task['id'])
            vid = association['results'][0]['to'][0]['toObjectId']
            contact = self.getContactLinkedInURL(vid)
            
            liprofile = liProfile()
            try:            
                profileName = 'sakina-chenot-7a8a7936'
                print(f'Starting generating LinkedIn message for {profileName} at {datetime.now().isoformat()}')
                profileData = liprofile.getLIProfileDetails(profileName, 'profile_data')
                message = self.generateLinkedInPersonalisedMessage(profileData[0], profileData[1], profileData[2])
                if(liprofile.sendLinkedInMessage(profileName, 'send_message', message)):
                    self.markTaskCompleted(task['id'])
                    self.updateContactMessageSent(vid)
                    print(f'Completed sending LinkedIn Message for {profileData[0]} at {datetime.now().isoformat()}')
                else:
                    print(f'Could not send LinkedIn message for {profileData[0]}')
            except Exception as e:
                print(f'Error generating LinkedIn message for {profileData[0]}: {e}')

    def createLinkedInMessageTask(self, vid):
        print(f'Creating LinkedIn task for {vid}')

        try:
            headers = {
                'Authorization': f'Bearer {self.ACCESS_TOKEN}',
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
                    "hubspot_owner_id": self.OWNER_ID,
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

            response = requests.post(url=f'{self.API_URL}/crm/v3/objects/tasks', headers=headers, data=data)

            if response.status_code == 201:
                print(f'Task created successfully for {vid}')
            else: 
                print(f'Could not create task for {vid} with status code: {response.status_code}: \n{response.content}')
        except Exception as e:
            print(f'Error creating task for {vid}: {e}')

    def updateNewlyImportedContacts(self):
        print(f'Updating newly imported contacts at {datetime.now().isoformat()}')
        contacts = self.getAllContacts()

        for contact in contacts:
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
                        self.createLinkedInMessageTask(vid)
                    else: 
                        print(f'Could not updated contact {contact.properties["firstname"]} {contact.properties["lastname"]} with status code: {response.status_code}: \n{response.content}')
                        
            except Exception as e:
                print(f'Exception: {e}')

    def main(self, args):
        print(f'Commencing activity: {args}')
        if args == 'Generate LinkedIn Message':
            self.ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
            self.OWNER_ID = os.getenv('OWNER_ID')
            self.generateLinkedInMessage()
        if args == 'Update newly imported contacts':
            self.ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
            self.OWNER_ID = os.getenv('OWNER_ID')
            self.updateNewlyImportedContacts()
        if args == 'TEST Generate LinkedIn Message':
            self.ACCESS_TOKEN = os.getenv('TEST_ACCESS_TOKEN')
            self.OWNER_ID = os.getenv('TEST_OWNER_ID')
            self.testGenerateLinkedInMessage()
        if args == 'TEST Update newly imported contacts':
            self.ACCESS_TOKEN = os.getenv('TEST_ACCESS_TOKEN')
            self.OWNER_ID = os.getenv('TEST_OWNER_ID')
            self.updateNewlyImportedContacts()

if __name__ == "__main__":
        m = Main()

        if len(sys.argv) > 1:
            if sys.argv[1] == '1':
                m.main('Generate LinkedIn Message')
            if sys.argv[1] == '2':
                m.main('Update newly imported contacts')
            if sys.argv[1] == '3':
                m.main('TEST Generate LinkedIn Message')
            if sys.argv[1] == '4':
                m.main('TEST Update newly imported contacts')
        else:
            options = ['Generate LinkedIn Message', 'Update newly imported contacts', 'TEST Generate LinkedIn Message', 'TEST Update newly imported contacts']
            print("Select an option:")
            for index, option in enumerate(options):
                print(f"{index+1}) {option}")

            selection = input("Enter the number of your choice: ")
            if selection.isdigit() and 1 <= int(selection) <= len(options):
                selected_option = options[int(selection) - 1]
      
            m.main(args=selected_option)