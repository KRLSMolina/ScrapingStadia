# Import packages
from selenium import webdriver
from backports import configparser
import time

# Variables
url_for_login = 'https://stackoverflow.com/users/signup?ssrc=head&returnurl=%2fusers%2fstory%2fcurrent%27'
url_stadia_store = 'https://stadia.google.com/store/list/3'

# Get credentials to login
config = configparser.RawConfigParser()
config.read('config.properties')

mail_address = config.get('Google Account', 'google_user')
password = config.get('Google Account', 'google_pass')

# WebDriver Initialization. Stadia only works with Chrome
driver = webdriver.Chrome('drivers/chromedriver.exe')

# Login through a website that allows you to log in with Google data
driver.get(url_for_login)
driver.find_element_by_xpath('//*[@id="openid-buttons"]/button[1]').click()

driver.find_element_by_xpath('//input[@type="email"]').send_keys(mail_address)
driver.find_element_by_xpath('//*[@id="identifierNext"]').click()
time.sleep(5)
driver.find_element_by_xpath('//input[@type="password"]').send_keys(password)
driver.find_element_by_xpath('//*[@id="passwordNext"]').click()
time.sleep(3)

# Open Stadia Store
driver.get(url_stadia_store)
driver.maximize_window()
time.sleep(3)

# SCRAPER
games_info = ['title','price','type_game']

items = driver.find_elements_by_class_name('h6J22d.QAAyWd')
print('Tenim {} elements per extreure la informació.'.format(len(items)))

for item in items:
    title = item.find_element_by_class_name('T2oslb.zHGix').text
    price = item.find_element_by_class_name('eoQBOd').text
    typee = item.find_element_by_class_name('vaa0f.eoQBOd').text
    new = ((title,price,typee))
    games_info.append(new)

print(games_info)

# Close browser
driver.quit()