from liLogin import LILogin
from fastapi import FastAPI, HTTPException

class liProfile():
    def getLIProfileDetails(self, profileLink):
        liLogin = LILogin()
        liLogin.setup_method()    
        details = liLogin.runLILogin(url=f'https://linkedin.com/in/{profileLink}')
        liLogin.teardown_method()

        # return details
        if (details == ['', '', '']):
                raise HTTPException(status_code=404, detail="Data not found")
        else:        
            if(details != []):
                # print(details)
                return details
            else:
                for d in details: 
                    # print(f'Name: {d[0]}')
                    # print(f'Title: {d[1]}')
                    # print(f'About: {d[2]}')
                    return d
                
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