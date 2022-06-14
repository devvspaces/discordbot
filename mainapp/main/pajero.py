from time import sleep
import pandas as pd

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

import re
import requests

connects = [
    {
        'link': 'https://www.linkedin.com/in/michelle-chen-ba111b17b/',
        'note': 'Hi, i would love to work with you on your fiverr work. Lols this is Israel nice to meet you again. How is the strava api website i built and hosted for you.'
    }
]

class Driver:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        
        driver = webdriver.Chrome("chromedriver.exe", chrome_options=chrome_options)
        

        self.driver = driver
        self.base_url = 'https://pagesjaunes.fr'

        self.hide()
        
        print('Created driver now')

    
    def hide(self):
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/2.0 (Windows NT 11.0; Win64; x32) AppleWebKit/555.36 (KHTML, like Wander) Chrome/81.0.4545.22 Safari/555.36'})
        # self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        # "source": """
        #     Object.defineProperty(navigator, 'webdriver', {
        #     get: () => undefined
        #     })
        # """
        # })
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print('\n\n', self.driver.execute_script("return navigator.userAgent;"))
    

    def get_search_queries(self)->list:
        # data = pd.read_excel(r"C:\Users\Dell\Downloads\métiers LBB.xlsx")
        # df = pd.DataFrame(data, columns= ['work'])

        # for column, frame in df.items():
        #     print(frame.loc[0, column])
        return ['secrétariat']
    
    def get_france_ciites(self)->list:
        return ['Paris']
    
    def scrape_email(self, original_url):
        emails = set()

        print(f"Crawling URL {original_url}")
        try:
            response = requests.get(original_url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            return

        new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com", response.text, re.I))
        emails.update(new_emails) 
        
        return emails


    def visit_site(self):

        # try:
        # self.hide()
        self.driver.get(self.base_url)

        WebDriverWait(self.driver, 3600).until(EC.presence_of_element_located((By.XPATH, '//*[@id="ou"]')))
        WebDriverWait(self.driver, 3600).until(EC.presence_of_element_located((By.XPATH, '//*[@id="quoiqui"]')))
        
        location = self.driver.find_element(by=By.XPATH, value='//*[@id="ou"]')
        work = self.driver.find_element(by=By.XPATH, value='//*[@id="quoiqui"]')

        search = self.get_search_queries()[0]
        city = self.get_france_ciites()[0]

        location.send_keys(city)
        
        work.send_keys(search)
        

        # Check for overlay :
        try:
            pop_up_btn = self.driver.find_element(by=By.XPATH, value='//*[@id="didomi-notice-agree-button"]')
            pop_up_btn.click()
            
        except Exception as e:
            pass

        search_btn = self.driver.find_element(by=By.XPATH, value='//*[@id="form_motor_pagesjaunes"]/div[1]/div[2]/div[2]/button')
        self.hide()
        search_btn.click()
        

        count = 1

        WebDriverWait(self.driver, 3600).until(EC.presence_of_element_located((By.XPATH, '//*[@id="tris-container"]/form/div')))


        # Get elements
        list_name = 'ul.bi-list li.bi.bi-generic .bi-clic-mobile .bi-with-visual .bi-content .bi-denomination.pj-lb.pj-link'
        elements = self.driver.find_element(by=By.CLASS_NAME, value=list_name)

        links = []

        for element in elements:
            links.append(element.get_attribute('href'))
        
        scraped_details = []
        
        for link in links[:count]:
            self.hide()
            self.driver.get(link)

            number_path = '//*[@id="teaser-footer"]/div/div/div[1]/a'
            WebDriverWait(self.driver, 3600).until(EC.presence_of_element_located((By.XPATH, number_path)))

            number_btn = self.driver.find_element(by=By.XPATH, value=number_path)
            number_btn.click()
            

            main_number_path = '//*[@id="teaser-footer"]/div/div/div[1]/div/span/span[2]'
            website_path = '//*[@id="teaser-footer"]/div/div/div[3]/a/span[2]/font/font'
            address_path = '//*[@id="teaser-footer"]/div/div/div[2]/a[1]'
            business_path = '//*[@id="teaser-header"]/div[1]/div[1]/div/div[1]/h1'

            number = self.driver.find_element(by=By.XPATH, value=main_number_path).text
            website = self.driver.find_element(by=By.XPATH, value=website_path).text
            address = self.driver.find_element(by=By.XPATH, value=address_path).text
            business = self.driver.find_element(by=By.XPATH, value=business_path).text

            emails = self.scrape_email(website)

            data = {
                'business': business,
                'number': number,
                'website': website,
                'address': address,
                'emails': emails,
            }

            scraped_details.append(data)
        
        print(scraped_details)


        # except (WebDriverException, TimeoutError, Exception) as e:
        #     print(e)

    def quit(self):
        sleep(3600)
        try:
            self.driver.quit()
            del self.driver

            print('Deleted the driver')
        except Exception as e:
            print(e)

    def __del__(self):
        sleep(3600)
        self.quit()
        del self


site = Driver()
site.visit_site()