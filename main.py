import sys
from datetime import datetime
from linkedin.liProfile import liProfile
from hubspotutils.contact import Contact
from hubspotutils.task import Task
from database.mongodb import MongoDB
from ai.openai import OpenAI

class Main():
    def __init__(self, env):
        self.ENV = env
        self.hubspotTask = Task(env)
        self.hubspotContact = Contact(env)
        self.openai = OpenAI(env)

    def generateLinkedInMessage(self):
        print(f'Starting generating LinkedInMessages at {datetime.now().isoformat()}')
        tasks_due = self.hubspotTask.getTasksDue()
        print(f'{len(tasks_due)} tasks found.')

        for task in tasks_due:
            association = self.hubspotTask.getTaskAssociation(task['id'])
            vid = association['results'][0]['to'][0]['toObjectId']
            contact = self.hubspotContact.getContactLinkedInURL(vid)
            
            liprofile = liProfile()
            try:            
                profileName = str(contact.properties['hublead_linkedin_profile_url']).removeprefix('https://www.linkedin.com/in/')
                print(f'Starting generating LinkedIn message for {profileName} at {datetime.now().isoformat()}')
                profileData = liprofile.getLIProfileDetails(profileName, 'profile_data')
                message = self.openai.generateLinkedInPersonalisedMessage(profileData[0], profileData[1], profileData[2])
                if(liprofile.sendLinkedInMessage(profileName, 'send_message', message)):
                    self.hubspotTask.markTaskCompleted(task['id'])
                    self.hubspotContact.updateContactMessageSent(vid)
                    print(f'Completed sending LinkedIn Message for {profileData[0]} at {datetime.now().isoformat()}')
                else:
                    print(f'Could not send LinkedIn message for {profileData[0]}')
            except Exception as e:
                print(f'Error generating LinkedIn message for {profileData[0]}: {e}')

        print(f'Completed sending {len(tasks_due)} messages at {datetime.now().isoformat()}')

    def testGenerateLinkedInMessage(self):
        print(f'Starting generating LinkedInMessages at {datetime.now().isoformat()}')
        tasks_due = self.hubspotTask.getTasksDue()
        # tasks_due = self.hubspotTask.getAllTasks()

        for task in tasks_due:
            association = self.hubspotTask.getTaskAssociation(task['id'])
            vid = association['results'][0]['to'][0]['toObjectId']
            
            liprofile = liProfile()
            try:            
                profileName = 'sakina-chenot-7a8a7936'
                print(f'Starting generating LinkedIn message for {profileName} at {datetime.now().isoformat()}')
                profileData = liprofile.getLIProfileDetails(profileName, 'profile_data')
                message = self.openai.generateLinkedInPersonalisedMessage(profileData[0], profileData[1], profileData[2])
                if(liprofile.sendLinkedInMessage(profileName, 'send_message', message)):
                    self.hubspotTask.markTaskCompleted(task['id'])
                    self.hubspotContact.updateContactMessageSent(vid)
                    print(f'Completed sending LinkedIn Message for {profileData[0]} at {datetime.now().isoformat()}')
                else:
                    print(f'Could not send LinkedIn message for {profileData[0]}')
            except Exception as e:
                print(f'Error generating LinkedIn message for {profileData[0]}: {e}')

    def updateNewlyImportedContacts(self):
        print(f'Updating newly imported contacts at {datetime.now().isoformat()}')
        contacts = self.hubspotContact.getAllContacts()

        for contact in contacts:
            self.hubspotContact.updateContactProperties(contact)

        print(f'Finished updating {len(contacts)} contacts at {datetime.now().isoformat()}')

    def main(self, args):
        print(f'Commencing activity: {args}')
        if args == 'Generate LinkedIn Message':
            self.generateLinkedInMessage()
        if args == 'Update newly imported contacts':
            self.updateNewlyImportedContacts()
        if args == 'TEST Generate LinkedIn Message':
            self.testGenerateLinkedInMessage()
        if args == 'TEST Update newly imported contacts':
            self.updateNewlyImportedContacts()
        if args == 'TEST MongoDB':
            mongo = MongoDB()
            mongo.testConnection()

if __name__ == "__main__":
    arg = ''
    env = 'prod'

    if len(sys.argv) > 1:
        if sys.argv[1] == '1':
            arg = 'Generate LinkedIn Message'
        if sys.argv[1] == '2':
            arg = 'Update newly imported contacts'
        if sys.argv[1] == '3':
            arg = 'TEST Generate LinkedIn Message'
        if sys.argv[1] == '4':
            arg = 'TEST Update newly imported contacts'

        if sys.argv[1] == '3' or sys.argv[1] == '4':
            env = 'test'
    else:
        options = ['Generate LinkedIn Message', 'Update newly imported contacts', 'TEST Generate LinkedIn Message', 'TEST Update newly imported contacts', 'TEST MongoDB']
        print("Select an option:")
        for index, option in enumerate(options):
            print(f"{index+1}) {option}")

        selection = input("Enter the number of your choice: ")
        if selection.isdigit() and 1 <= int(selection) <= len(options):
            selected_option = options[int(selection) - 1]
            arg = selected_option

            if 'TEST' in selected_option:
                env = 'test'
    
    m = Main(env)
    m.main(args=arg)