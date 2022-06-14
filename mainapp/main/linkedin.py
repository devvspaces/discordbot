from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from imap import find_linkedin_otp

connects = [
    {
        'link': 'https://www.linkedin.com/in/michelle-chen-ba111b17b/',
        'note': 'Hi, i would love to work with you on your fiverr work. Lols this is Israel nice to meet you again. How is the strava api website i built and hosted for you.'
    }
]

class Driver:
    def __init__(self):
        # chrome_options = webdriver.ChromeOptions()

        # Other driver settings
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # chrome_options.add_experimental_option("prefs", prefs)
        # chrome_options.add_argument("--disable-infobars")
        # chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_argument('--disable-gpu')

        # chrome_options.add_argument("--headless")
        # driver = webdriver.Chrome("chromedriver.exe", options=chrome_options)
        driver = webdriver.Chrome("chromedriver.exe")

        self.driver = driver
        self.base_login = 'https://www.linkedin.com/login'
        
        print('Created driver now')


    def login_linkedin(self, email, password_text, imap_pass):

        try:
            self.driver.get(self.base_login)

            ### get username and password input boxes path
            username = self.driver.find_element(by=By.XPATH, value='//*[@id="username"]')
            password = self.driver.find_element(by=By.XPATH, value='//*[@id="password"]')

            ### input the email id and password
            username.send_keys(email)
            password.send_keys(password_text)

            ### click the login button
            login_btn = self.driver.find_element(by=By.XPATH, value="/html/body/div/main/div[2]/div[1]/form/div[3]/button")

            sleep(1)
            login_btn.click()

            if self.driver.current_url.startswith('https://www.linkedin.com/feed/'):
                print('\n\nSuccessful Login\n\n')
                return
            
            if self.driver.current_url.startswith('https://www.linkedin.com/checkpoint/challenge/'):
                # Get email otp
                sleep(10)
                otp = find_linkedin_otp(email, imap_pass)
                print('\n\n', otp, '\n\n')
                
                opt_field = self.driver.find_element(by=By.XPATH, value='//*[@id="input__email_verification_pin"]')
                opt_field.send_keys(otp)

                ### click the submit button
                sumbit_btn = self.driver.find_element(by=By.XPATH, value='//*[@id="email-pin-submit-button"]')
                sleep(1)
                sumbit_btn.click()

        except (WebDriverException, TimeoutError, Exception) as e:
            print(e)


    def connect_linkedins(self):
        for connect in connects:
            try:
                self.driver.get(connect['link'])

                ### click the more button
                more_btn_path = '/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[3]/div/div[2]/button'
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, more_btn_path)))
                more_btn = self.driver.find_element(by=By.XPATH, value=more_btn_path)
                more_btn.click()

                print('Got to the first one')

                # element = self.driver.find_element_by_xpath('//*[@id="ember36"]/div[2]/div[2]/div[1]/div[1]/h1')
                # self.driver.execute_script("return arguments[0].scrollIntoView(true);", element)

                # print('Scrolled up')
                # sleep(5)
                
                # Click connect btn
                connect_path = '/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[3]/div/div[2]/div/div/ul/li[5]/div'
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, connect_path)))
                connect_btn = self.driver.find_element(by=By.XPATH, value=connect_path)
                connect_btn.click()

                print('Got to the first 2')


                addnote_path = '/html/body/div[3]/div/div/div[3]/button[1]'
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, addnote_path)))
                addnote_btn = self.driver.find_element(by=By.XPATH, value=addnote_path)
                addnote_btn.click()

                print('Got to the first 3')

                # Write message
                note_path = '/html/body/div[3]/div/div/div[2]/div/textarea'
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, note_path)))
                note_field = self.driver.find_element(by=By.XPATH, value=note_path)
                note_field.send_keys(connect['note'])
                sleep(5)

                print('Got to the first 4')

                sendnote_path = '/html/body/div[3]/div/div/div[3]/button[2]'
                sendnote_btn = self.driver.find_element(by=By.XPATH, value=sendnote_path)
                sleep(10)
                sendnote_btn.click()

                print('Got to the first 5')

            except (WebDriverException, TimeoutError, Exception) as e:
                print(e)
        
        print('DONE DONE DONE DONE DONE DONE DONE DONE DONE DONE ')
        print('AUTOMATION IS LIFE.')

    def quit(self):
        try:
            self.driver.quit()
            del self.driver

            print('Deleted the driver')
        except Exception as e:
            print(e)

    def __del__(self):
        self.quit()
        del self


site = Driver()
password = 'emodnhhjeomhybyz'
email = 'bossdollyp@gmail.com'
linked_in_pass = 'alakio12345'
site.login_linkedin(email, linked_in_pass, password)
site.connect_linkedins()
sleep(3600)
