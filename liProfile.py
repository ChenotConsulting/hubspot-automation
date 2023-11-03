from liLogin import LILogin
from fastapi import FastAPI, HTTPException
from datetime import datetime

class liProfile():
    def getLIProfileDetails(self, profileLink, action):
        print(f'Getting profile {profileLink} details at {datetime.now().isoformat()}')
        liLogin = LILogin()
        liLogin.setup_method()    
        details = liLogin.runLILogin(url=f'https://linkedin.com/in/{profileLink}', action=action, message='')
        liLogin.teardown_method()

        # return details
        if (details == ['', '', '']):
            raise HTTPException(status_code=404, detail="Data not found")
        else:        
            return details
    
    def sendLinkedInMessage(self, profileLink, action, message):
        print(f'Sending LinkedIn message for {profileLink} at {datetime.now().isoformat()}')
        try:
            liLogin = LILogin()
            liLogin.setup_method()    
            liLogin.runLILogin(url=f'https://linkedin.com/in/{profileLink}', action=action, message=message)
            liLogin.teardown_method()

            return True
        except Exception as e:
            return False

    app = FastAPI()

    @app.get("/linkedin/profile/{profile_name}", status_code=200)
    async def getProfileData(self, profile_name):
        try:
            return self.getLIProfileDetails(profile_name)
        except Exception as e:
            return {"Exception": e}

    @app.post("/linkedin/profile/{profile_name}/message/send", status_code=201)
    async def generateMessageForLinkedInProfile(profile_name: str):
        try:
            return {"message": "Hello World"}
        except Exception as e:
            return {"Exception": e}