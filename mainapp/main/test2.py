import os, sys, ctypes, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

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

# # Find total members and online members
# both = driver.find_elements_by_class_name('pillMessage-1btqlx')
# for i in both:
#     print(i.text)
# print('\n')

# Find button and click
server_connect = driver.find_element_by_css_selector("button[type='button']")
server_connect.click()
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.childWrapper-anI2G9")))

# Scraping members
sent = []
real_names = []

completed = True
while completed:
members = driver.find_elements_by_css_selector('div.nameAndDecorators-5FJ2dg')
for i in members:
    # Name
    name = i.text

    # Test if user has been messaged
    # if (name not in sent) or (name.find('bot')==-1):
    if name.find('bot')==-1:
        # FInd the real name
        i.click()
        time.sleep(6)

        try:
            real_name = driver.find_element_by_css_selector('div.headerText-1vVs-U > div.nameTag-m8r81H').text
            real_names.append(real_name)
        except NoSuchElementException as e:
            print(e)
            pass
        
        # try:
        #     real_name = driver.find_element_by_css_selector('div.headerText-1vVs-U > div.nameTag-m8r81H').text

        #     # Find message box
        #     inputElement = driver.find_element_by_css_selector('div.layer-v9HyYc > div.footer-3UKYOU > div > input')

        #     inputElement.send_keys('Have a nice day')
        #     inputElement.send_keys(Keys.ENTER)
        #     time.sleep(6)

        #     # Add user to the sent list
        #     sent.append(name)
        #     print('Message sent to ' + real_name)

        #     driver.back()
        #     break
        # except NoSuchElementException:
        #     # Add user to the sent list
        #     sent.append(name)
# else:
#     break
#     completed = True
    
    # if len(sent) == count:
    #     break

print(real_names)

# print(f'Sent {len(sent)} messages to discord members')