import os
from dotenv import load_dotenv
from zenrows import ZenRowsClient
from bs4 import BeautifulSoup as bs 
import requests 

class ZenRowScraper:
    load_dotenv()
    API_KEY = os.getenv('ZEN_ROW_API_KEY')
    client = ZenRowsClient(API_KEY)
    url = "https://linkedin.com/" 
    params = {
        "js_render": "true", # 5 credits
        "antibot": "false", # 5 credits
        "block_resources": "image,media,font",
        "session_id": 12345
    }   

    def getProfileData(self, profile_name):
        self.url += profile_name

        response = self.client.get(self.url, params=self.params)

        print(response.text)

    def linkedInLogin():
        LOGIN_URL = "https://www.linkedin.com/home"
        with requests.session() as s:
            req = s.get(LOGIN_URL).text 
            html = bs(req,"html.parser") 
            csrf_token = html.find("input", {"name": "loginCsrfParam"}).attrs["value"]

        URL = "https://www.linkedin.com/uas/login-submit" 
 
        headers = {
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        payload = { 
            "loginCsrfParam": csrf_token,
            "session_key": os.getenv('LINKEDIN_USERNAME'), 
            "session_password": os.getenv('LINKEDIN_PASSWORD'),
            "session_redirect": {
                "trk": "homepage-basic_sign-in-submit",
                "controlId": "d_homepage-guest-home-homepage-basic_sign-in-submit-btn",
                "pageInstance": "urn:li:page:d_homepage-guest-home_jsbeacon;Sa5Yyu9wSY6KjejVP2OI5w=="
            }
        } 
        s = requests.session() 
        response = s.post(URL, data=payload, headers=headers) 
        print(response.status_code) # If the request went Ok we usually get a 200 status. 