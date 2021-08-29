from paygate.models import Order
import time

# Required for channel communication
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
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
        chrome_options.add_argument('--disable-gpu')

        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome("C:/Users/HP6460B/discordauto/mainapp/main/chromedriver.exe", options=chrome_options)

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
        if invalid_title is not None:
            if invalid_title.text.lower() in [i.lower() for i in invalid_titles]:
                invalid = True
        
        return invalid


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
            
            print('Makeeeee')

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

    
    def stop_messaging(self, event, message, messages_left):
        # If event is set stop sending messages
        if event.isSet():
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
                    return self.end_message(message, 'Error connecting to discord server. Support teams have been alerted, try again later', mtype='completed_message')
            

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


            # Get the members on the discord page
            members = self.find_webelement(wait_time = 1, count = 40, find_function=self.driver.find_elements_by_css_selector, selector='div.member-3-YXUe', is_list=True)
            
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
            real_names = []
            created = []


            # Start the looping to send messages to any found users
            completed = True
            while completed:

                logger.debug('Started while loop')

                # Get the messages left for the user
                messages_left = Order.objects.filter(profile=message.profile).count_dm() - DirectMessage.objects.filter(profile=message.profile).count_sent()

                # Check to see if we are to stop messaging
                if self.stop_messaging(event, message, messages_left):
                    logger.debug('Loop was broken by stop_messaging')
                    break

                # Check to see if messages have been sent to all members or continue
                if members is None:
                    members = [i for i in self.driver.find_elements_by_css_selector('div.member-3-YXUe') if i.text.find('BOT')==-1]
                    if len(members) <= len(sent):
                        logger.debug('Members on page are less than members already sent to')
                        break

                logger.debug(f'Scraped members {len(members)}')
                logger.debug(f'Scraped users {len(sent)}')


                # Loop through all found members
                for i in members:
                    
                    # Making checks before trying to find users ====

                    # Check to see if we are to stop messaging
                    if self.stop_messaging(event, message, messages_left):
                        completed = False
                        logger.debug('For Loop was broken completely by stop_messaging')
                        break

                    # Checking ends =================================



                    # Getting the general username
                    try:
                        item = self.find_webelement(wait_time=1, count=20, find_function=i.find_element_by_css_selector, selector='div.nameAndDecorators-5FJ2dg')
                        if item:
                            name = item.text
                            logger.debug(f'Got a name --> {name}')
                        else:
                            continue
                    except StaleElementReferenceException:
                        # If webelements session have expired, set members to none to rescrape
                        logger.debug('Members became stale, restarting loop')
                        members = None
                        break
                    # End of getting general username ================

                    # Test if name is available, if user hasn't been processed before and if user is not a BOT
                    if name and (name not in sent) and (name.find('BOT')==-1):
                        # Click the member to send a message and get details
                        try:
                            i.click()
                        except ElementClickInterceptedException:
                            logger.debug('Had to use script')
                            self.driver.execute_script("arguments[0].click();", i)
                        
                        
                        # Find the text element ============
                        # layer = self.find_webelement(wait_time=1, count=20, find_function=self.driver.find_element_by_css_selector, selector='.layer-v9HyYc')
                        # logger.debug(f'\n\n{layer.get_attribute("innerHTML")}\n\n')
                        # return self.end_message(message, 'Broke it all for testing')

                        real_name = self.find_webelement(wait_time=1, count=20, find_function=self.driver.find_element_by_css_selector, selector='div.nameTag-m8r81H')
                        if real_name is not None:
                            name_data = real_name.text

                            logger.debug(f'Found a new name {name_data}')
                            
                            if name_data not in created:
                                # Save or get the new user as a member
                                user_mem, _ = Member.objects.get_or_create(username=name_data, discord_server=discord)
                                created.append(name_data)
                            
                                # Get user image
                                try:
                                    image = self.driver.find_element_by_css_selector('div.avatar-37jOim > svg > foreignObject > div > img')
                                    image = image.get_attribute("src")
                                    user_mem.image = image
                                except NoSuchElementException as e:
                                    pass
                                
                                # Get Roles
                                try:
                                    roles = self.driver.find_elements_by_css_selector('div.role-2irmRk > div.roleName-32vpEy')
                                    role_text = ', '.join([i.text for i in roles])
                                    user_mem.roles = role_text
                                except NoSuchElementException as e:
                                    pass
                                
                                user_mem.save()
                                logger.debug(f'Created or got a new name {name_data}')
                            

                            # Sending a message to this user ===========
                            
                            # Find message box
                            try:
                                inputElement = self.driver.find_element_by_css_selector('div.footer-3UKYOU > div > input')
                            except NoSuchElementException as e:
                                # If the input box wasn't found add the user to sent and continue
                                sent.append(name)
                                real_names.append(name_data)
                                continue


                            inputElement.send_keys(message_text)
                            inputElement.send_keys(Keys.ENTER)
                            

                            # Wait for the message to send ===========
                            messages = self.find_webelement(wait_time=1, count=20, find_function=self.driver.find_elements_by_css_selector, selector='.messageContent-2qWWxC', is_list=True)

                            if messages:
                                # Add user to the sent list
                                logger.debug('Message sent to ' + name_data)
                                sent.append(name)
                                real_names.append(name_data)
                                
                                # Update the message sent
                                message.sent = message.sent + 1
                                message.save()

                                # Send message through websocket to update user
                                send_channel_message(user_name, message='', mtype='message_update', count = 1)

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
                            else:
                                logger.debug('No messages was found here')

                            self.driver.back()
                            # End of sending message to user ==========


                else:
                    logger.debug('Finished a loop or members')
                    members = None
            
            logger.debug(f'Sent messages to {len(set(sent))} members and Created {len(set(created))} members')

            
            # Update message model and Send completed message to websocket that it is completed
            return self.end_message(message, 'Completed sending messages')

        except Exception as e:
            err_logger.exception(e)
            return self.end_message(message,'Completed sending messages')

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
        