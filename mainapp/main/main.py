import os, sys, ctypes, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC



os.system('cls')
# token = input('Token: ')
token = 'ODQyMTc4NTk2NDIwMDU5MTU4.YPsSmw.l9pMg1Rs5e_fjD76LpWPDcWpSaw'
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

chrome_options = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)
# driver = webdriver.Chrome('chromedriver.exe')

driver.get('https://discord.com/login')
js = 'function login(token) {setInterval(() => {document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `"${token}"`}, 50);setTimeout(() => {location.reload();}, 500);}'
WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='button']")))

# Login discord
driver.execute_script(js + f'login("{token}")')

# Find server
link_to_server = 'https://discord.gg/vRKcFJSk'
# 'https://discord.gg/354Vs4Zu'
# 'https://discord.gg/5R55frmx'
# 'https://discord.gg/NUFd2H2p'
# 'https://discord.gg/AqVD73wX'
driver.get(link_to_server)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='button']")))

server_connect = driver.find_element_by_css_selector("button[type='button']")
server_connect.click()
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.childWrapper-anI2G9")))

# Scraping members
sent = []
real_names = []

# completed = True
while True:
    members = driver.find_elements_by_css_selector('div.nameAndDecorators-5FJ2dg')
    for i in members:
        # Name
        try:
            name = i.text
        except StaleElementReferenceException:
            break

        # Test if user has been messaged
        if (name not in sent) and (name.find('BOT')==-1):
            # FInd the real name
            i.click()
            time.sleep(6)

            try:
                real_name = driver.find_element_by_css_selector('div.headerText-1vVs-U > div.nameTag-m8r81H').text
                real_names.append(real_name)
                sent.append(name)
            except NoSuchElementException as e:
                pass
    else:
        break
       
print(real_names)
