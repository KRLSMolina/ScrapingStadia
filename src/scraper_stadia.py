# Import packages
from selenium import webdriver
from backports import configparser
import time
import pandas as pd
from difflib import SequenceMatcher
from sys import platform


def add_stadia_data(update_external=True):
    # Variables
    url_for_login = 'https://stackoverflow.com/users/signup?ssrc=head&returnurl=%2fusers%2fstory%2fcurrent%27'
    url_stadia_store = 'https://stadia.google.com/store/list/3'

    # Get credentials to login
    config = configparser.RawConfigParser()
    config.read('config.properties')

    username = config.get('Google Account', 'google_user')
    password = config.get('Google Account', 'google_pass')

    # WebDriver Initialization. Stadia only works with Chrome
    if platform == 'darwin':
        driver = webdriver.Chrome('drivers/chromedriver')
    elif platform == 'win32':
        driver = webdriver.Chrome('drivers/chromedriver.exe')

    # Login through a website that allows you to log in with Google data
    driver.get(url_for_login)
    driver.find_element_by_xpath('//*[@id="openid-buttons"]/button[1]').click()

    driver.find_element_by_xpath('//input[@type="email"]').send_keys(username)
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
    games_info = {'title': [], 'price': [], 'type_game': []}

    items = driver.find_elements_by_class_name('h6J22d.QAAyWd')
    print('Tenim {} elements per extreure la informació.'.format(len(items)))

    for item in items:
        title = item.find_element_by_class_name('T2oslb.zHGix').text
        price = item.find_element_by_class_name('eoQBOd').text
        typee = item.find_element_by_class_name('vaa0f.eoQBOd').text
        games_info['title'].append(title)
        games_info['price'].append(price)
        games_info['type_game'].append(typee)

    # Close browser
    driver.quit()

    # Update file with external data
    df = pd.DataFrame(games_info)
    if update_external:
        df = df[df['type_game'].isin(['Juego','Game','Joc'])]
        df['price'] = df['price'].apply(lambda x: x.split('\n')[0])
        df.loc[df['price'].isin(['Game', 'Juego', 'Joc', 'Claimed', 'Reclamat', 'Obtenido', 'Free', 'Gratis', 'Purchased', 'Comprado', 'S\'ha comprat']), 'price'] = 'Unknown'
        df_external = pd.read_csv('output_data/stadia_games_info.csv')

        if 'price_stadia' in df_external.columns:
            df_external.drop('price_stadia', axis=1, inplace=True)

        df_stadia_titles_match = pd.DataFrame(columns=['title', 'price_stadia'])

        for idx, row in df.iterrows():
            sim = 0
            tit_sim = ''
            for tit2 in df_external['title'].unique():
                new_score = SequenceMatcher(None, row['title'].lower(), tit2.lower()).ratio()
                if new_score > sim:
                    sim = new_score
                    tit_sim = tit2
            if sim >= .5:
                df_stadia_titles_match = df_stadia_titles_match.append(
                    pd.DataFrame({'title': [tit_sim], 'price_stadia': row['price']})
                )
            else:
                df_stadia_titles_match = df_stadia_titles_match.append(
                    pd.DataFrame({'title': [row['title']], 'price_stadia': [row['price']]})
                )
            df_external.merge(df_stadia_titles_match, on='title', how='outer').to_csv('output_data/stadia_games_info.csv',
                                                                                      index=False)
    else:
        df.to_csv('output_data/stadia_games_info.csv', index=False)
