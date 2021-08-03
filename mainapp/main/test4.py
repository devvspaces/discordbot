from threading import Thread
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor

#Your script will execute on each of the browser, device and OS combinations	 
token = 'ODQyMTc4NTk2NDIwMDU5MTU4.YPsSmw.l9pMg1Rs5e_fjD76LpWPDcWpSaw'



# driver = webdriver.Chrome('chromedriver.exe')

time.sleep(3)

# Login discord

By.Cl
# Find server
link_to_server = 'https://discord.gg/vRKcFJSk'
driver.get(link_to_server)
time.sleep(10)

#run_session function searches for 'BrowserStack' on google.com
def run_session():
  chrome_options = webdriver.ChromeOptions()
  prefs = {"profile.managed_default_content_settings.images": 2}
  chrome_options.add_experimental_option("prefs", prefs)

  driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)
  
  driver.get('https://discord.com/login')
  js = 'function login(token) {setInterval(() => {document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `"${token}"`}, 50);setTimeout(() => {location.reload();}, 500);}'

  WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'IdOfMyElement')))
  driver.execute_script(js + f'login("{token}")')

  if not "Google" in driver.title:
      raise Exception("Unable to load google page!")
  elem = driver.find_element_by_name("q")
  elem.send_keys("BrowserStack")
  elem.submit()
  try:
      WebDriverWait(driver, 5).until(EC.title_contains("BrowserStack"))
      driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "Title matched!"}}')
  except TimeoutException:
      driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "Title not matched"}}')
  print(driver.title)
  driver.quit()

#The `ThreadPoolExecutor` function takes `max_workers` as an argument which represents the number of threads in threadpool and execute multiple sessions on each of the thread as and when each session completes execution.
with ThreadPoolExecutor(max_workers=2) as executor:
	executor.map(run_session, caps)
