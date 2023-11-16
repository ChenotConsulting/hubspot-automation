from time import mktime
import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

class Task():
    load_dotenv()

    def __init__(self, env):
        self.ENV = env
        self.API_URL = os.getenv('HUBSPOT_API_URL')

        if env == 'prod':
            self.ACCESS_TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN')
            self.OWNER_ID = os.getenv('HUBSPOT_OWNER_ID')
        if env == 'test':
            self.ACCESS_TOKEN = os.getenv('TEST_HUBSPOT_ACCESS_TOKEN')
            self.OWNER_ID = os.getenv('TEST_HUBSPOT_OWNER_ID')
    
    def getAllTasks(self):
        try:
            headers = {
                'Authorization': f'Bearer {self.ACCESS_TOKEN}',
                'Content-Type': 'application/json'
            }

            response = requests.get(url=f'{self.API_URL}/crm/v3/objects/tasks?properties=hs_queue_membership_ids,hs_task_status,hs_timestamp', headers=headers)
            jsonResponse = json.loads(response.content)
            tasks = [resp for resp in jsonResponse['results']]

            return tasks
        except Exception as e:
            print(f'Error getting all tasks: ${e}')

    def getTasksDue(self):
        try:
            headers = {
                'Authorization': f'Bearer {self.ACCESS_TOKEN}',
                'Content-Type': 'application/json'
            }

            data = {
                'filterGroups': [
                    {
                        'filters': [
                            {
                                'propertyName': 'hs_task_status',
                                'operator': 'EQ',
                                'value': 'NOT_STARTED',
                            },
                            {
                                'propertyName': 'hs_queue_membership_ids',
                                'operator': 'EQ',
                                'value': '18772971',
                            },
                            {
                                'propertyName': 'hs_timestamp',
                                'operator': 'LT',
                                'value': int(mktime(datetime.now().timetuple()) * 1000),
                            }
                        ],
                    },
                ],
                "sorts": [""],
                "properties": [""],
                "limit" : "100"
            }

            response = requests.post(url=f'{self.API_URL}/crm/v3/objects/tasks/search', headers=headers, json=data)
            jsonResponse = json.loads(response.content)
            tasks_due = [resp for resp in jsonResponse['results']]
                    
            return tasks_due
        except Exception as e: 
            print(f'Error search tasks: ${e}')

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

    def markTaskCompleted(self, task_id):
        print(f'Updating task {task_id}')
        try:
            headers = {
                'Authorization': f'Bearer {self.ACCESS_TOKEN}',
                'Content-Type': 'application/json'
            }

            now = datetime.now()
            ts = mktime(now.timetuple()) * 1000

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

    def createLinkedInMessageTask(self, vid):
        print(f'Creating LinkedIn task for {vid}')

        try:
            headers = {
                'Authorization': f'Bearer {self.ACCESS_TOKEN}',
                'Content-Type': 'application/json'
            }

            now = datetime.now()
            target_date = now + timedelta(days=2)
            target_datetime = target_date.replace(hour=8, minute=0, second=0, microsecond=0)
            ts = mktime(target_datetime.timetuple()) * 1000

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