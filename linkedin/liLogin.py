
import time
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime

class LILogin():
  # name = ''
  # title = ''
  # about = ''

  def setup_method(self):
    print('Launching headless Chrome driver')
    options = webdriver.ChromeOptions()
    # COMMENT OUT FOR SHOWING THE BROWSER WHILE TESTING
    # options.add_argument('--headless')
    options.add_argument("user-data-dir=~/Library/Application Support/Google/Chrome/Default")
    self.driver = webdriver.Chrome(options=options)
    self.vars = {}
  
  def teardown_method(self):
    print('Closing headless Chrome driver')
    self.driver.quit()

  def extractData(self):
    print('Extracting data')
    time.sleep(1)
    
    try:
      if(self.driver.find_elements(By.XPATH, "//h1[contains(@class, 'text-heading-xlarge inline t-24 v-align-middle break-words')]")):
        self.name = self.driver.find_element(By.XPATH, "//h1[contains(@class, 'text-heading-xlarge inline t-24 v-align-middle break-words')]").text
      else:
        self.name = ''
      if(self.driver.find_elements(By.XPATH, "//div[contains(@class, 'text-body-medium break-words')]")):
        self.title = self.driver.find_element(By.XPATH, "//div[contains(@class, 'text-body-medium break-words')]").text
      else: 
        self.title = ''
      if(self.driver.find_elements(By.XPATH, "//section[starts-with(@id, 'ember')]//div//div//div//div//h2//span[contains(text(), 'About')]//ancestor::section[starts-with(@id, 'ember')]//div[3]//div//div//div//span[1]")):
        self.about = self.driver.find_element(By.XPATH, "//section[starts-with(@id, 'ember')]//div//div//div//div//h2//span[contains(text(), 'About')]//ancestor::section[starts-with(@id, 'ember')]//div[3]//div//div//div//span[1]").text
      else:
        self.about = ''

      print(f'Data extracted for {self.name}')
    except Exception as e:
      print(f'Error extracting data: {e}')
  
  def sendMessage(self, message):
    try:
      time.sleep(1)
      self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Message') and contains(@class, 'pvs-profile-actions__action')]").click()
      time.sleep(1)
      message_input = self.driver.find_element(By.XPATH, "//div[contains(@class, '__contenteditable')]//p")
      message_input.send_keys(message)
      time.sleep(1)
      self.driver.find_element(By.XPATH, "//button[contains(@class, 'msg-form__send-button')]").click()
    except Exception as e:
      print(f'Error sending LinkedIn message: {e}')

  def runLILogin(self, url, action, message):
    print(f'Running LinkedIn login for URL {url}, for action: {action} at {datetime.now().isoformat()}')
    # Load the environment variables
    load_dotenv()
    LI_USERNAME = os.getenv('LINKEDIN_USERNAME')
    LI_PASSWORD = os.getenv('LINKEDIN_PASSWORD')

    try:
      self.driver.get("https://www.linkedin.com/")

      if(self.driver.find_elements(By.CSS_SELECTOR, ".sign-in-form__submit-btn--full-width")):
        self.driver.find_element(By.ID, "session_key").click()
        self.driver.find_element(By.ID, "session_key").send_keys(LI_USERNAME)
        self.driver.find_element(By.ID, "session_password").click()
        self.driver.find_element(By.ID, "session_password").send_keys(LI_PASSWORD)
        self.driver.find_element(By.CSS_SELECTOR, ".sign-in-form__submit-btn--full-width").click()
        print('Logged into LinkedIn')
      else:
        print('Skipped login')
        
      self.driver.get(url)

      if(self.driver.current_url.find('checkpoint') != -1 or self.driver.current_url.find('authwall') != -1): 
        print('Too many attemps have been made. Please wait and try again later.')
        return False
      else:
        if(action == 'profile_data'):
          self.extractData()
          return [self.name, self.title, self.about]
        if(action == 'send_message'):
          self.sendMessage(message=message)
          return True
    except Exception as e:
      raise Exception(e)

    
  
