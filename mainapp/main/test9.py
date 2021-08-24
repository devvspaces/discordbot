from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
 
# The place we will direct our WebDriver to
url = 'http://www.srcmake.com/'

# Creating the WebDriver object using the ChromeDriver
driver = webdriver.Chrome('/usr/bin/chromedriver', options=chrome_options)

# Directing the driver to the defined url
driver.get(url)

print(driver.title)