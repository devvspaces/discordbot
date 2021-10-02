from paygate.models import Order
import time

# Required for channel communication
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

import logging

# Create the logger and set the logging level
logger = logging.getLogger('basic')
err_logger = logging.getLogger('basic.error')

from django.conf import settings

from mainapp.models import DirectMessage, Member

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
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_argument('--disable-gpu')

        # chrome_options.add_argument("--headless")
        driver = webdriver.Chrome("C:/Users/User/discordbot/mainapp/main/chromedriver.exe", options=chrome_options)

        self.driver = driver

        self.working = False

        self.is_authenticated = False

        self.account_id = None

        self.connected_to = None

        self.event = None
        
        logger.debug('Created driver now')


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
        logger.debug('No account to use, user can\'t login')
        return False


    def update_discord_server(self, server, name, members, icon):
        # Save data in to discord_server
        server.name = name
        server.members = members

        icon = icon.value_of_css_property("background-image").split('"')
        if len(icon) > 1:
            icon = icon[1]
            server.icon = icon
            
        server.save()


    def check_invite(self):
        # To check if the invite is expired
        invalid = False

        # Invalid titles
        invalid_titles = ['Unable to accept invite', 'Invite invalid']

        # First check if the invite is already expired
        invalid_title = self.find_webelement(wait_time = 1, count = 20, find_function=self.driver.find_element_by_css_selector, selector="h3.title-jXR8lp")
        
        try:
            if invalid_title is not None:
                if invalid_title.text.lower() in [i.lower() for i in invalid_titles]:
                    invalid = True
        except StaleElementReferenceException:
            return self.check_invite()
        
        return invalid


    def check_app_redirect(self):
        # To check if the invite is expired
        check = False

        logger.debug('Got here')

        # Invalid titles
        invalid_titles = ['Discord App Launched']

        # First check if the invite is already expired
        invalid_title = self.find_webelement(wait_time = 1, count = 5, find_function=self.driver.find_element_by_css_selector, selector="h3.title-jXR8lp")
        
        try:
            if invalid_title is not None:
                logger.debug(f'Checked for redirect: {invalid_title.text.lower()}')
                if invalid_title.text.lower() in [i.lower() for i in invalid_titles]:
                    check = True
        except StaleElementReferenceException:
            logger.debug('Went stale while checking for redirect')
            return self.check_app_redirect()
        
        return check


    def get_server_detail_els(self):
        server_icon = self.find_webelement(wait_time = 1, count = 10, find_function=self.driver.find_element_by_css_selector, selector="div.icon-3o6xvg")
        server_name = self.driver.find_element_by_css_selector("h3.title-jXR8lp").text
        online_members, members = [int(i.text.split(' ')[0].replace(',', '')) for i in self.driver.find_elements_by_class_name('pillMessage-1btqlx')]

        return server_icon, server_name, members, online_members


    def get_server_details(self, discord_server):
        try:
            self.working = True

            # Visit the invite link
            self.driver.get(discord_server.link)

            # Check if the invite is still valid
            if self.check_invite():
                self.working = False
                return f'The discord server invite may be expired, invalid, or we do not have permission to join.'

            server_icon, server_name, members, online_members = self.get_server_detail_els()

            logger.debug(f'Got number of online users from {server_name} which is {online_members}')

            # Save data in to discord_server
            self.update_discord_server(discord_server, server_name, members, server_icon)

            # Validate the online_members
            if online_members <= 0:
                return 'There are currently no online members on this server'

            self.working = False
        except Exception as e:
            self.working = False
            err_logger.exception(e)
            return

        return online_members


    def parse_server_basic(self, discord_server):
        try:
            self.working = True

            self.driver.get(discord_server.link)

            # If the server name contains invalid, this means the server link is invalid
            if self.check_invite():
                self.working = False
                return f'The discord server invite may be expired, invalid, or we do not have permission to join.'
            
            server_icon, server_name, members, _ = self.get_server_detail_els()

            # Check if the server already exists
            if discord_server.user.discordserver_set.filter(name__exact=server_name).exists():
                self.working = False
                return 'Server has already been added'

            # Save data in to discord_server
            self.update_discord_server(discord_server, server_name, members, server_icon)

            self.working = False
        except Exception as e:
            self.working = False
            err_logger.exception(e)
            return

        return True
    

    def find_webelement(self, wait_time = 1, count=1, find_function=None, selector='', is_list=False):
        el = None
        if (find_function is not None) and selector:
            find_count = 0
            while find_count < count:

                try:
                    # Run the function passed with the selecting argument
                    el = find_function(selector)
                    
                    # Check if a list was expected
                    if is_list:
                        if len(el) == 0:
                            find_count += 1

                            # Wait for the time
                            time.sleep(wait_time)
                            logger.debug(f'Waited {wait_time}')
                        else:
                            break

                    else:
                        break

                except NoSuchElementException:
                    logger.debug(f'NoSuchElementException for: {selector}')
                    find_count += 1

                    # Wait for the time
                    time.sleep(wait_time)
                    logger.debug(f'Waited {wait_time}')

                # except StaleElementReferenceException:
                #     logger.debug('Elements went stale here')
                    
                #     self.driver.refresh()

                #     wait = WebDriverWait(self.driver, 200)
                #     wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".ready-36e6Vk"))) 

        return el
    

    def end_message(self, instance, message_text):
        try:

            # Set the message to completed
            instance.completed = True
            instance.save()

            logger.debug(f'A message is set to completed: Message text: {message_text}')
            send_channel_message(instance.profile.discord_username, message=message_text, mtype='completed_message')
            self.working = False

        except Exception as e:
            err_logger.exception(e)

    
    def stop_messaging(self, message, messages_left):
        # If event is set stop sending messages
        if message.isSet():
            logger.debug('Stop message event was set')
            return True
            
        # Stop sending messages
        stop = message.message_stop
        if stop > 0:
            if message.sent >= stop:
                logger.debug('Message sent has passed/reached the stop count')
                return True
        
        # Check if user has any available messages
        if messages_left <= 0:
            logger.debug('Message stopped because user has no more messages left')
            return True


    def get_members(self):
        return self.find_webelement(wait_time = 1, count = 40, find_function=self.driver.find_elements_by_css_selector, selector='div.member-3-YXUe', is_list=True)


    def get_members_names(self, members=None, count=0):
        logger.debug(f'Counted {count}')
        if count < 15:
            try:
                if not members:
                    members = self.get_members()
                return [i.text for i in members if i.text.find('BOT')==-1]
            except StaleElementReferenceException:
                count += 1
                logger.debug('Members went stale during processing')
                return self.get_members_names(count=count)
        else:
            logger.debug(f'Could not get any member at all')
            raise StaleElementReferenceException


    def close_element_modal(self, class_names=None, id_names=None):

        # If argument is none create a list
        if class_names is None:
            class_names = []

        # If argument is none create a list
        if id_names is None:
            id_names = []

        if class_names:
            # Loop through class names and try to click the element to remove it
            for i in class_names:
                try:
                    el = self.driver.find_element_by_css_selector(i)
                    self.driver.execute_script("arguments[0].click();", el)
                except NoSuchElementException:
                    pass

        elif id_names:
            pass

        return


    def send_message(self, message, event):
        self.working = True

        # Get the users, blacklists and discord_server link
        discord = message.server
        blacklist = message.blacklist
        user_name = message.profile.discord_username
        sent = message.sent
        stop = message.message_stop
        message_text = message.message
        # =================================================

        try:
            # Check if a discord server is connected to the message
            if discord is None:
                return self.end_message(message, 'Error processing message')


            # Login to a discord account
            if not self.is_authenticated:
                response = self.login_account()
                if not response:
                    return self.end_message(message, 'Error connecting to discord server. Support teams have been alerted, try again later')
            

            # Go to the discord link
            self.driver.get(discord.link)


            # To check if the invite is expired
            invalid = self.check_invite()

            if invalid == False:
                # Find button and click
                server_connect = self.find_webelement(wait_time = 1, count = 20, find_function=self.driver.find_element_by_css_selector, selector="button[type='button']")

                # If the server_connect button was never found, this means the server link is invalid
                if server_connect is None:
                    invalid = True

            # If invalid is true return message
            if invalid:
                return self.end_message(message, f'The discord server invite may be expired, invalid, or we do not have permission to join. Discor server: {discord.link}')


            # Click to go to discord server page
            server_connect.click()

            # if there is another occurence where by discord tries to redirect to app
            if self.check_app_redirect():
                server_connect = self.find_webelement(wait_time = 1, count = 1, find_function=self.driver.find_element_by_css_selector, selector="button[type='button']")
                if server_connect:
                    server_connect.click()


            # Get the members on the discord page
            members = self.get_members()
            
            # If no members where found
            if (members is None) or (len(members) == 0):
                logger.debug('No members found')
                
                # Check if the discord account being used is expired
                if self.check_invite():
                    logger.debug('Token has expired')
                    if self.account_id:
                        account = DiscordAccount.objects.get(id=self.account_id)
                        account.expired_token = True
                        account.save()
                        logger.debug(f'Updated expired token, account_id: {self.account_id}')

                    return self.end_message(message,'Sorry we can not connect to any server right now, try again later')

                return self.end_message(message,'Returned none to view because no members was found')
            

            # Set the containers to store names found and names of users that have received messages
            sent = []
            usernames = []
            real_names = []
            created = []

            server_rel_link = self.driver.current_url

            logger.debug(f'Discord server real link is {server_rel_link}')

            # Set page scrolling counter and count
            scroll_by = 5000
            scroll_count = 1

            # Start the looping to send messages to any found users
            completed = True
            while completed:

                logger.debug('Started while loop')

                message.refresh_from_db()

                # Get the messages left for the user
                messages_left = Order.objects.filter(profile=message.profile).count_dm() - DirectMessage.objects.filter(profile=message.profile).count_sent()

                # Check to see if we are to stop messaging
                if self.stop_messaging(message, messages_left):
                    logger.debug('Loop was broken by stop_messaging')
                    break

                # Get the names found
                usernames += self.get_members_names(members=members)
                usernames = list(set(usernames))
                members = None

                # Get the names that hasn't been sent messages
                unique = set(sent).symmetric_difference(set(usernames))

                logger.debug(f'Usernames {len(usernames)}')
                logger.debug(f'Sent {len(sent)}')
                logger.debug(f'Unique names {len(unique)}')


                if len(unique) == 0:
                    completed = False
                else:
                    # Loop through all unique names
                    for username in unique:

                        message.refresh_from_db()
                        
                        # Check to see if we are to stop messaging
                        if self.stop_messaging(message, messages_left):
                            completed = False
                            logger.debug('For Loop was broken completely by stop_messaging')
                            break
                        # Checking ends =================================


                        # Find the user with quick search
                        # create action chain object
                        action = ActionChains(self.driver)
                         
                        # perform the operation
                        action.key_down(Keys.CONTROL).send_keys('k').key_up(Keys.CONTROL).perform()

                        try:
                            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.quickswitcher-3JagVE > input.input-2VB9rf")))

                            inputx = self.driver.find_element_by_css_selector("div.quickswitcher-3JagVE > input.input-2VB9rf")
                            inputx.send_keys(username)
                            inputx.send_keys(Keys.ENTER)

                            wait = WebDriverWait(self.driver, 10)
                            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".cursorPointer-1j7DL8"))) 

                            # Sending messages
                            inputx = self.driver.find_element_by_css_selector("div.textArea-12jD-V.textAreaSlate-1ZzRVj.slateContainer-3Qkn2x > div.markup-2BOw-j.slateTextArea-1Mkdgw.fontSize16Padding-3Wk7zP > div")
                            
                            try:
                                inputx.click()
                            except ElementClickInterceptedException as e:
                                err_logger.exception(e)
                                
                                # Try to close some possible interacting elements
                                self.close_element_modal(class_names=['.backdrop-1wrmKB'])

                                # Try click input again
                                logger.debug('Trying to click input element again')
                                inputx.click()

                            inputx.send_keys(message_text + Keys.ENTER)

                            # Add user to the sent list
                            logger.debug('Message sent to ' + username)
                            sent.append(username)
                            
                            # Update the message sent
                            message.sent = message.sent + 1
                            message.save()

                            # Send message through websocket to update user
                            send_channel_message(user_name, message='', mtype='message_update', count = 1)

                            # Getting the real name
                            btn_cursor = self.driver.find_element_by_css_selector('.cursorPointer-1j7DL8')
                            btn_cursor.click()

                            wait = WebDriverWait(self.driver, 1)
                            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".nameTag-m8r81H")))

                            # Get the real user identifier and save
                            name_code = self.driver.find_element_by_css_selector('.nameTag-m8r81H').text
                            name_data = real_name.text
                            
                            # Create new name
                            if name_data not in created:
                                # Save or get the new user as a member
                                user_mem, _ = Member.objects.get_or_create(username=name_data, discord_server=discord)
                                created.append(name_data)
                            
                                # Get user image
                                try:
                                    image = self.driver.find_element_by_css_selector('.avatarStack-2Dr8S9 img')
                                    image = image.get_attribute("src")
                                    user_mem.image = image
                                except NoSuchElementException as e:
                                    pass
                                
                                user_mem.save()
                                logger.debug(f'Created or got a new name {name_data}')
                            
                            # If blacklist users option is selected
                            if message.blacklist_users:
                                # Delete user from server members and add to selected blacklist
                                member = discord.member_set.get(username = name_data)
                                member.delete()
                                blacklist.blacklist_set.create(username=member.username)


                            # Wait for the time delay
                            delay = message.delay
                            # **********Remove this when in production 3@3
                            delay = 1
                            # ****************************************
                            time.sleep(delay)

                        except TimeoutException as e:
                            logger.info('Timeout exception gotten')
                            err_logger.exception(e)
                            continue
                    
                    # Visit main page and scroll down
                    self.driver.get(server_rel_link)

                    try:
                        # Wait for page to load
                        wait = WebDriverWait(self.driver, 200)
                        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".ready-36e6Vk"))) 

                        # Get members
                        members = self.get_members()
                        
                        self.driver.execute_script(f"document.querySelector('.members-1998pB.thin-1ybCId.scrollerBase-289Jih').scrollTop = {scroll_by * scroll_count}") 
                        scroll_count += 1
                    except TimeoutException as e:
                        logger.info('Timeout exception gotten')
                        err_logger.exception(e)


            logger.debug(f'Sent messages to {len(sent)} members')
            
            # Update message model and Send completed message to websocket that it is completed
            return self.end_message(message, 'Completed sending messages')

        except Exception as e:
            err_logger.exception(e)
            return self.end_message(message,'Stopped sending messages')

        return True


    def quit(self):
        try:
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
            
            logger.debug('Deleted the driver')
        except Exception as e:
            print(e)

    def __del__(self):
        self.quit()
        del self
        