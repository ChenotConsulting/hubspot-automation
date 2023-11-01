# Generated by Selenium IDE
import time
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options

class LILogin():
  name = ''
  title = ''
  about = ''

  def setup_method(self):
    self.driver = webdriver.Chrome()
    self.vars = {}
  
  def teardown_method(self):
    self.driver.quit()

  def extractData(self):
    time.sleep(1)
    
    try:
      if(self.driver.find_elements(By.XPATH, "//h1[contains(@class, 'text-heading-xlarge inline t-24 v-align-middle break-words')]")):
        self.name = self.driver.find_element(By.XPATH, "//h1[contains(@class, 'text-heading-xlarge inline t-24 v-align-middle break-words')]").text
      if(self.driver.find_elements(By.XPATH, "//div[contains(@class, 'text-body-medium break-words')]")):
        self.title = self.driver.find_element(By.XPATH, "//div[contains(@class, 'text-body-medium break-words')]").text
      if(self.driver.find_elements(By.XPATH, "//section[starts-with(@id, 'ember')]//div//div//div//div//h2//span[contains(text(), 'About')]//ancestor::section[starts-with(@id, 'ember')]//div[3]//div//div//div//span[1]")):
        self.about = self.driver.find_element(By.XPATH, "//section[starts-with(@id, 'ember')]//div//div//div//div//h2//span[contains(text(), 'About')]//ancestor::section[starts-with(@id, 'ember')]//div[3]//div//div//div//span[1]").text
      # self.driver.find_element(By.XPATH, "//button[contains(@class, 'global-nav__primary-link global-nav__primary-link-me-menu-trigger artdeco-dropdown__trigger artdeco-dropdown__trigger--placement-bottom ember-view')]").click()
      # time.sleep(1)
      # self.driver.find_element(By.XPATH, "//a[contains(@href, 'logout')]").click()
    except Exception as e:
      print(f'Error extracting data: {e}')
  
  def runLILogin(self, url):
    self.teardown_method()
    # Load the environment variables
    load_dotenv()
    LI_USERNAME = os.getenv('LINKEDIN_USERNAME')
    LI_PASSWORD = os.getenv('LINKEDIN_PASSWORD')

    try:
      chrome_options = Options()
      chrome_options.add_argument("user-data-dir=~/Library/Application Support/Google/Chrome/Default")

      self.driver = webdriver.Chrome(options=chrome_options)
      self.driver.get("https://www.linkedin.com/")
      self.driver.set_window_size(1920, 1080)

      if(self.driver.find_elements(By.CSS_SELECTOR, ".sign-in-form__submit-btn--full-width")):
        self.driver.find_element(By.ID, "session_key").click()
        self.driver.find_element(By.ID, "session_key").send_keys(LI_USERNAME)
        self.driver.find_element(By.ID, "session_password").click()
        self.driver.find_element(By.ID, "session_password").send_keys(LI_PASSWORD)
        self.driver.find_element(By.CSS_SELECTOR, ".sign-in-form__submit-btn--full-width").click()
        
      self.driver.get(url)

      if(self.driver.current_url.find('checkpoint') != -1 or self.driver.current_url.find('authwall') != -1): 
        return 'Too many attemps have been made. Please wait and try again later.'
      else:
        self.extractData()
    except Exception as e:
      raise Exception(e)

    return [self.name, self.title, self.about]
  
