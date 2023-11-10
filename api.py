from fastapi import FastAPI, HTTPException
from main import Main

app = FastAPI()

@app.post("/automation/hubspot/contacts/update", status_code=204)
def updateContacts(env: str = 'prod'):
    m = Main(env)
    m.updateNewlyImportedContacts()

@app.post("/automation/hubspot/tasks/linkedin/message", status_code=204)
def generateLinkedInMessage(env: str = 'prod'):
    m = Main(env)

    if env == 'prod':
        m.generateLinkedInMessage()
    if env == 'test':
        m.testGenerateLinkedInMessage()