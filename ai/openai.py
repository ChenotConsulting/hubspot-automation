import os
from dotenv import load_dotenv
import requests
from datetime import datetime

class OpenAI():
    load_dotenv()
    ENV = ''

    def __init__(self, env):
        self.ENV = env

    def generateLinkedInPersonalisedMessage(self, name, title, about):
        print(f'Generating LinkedIn personalised message for {name} with OpenAI at {datetime.now().isoformat()}')

        if self.ENV == 'prod':
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
        else:
            return 'This is a mock message generated by OpenAI'
