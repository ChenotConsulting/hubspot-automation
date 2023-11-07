# HubSpot automation
Various automation tasks for my HubSpot CRM and LinkedIn lead-gen framework. 

To run this application, you need to add a .env file with the following key/value pairs.
```
# HUBSPOT
ACCESS_KEY=[YOUR HUBSPOT PRIVATE APPLICATION API KEY] [Docs](https://developers.hubspot.com/docs/api/private-apps)
TEST_ACCESS_TOKEN=[YOUR HUBSPOT TEST ACCOUNT TOKEN]
API_URL=https://api.hubapi.com
OWNER_ID=[THE OWNER ID OF THE TASK]
TEST_OWNER_ID=[THE TEST OWNER ID OF THE TASK]

# LINKEDIN
LINKEDIN_USERNAME=[YOUR LINKEDIN USERNAME]
LINKEDIN_PASSWORD=[YOUR LINKEDIN PASSWORD]

# OPENAI
OPENAI_API_KEY=[YOUR OPENAI API KEY]
```

Once the variables are set up, you can run the application with ```python3 main.py X e.g. python3 main.py 4``` where `X` is:
1. Generate LinkedIn Message
2. TEST Generate LinkedIn Message
3. Update newly imported contacts
4. TEST update newly imported contacts