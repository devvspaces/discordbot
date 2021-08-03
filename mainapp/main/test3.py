import threading
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

# from collections import defaultdict
# import weakref

threadLocal = threading.local()

num = 0

g = getattr(threadLocal, 'g', None)


def get_driver():
  global threadLocal
  driver = getattr(threadLocal, 'driver', None)

  g = getattr(threadLocal, 'g', None)
  print(g, id(g))
  setattr(threadLocal, 'g', 2)

  global num

  if driver is None:
  # if True:
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    # chromeOptions.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    print('DId onece')
    setattr(threadLocal, 'driver', driver)

  print('Sent an instance', num, '\n\n')
  # return driver


def get_title(url, s):
  time.sleep(s)
  get_driver()
  driver = getattr(threadLocal, 'driver', None)
  global num
  num = num + 1 
  # driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
  driver.get(url)
  num = num -1
  print(id(driver), url, driver.command_executor._url, driver.session_id, '\n')

links = [
'https://www.wikipedia.org/',
'https://www.wikipedia.org/',
'https://www.wikipedia.org/']
times = [0, 0, 0]
for a,b in zip(links, times):
	t1 = threading.Thread(target=get_title, args=(a, b,))
	t1.start()
	# get_title(i)