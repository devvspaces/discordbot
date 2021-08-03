from mainapp.models import DiscordServer, Member
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from account.models import DiscordAccount

class Driver:
    def __init__(self):
        print('Created driver now')
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)

        # chromeOptions.add_argument("--headless")
        driver = webdriver.Chrome("C:/Users/HP6460B/discordauto/mainapp/main/chromedriver.exe", options=chrome_options)

        self.driver = driver

        self.working = False

        self.is_authenticated = False
    
    def login_account(self):
        account = DiscordAccount.objects.most_unused()
        try:
            if account:
                self.driver.get('https://discord.com/login')
                js = 'function login(token) {setInterval(() => {document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `"${token}"`}, 50);setTimeout(() => {location.reload();}, 500);}'
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='button']")))

                # Login discord
                self.driver.execute_script(js + f'login("{account.token}")')

                account.use_count = account.use_count + 1
                account.save()

                return True
        except (WebDriverException, TimeoutError) as e:
            print('Got an exception')
            print(e)

        # Alert admins
        return False
    
    def parse_server_basic(self, discord_server):
        if self.working:
            return False

        try:
            self.working = True

            self.driver.get(discord_server.link)

            # Wait for the page to load
            # WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='button']")))

            server_icon = self.find_webelement(wait_time = 1, count = 10, find_function=self.driver.find_element_by_css_selector, selector="div.icon-3o6xvg")

            # If the server name contains invalid, this means the server link is invalid
            if server_icon is None:
                return f'The discord server invite may be expired, invalid, or we do not have permission to join.'

            server_name = self.driver.find_element_by_css_selector("h3.title-jXR8lp").text
            members = int(self.driver.find_elements_by_class_name('pillMessage-1btqlx')[1].text.split(' ')[0].replace(',', ''))
            server_icon = server_icon.value_of_css_property("background-image").split('"')[1]

            # Check if the server already exists
            if discord_server.user.discordserver_set.filter(name__exact=server_name).exists():
                return 'Server has already been added'

            # Save data in to discord_server
            discord_server.name = server_name
            discord_server.members = members
            discord_server.icon = server_icon
            discord_server.save()

            self.working = False
        except Exception as e:
            e
            print(e)
            return

        return True


    def parse_users(self, discord_server):
        if self.working:
            return False

        # try:
        self.working = True

        if not self.is_authenticated:
            response = self.login_account()
            if not response:
                return
        
        self.driver.get(discord_server.link)
        # WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='button']")))

        # Find button and click
        server_connect = self.find_webelement(wait_time = 1, count = 20, find_function=self.driver.find_element_by_css_selector, selector="button[type='button']")
        # server_connect = self.driver.find_element_by_css_selector("button[type='button']")

        # If the server_connect button was never found, this means the server link is invalid
        if server_connect is None:
            return f'The discord server invite may be expired, invalid, or we do not have permission to join. DISCORD SERVER INVITE LINK ({discord_server.link})'

        server_connect.click()
        # WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.childWrapper-anI2G9")))

        # Scraping members
        sent = []
        real_names = []
        
        members = self.find_webelement(wait_time = 10, count = 100, find_function=self.driver.find_elements_by_css_selector, selector='div.member-3-YXUe', is_list=True)
        # If no members where found
        if members is None:
            return

        completed = True
        while completed:

            if members is None:
                members = [i for i in self.driver.find_elements_by_css_selector('div.member-3-YXUe') if i.text.find('BOT')==-1]
                if len(members) <= len(sent):
                    break

            print('Scraped members', len(members))
            print('Scraped users', len(sent))

            for i in members:
                # Get the general username
                try:
                    name = i.find_element_by_css_selector('div.nameAndDecorators-5FJ2dg').text
                except StaleElementReferenceException:
                    # If webelements session have expired, set members to none to rescrape
                    print('Stale ready')
                    members = None
                    break

                # Test if member real name has been successfully clicked and not a bot
                if name and (name not in sent) and (name.find('BOT')==-1):
                    # FInd the real name
                    try:
                        i.click()
                    except ElementClickInterceptedException:
                        print('Executed js')
                        self.driver.execute_script("arguments[0].click();", i)
                    
                    # Find the text element
                    real_name = self.find_webelement(wait_time=2, count=10, find_function=self.driver.find_element_by_css_selector, selector='div.headerText-1vVs-U > div.nameTag-m8r81H')
                    # time.sleep(2)
                    if real_name is not None:
                        real_names.append(real_name.text)
                        sent.append(name)
                    else:
                        pass
            else:
                # Find the members on the page again, if 
                members = None
        
        
        # Create members with the real names
        for i in real_names:
            Member.objects.get_or_create(username=i, discord_server=discord_server)

        # ***********Thread this it is not important to the current user**************
        # Find discord servers with the same name and update them too
        # similar_servers = DiscordServer.objects.filter(name=discord_server.name)
        # for a in similar_servers:
        #     for b in real_name:
        #         Member.objects.get_or_create(username=b, discord_server=a)

        self.working = False

        # except Exception as e:
        #     print(e)
        #     return

        return True

    def find_webelement(self, wait_time = 1, count=1, find_function=None, selector='', is_list=False):
        el = None
        if (find_function is not None) and selector:
            find_count = 0
            while find_count < count:
                try:
                    # Run the function passed with the selecting argument
                    time.sleep(wait_time)
                    el = find_function(selector)
                    print(f'Waited {wait_time}')
                    if is_list:
                        if len(el) == 0:
                            find_count += 1
                        else:
                            break
                    else:
                        break
                except NoSuchElementException:
                    print('Got here for', selector)
                    find_count += 1

        return el

    def send_dm(self):
        return

    def quit(self):
        self.driver.quit()

    def __del__(self):
        self.quit()
        del self
        