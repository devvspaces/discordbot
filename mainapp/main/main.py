import os, sys, ctypes, time
from selenium import webdriver
# import Action chains
from selenium.webdriver.common.action_chains import ActionChains
 
# import KEYS
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC



# os.system('cls')
# token = input('Token: ')
# token = 'ODQyMTc4NTk2NDIwMDU5MTU4.YQnsJg._gL3vVLq7Wcve-sdcVS1-jxnuqE'
token = 'ODc2NDY1NjgzNzY3MTE1ODI2.YRke1Q.93Css-rpBZqZMLw7dqdEQcQ8MvI'
# ODc2NDY1NjgzNzY3MTE1ODI2.YRke1Q.93Css-rpBZqZMLw7dqdEQcQ8MvI
# ODQyMTc4NTk2NDIwMDU5MTU4.YQnsJg._gL3vVLq7Wcve-sdcVS1-jxnuqE
# ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

chrome_options = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
# chrome_options.add_experimental_option("prefs", prefs)

hostname, port = '168.80.195.202:3128'.split(':')

# chrome_options.add_argument('--proxy-server=%s' % hostname + ":" + port)

# chrome_options.add_argument("start-maximized")
# chrome_options.add_argument("disable-infobars")
# chrome_options.add_argument("--disable-extensions")
# chrome_options.add_argument('headless')

driver = webdriver.Chrome('chromet.exe', options=chrome_options)
# driver = webdriver.Chrome('chromedriver.exe')

driver.get('https://discord.com/login')
js = 'function login(token) {setInterval(() => {document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `"${token}"`}, 50);setTimeout(() => {location.reload();}, 500);}'
WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='button']")))

# Login discord
driver.execute_script(js + f'login("{token}")')

# Find server
link_to_server = 'https://discord.gg/hev7YSG5'
'''
https://discord.gg/W5qNWYPHrD
https://discord.gg/fuXKyYfa
https://discord.gg/znMzNR3x
https://discord.gg/8m4Y27nT
https://discord.gg/hsYyRSg9
https://discord.gg/hev7YSG5
'''
driver.get(link_to_server)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='button']")))

server_connect = driver.find_element_by_css_selector("button[type='button']")
server_connect.click()
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.childWrapper-anI2G9")))

# Scraping members
# sent = []
# real_names = []
# images = []
# roles = []

# # completed = True
# while len(sent) < 5:
#     members = driver.find_elements_by_css_selector('div.nameAndDecorators-5FJ2dg')
#     for i in members:
#         # Name
#         try:
#             name = i.text
#         except StaleElementReferenceException:
#             break

#         # Test if user has been messaged
#         if (name not in sent) and (name.find('BOT')==-1):
#             # FInd the real name
#             i.click()
#             time.sleep(6)

#             try:
#                 real_name = driver.find_element_by_css_selector('div.headerText-1vVs-U > div.nameTag-m8r81H').text
#                 real_names.append(real_name)
#                 sent.append(name)

#                 image = driver.find_element_by_css_selector('div.avatar-37jOim > svg > foreignObject > div > img').get_attribute("src")
#                 images.append(image)

#                 role = driver.find_elements_by_css_selector('div.role-2irmRk > div.roleName-32vpEy')
#                 roles.append([i.text for i in role])

#                 # div.avatar-37jOim > svg > foreignObject > div > img
#             except NoSuchElementException as e:
#                 pass
#     else:
#         break
       
# print(real_names)
# print(sent)
# print(images)
# print(roles)


# Send message to users
username = 'jodymcl#7835'

# create action chain object
action = ActionChains(driver)
 
# perform the operation
action.key_down(Keys.CONTROL).send_keys('k').key_up(Keys.CONTROL).perform()

WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.quickswitcher-3JagVE > input.input-2VB9rf")))

inputx = driver.find_element_by_css_selector("div.quickswitcher-3JagVE > input.input-2VB9rf")
inputx.send_keys(username)
inputx.send_keys(Keys.ENTER)

time.sleep(2)

# div.textArea-12jD-V > div
inputx = driver.find_element_by_css_selector("div.textArea-12jD-V.textAreaSlate-1ZzRVj.slateContainer-3Qkn2x > div.markup-2BOw-j.slateTextArea-1Mkdgw.fontSize16Padding-3Wk7zP > div")
inputx.click()
inputx.send_keys('What up' + Keys.ENTER)

# perform the operation
action.key_down(Keys.CONTROL).send_keys('k').key_up(Keys.CONTROL).perform()

WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.quickswitcher-3JagVE > input.input-2VB9rf")))

inputx = driver.find_element_by_css_selector("div.quickswitcher-3JagVE > input.input-2VB9rf")
inputx.send_keys('n3trob3#6154')
inputx.send_keys(Keys.ENTER)

time.sleep(2)

# div.textArea-12jD-V > div
inputx = driver.find_element_by_css_selector("div.textArea-12jD-V.textAreaSlate-1ZzRVj.slateContainer-3Qkn2x > div.markup-2BOw-j.slateTextArea-1Mkdgw.fontSize16Padding-3Wk7zP > div")
inputx.click()
inputx.send_keys('What up' + Keys.ENTER)