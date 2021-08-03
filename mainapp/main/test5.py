import threading
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

from collections import defaultdict
import weakref

threadLocal = threading.local()

class KeepRefs(object):
    __refs__ = defaultdict(list)
    def __init__(self):
        self.__refs__[self.__class__].append(weakref.ref(self))

    @classmethod
    def get_instances(cls):
        for inst_ref in cls.__refs__[cls]:
            inst = inst_ref()
            if inst is not None:
                yield inst


class Driver(KeepRefs):
    def __init__(self):
        super(Driver, self).__init__()

        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)

        # chromeOptions.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)

        self.driver = driver

    def get_title(self, url, s):
        time.sleep(s)

        # driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
        self.driver.get(url)
        
        print(id(self), url, self.driver.command_executor._url, self.driver.session_id, '\n')

    def quit(self):
    	self.driver.quit()

def count_drivers():
    return list(Driver.get_instances())

def get_driver():
    drivers = count_drivers()

    print('Got here', drivers)

    if len(drivers) == 0:
        driver = Driver()
        return driver

    return drivers[0]

def work(url, s):
    driver = get_driver()
    driver.get_title(url, s)
    # driver.quit()


links = [
'https://www.wikipedia.org/',
'https://www.google.com/',
'https://www.facebook.com/']
times = [0, 5, 8]
for a,b in zip(links, times):
    t1 = threading.Thread(target=work, args=(a, b,))
    t1.start()

time.sleep(20)