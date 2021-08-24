import time, threading
import logging
# Create the logger and set the logging level
logger = logging.getLogger('basic')
err_logger = logging.getLogger('basic.error')

# Required for channel communication
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from django.conf import settings

from mainapp.models import DiscordServer, Member

from account.models import DiscordAccount, ProxyPort


def send_channel_message(group_name, message, mtype='', count=''):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'chat_{group_name}',
        {
            'type': 'channel_message',
            'message': message,
            'mtype': mtype,
            'count': count
        }
    )

class Driver:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()

        # Get the proxy to use
        self.proxy = None
        proxy = ProxyPort.objects.most_unused()
        if proxy:
            # chrome_options.add_argument(f'--proxy-server={proxy}')
            proxy.use_count = proxy.use_count + 1
            proxy.save()
            self.proxy = proxy
        
        # Other driver settings
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--disable-extensions")

        # chromeOptions.add_argument("--headless")
        driver = webdriver.Chrome("C:/Users/HP6460B/discordauto/mainapp/main/chromedriver.exe", options=chrome_options)

        self.driver = driver

        self.working = False

        self.is_authenticated = False

        self.account_id = None

        self.connected_to = None

        self.event = None
        
        logger.debug('Created driver now')

    def set_working_complete(self, event):
        for i in range(settings.BOT_CONNECTION_TIME * 60):
            time.sleep(i)
            if event.isSet():
                return

        self.connected_to = None
        self.working = False
        self.event = None

    def login_account(self):
        account = DiscordAccount.objects.most_unused()
        try:
            if account:
                logger.debug('Got an account')
                self.driver.get('https://discord.com/login')
                js = 'function login(token) {setInterval(() => {document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `"${token}"`}, 50);setTimeout(() => {location.reload();}, 500);}'
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='button']")))

                # Login discord
                self.driver.execute_script(js + f'login("{account.token}")')

                account.use_count = account.use_count + 1
                account.save()

                # Save the current logged in account id
                self.account_id = account.id

                return True
        except (WebDriverException, TimeoutError) as e:
            err_logger.exception(e)

        # Alert admins
        logger.debug('No account to use')
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

            # Check if the server already exists
            if discord_server.user.discordserver_set.filter(name__exact=server_name).exists():
                return 'Server has already been added'

            # Save data in to discord_server
            discord_server.name = server_name
            discord_server.members = members

            server_icon = server_icon.value_of_css_property("background-image").split('"')
            if len(server_icon) > 1:
                server_icon = server_icon[1]
                discord_server.icon = server_icon
                
            discord_server.save()

            self.working = False
        except Exception as e:
            e
            err_logger.exception(e)
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
                logger.debug('User could not login')
                self.working = False
                return
        
        self.driver.get(discord_server.link)

        invalid = False

        # First check if the invite is already expired
        invalid_title = self.find_webelement(wait_time = 1, count = 20, find_function=self.driver.find_element_by_css_selector, selector="h3.title-jXR8lp")
        if invalid_title is not None:
            if invalid_title.text.lower() == 'Invite invalid'.lower():
                invalid = True

        # Find button and click
        server_connect = self.find_webelement(wait_time = 1, count = 20, find_function=self.driver.find_element_by_css_selector, selector="button[type='button']")

        # If the server_connect button was never found, this means the server link is invalid
        if server_connect is None:
            invalid = True

        # If invalid is true return message
        if invalid:
            return f'The discord server invite may be expired, invalid, or we do not have permission to join. DISCORD SERVER INVITE LINK ({discord_server.link})'

        # Click to go to page
        server_connect.click()

        # Scraping members
        sent = []
        real_names = []
        created = []

        
        members = self.find_webelement(wait_time = 10, count = 2, find_function=self.driver.find_elements_by_css_selector, selector='div.member-3-YXUe', is_list=True)
        # If no members where found
        if (members is None) or (len(members) == 0):
            logger.debug('No members found')
            invalid_title = self.find_webelement(wait_time = 1, count = 5, find_function=self.driver.find_element_by_css_selector, selector="h3.title-jXR8lp")
            # Check if the discord account being used is expired
            if invalid_title.text.lower() == 'Unable to accept invite'.lower():
                logger.debug('Token has expired')
                if self.account_id:
                    account = DiscordAccount.objects.get(id=self.account_id)
                    account.expired_token = True
                    account.save()
                    logger.debug(f'Updated expired token, account_id: {self.account_id}')
                return 'Sorry we can not connect to any server right now, try again later'
            
            logger.debug('Returned none to view because no members was found')
            return None

        completed = True
        while completed:

            if members is None:
                # =======================
                break
                # =======================
                members = [i for i in self.driver.find_elements_by_css_selector('div.member-3-YXUe') if i.text.find('BOT')==-1]
                if len(members) <= len(sent):
                    break

            logger.debug(f'Scraped members {len(members)}')
            logger.debug(f'Scraped user {len(sent)}')

            for i in members:
                # Get the general username
                try:
                    item = self.find_webelement(wait_time=1, count=20, find_function=i.find_element_by_css_selector, selector='div.nameAndDecorators-5FJ2dg')
                    if item:
                        name = item.text
                    else:
                        continue
                except StaleElementReferenceException:
                    # If webelements session have expired, set members to none to rescrape
                    members = None
                    break

                # Test if member real name has been successfully clicked and not a bot
                if name and (name not in sent) and (name.find('BOT')==-1):
                    # FInd the real name
                    try:
                        i.click()
                    except ElementClickInterceptedException:
                        self.driver.execute_script("arguments[0].click();", i)
                    
                    # Find the text element
                    real_name = self.find_webelement(wait_time=1, count=20, find_function=self.driver.find_element_by_css_selector, selector='div.headerText-1vVs-U > div.nameTag-m8r81H')
                    # time.sleep(2)
                    if real_name is not None:
                        name_data = real_name.text
                        real_names.append(name_data)
                        sent.append(name)

                        logger.debug(f'Added a new name {name}')
                        
                        if name_data not in created:
                            # Save or get the name here
                            user_mem, c = Member.objects.get_or_create(username=name_data, discord_server=discord_server)
                            created.append(name_data)
                        
                            # Get image
                            image = self.find_webelement(wait_time=1, count=20, find_function=self.driver.find_element_by_css_selector, selector='div.avatar-37jOim > svg > foreignObject > div > img')
                            if image is not None:
                                image = image.get_attribute("src")
                                user_mem.image = image
                            
                            # Get Roles
                            roles = self.find_webelement(wait_time=1, count=20, find_function=self.driver.find_elements_by_css_selector, selector='div.role-2irmRk > div.roleName-32vpEy')
                            if roles is not None:
                                role_text = ', '.join([i.text for i in roles])
                                user_mem.roles = role_text
                            
                            user_mem.save()

                    else:
                        pass
            else:
                # Find the members on the page again, if 
                members = None
        
        logger.debug('Broke loop and got here')
        logger.debug(f'{real_names}, {sent}, {created}')
        
        
        # Create members with the real names
        # for i in real_names:
        #     Member.objects.get_or_create(username=i, discord_server=discord_server)

        # ***********Thread this it is not important to the current user**************
        # Find discord servers with the same name and update them too
        # similar_servers = DiscordServer.objects.filter(name=discord_server.name)
        # for a in similar_servers:
        #     for b in real_name:
        #         Member.objects.get_or_create(username=b, discord_server=a)

        # Make this connected to the user id for specified time
        self.connected_to = discord_server.user.id

        # Create event to automatically kill the thread
        e1 = threading.Event()
        self.event = e1

        t1 = threading.Thread(target=self.set_working_complete, args=(e1, ))
        t1.start()

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
                    # logger.debug(f'Waited {wait_time}')
                    if is_list:
                        if len(el) == 0:
                            find_count += 1
                        else:
                            break
                    else:
                        break
                except NoSuchElementException:
                    # logger.debug('Got here for', selector)
                    find_count += 1

        return el
    
   
    def send_dm_user(self, username):
        # Login to not logged in

        # User CTRL + K to find user and send them a message

        # Return True if completed successfully else false
        
        return True

    def send_message(self, message, event, messages_left):
        # Set the messaging event
        if self.event:
            self.event.set()

        # Get the users, blacklists and discord_server link
        discord = message.server
        blacklist = message.blacklist
        user_name = message.profile.discord_username
        sent = message.sent
        stop = message.message_stop

        if discord is None:
            # Send message through web socket
            send_channel_message(user_name, message='Discord Server Error')
            return

        discord_members = [i.username for i in  discord.member_set.all()]
        screened = discord_members.copy()
        if blacklist is not None:
            usernames = [i.username for i in blacklist.blacklist_set.all()]
            screened = [i for i in discord_members if i not in usernames]

        for a,b in enumerate(screened):
            # If event is set stop sending messages
            if event.isSet():
                break

            # Stop sending messages
            if stop > 0:
                if a > (stop - 1):
                    break
            
            # Check if user has any available messages
            if messages_left <= 0:
                time.sleep(3)
                send_channel_message(user_name, message='Completed sending messages', mtype='completed_message')
                return

            # Send a message
            val = self.send_dm_user(b)
            if val:
                sent += 1
                message.sent = sent
                message.save()

                # Sent message through websocket to update user if online
                send_channel_message(user_name, message='', mtype='message_update', count = 1)

                # If blacklist users option is selected
                if message.blacklist_users:
                    # Delete user from server members and add to selected blacklist
                    member = discord.member_set.get(username=b)
                    member.delete()
                    blacklist.blacklist_set.create(username=member.username)

                # Wait for the time delay
                delay = message.delay
                # time.sleep(delay)
                time.sleep(1)
        
        logger.debug('Finished that, Got here')
        
        # Update message model and Send completed message to websocket that it is completed
        message.completed = True
        message.save()
        time.sleep(3)
        send_channel_message(user_name, message='Completed sending messages', mtype='completed_message')

        self.connected_to = None
        self.working = False
        self.event = None

        return

    def quit(self):
        logger.debug('Deleted the driver')
        self.driver.quit()
        del self.driver

        # Reduce the account use if driver is logged in to an account
        if self.is_authenticated:
            # Get the account
            account = DiscordAccount.objects.get(id=self.account_id)
            account.use_count = account.use_count-1
            account.save()
        
        if self.proxy:
            self.proxy.use_count = self.proxy.use_count-1
            self.proxy.save()

    def __del__(self):
        self.quit()
        del self
        