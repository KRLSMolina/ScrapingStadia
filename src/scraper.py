import re
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class StradaScrapper:
    def get_games_names(self):
        print("Fent scraping dels noms dels videojocs disponibles a strada...")
        page = requests.get("https://store.google.com/es/product/stadia_games")
        assert page.status_code == 200

        soup = BeautifulSoup(page.content, 'html.parser')
        game_names = soup.find_all(class_='mqn2-b9n')

        raw_list_games = [x.get_text() for x in game_names]
        print("Scraping fet! {} videojocs identificats".format(len(raw_list_games)))
        list_games = []
        for game in raw_list_games:
            gm = "".join(re.findall('[^\\n][^\s]+', game))
            if gm[0] == ' ':
                gm = gm[1:]
            list_games.append(gm)
        self.list_games = list_games

    def get_all_games_metacritic_beautifulsoup(self, platform='ps4'):
        web = 'https://www.metacritic.com/browse/games/score/metascore/all/{}'.format(platform)

        page = requests.get(web)
        assert page.status_code == 200

        soup = BeautifulSoup(page.content, 'html.parser')
        games = soup.find_all(class_='basic_stat product_title')
        games


    def get_all_games_metacritic(self, platform='ps4'):
        driver = webdriver.Firefox()

        web = 'https://www.metacritic.com/browse/games/score/metascore/all/{}'.format(platform)

        driver.get(web)

        accept_coockies = WebDriverWait(driver, 200).until(
            EC.presence_of_element_located((By.ID, 'onetrust-accept-btn-handler')))
        accept_coockies.click()

        games_info = ['title', 'link', 'platform']
        page = 0

        total_pages = driver.find_element_by_class_name('last_page').text.split('\n')[1]

        while True:
            page += 1
            print("Important títols per a la pàgina {} de {} dels jocs de {}".format(page, total_pages, platform))

            # https://stackoverflow.com/questions/21713280/find-div-element-by-multiple-class-names
            elems = WebDriverWait(driver, 2000).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li[class*='product game_product']")))
                #EC.presence_of_all_elements_located((By.CLASS_NAME, "product_title")))

            # elems = driver.find_elements_by_class_name("product_title")
            for num, elem in enumerate(elems):
                subelem = elem.find_element_by_class_name('product_title')
                title = subelem.text
                print(page, title)
                link = subelem.find_element_by_css_selector('a').get_attribute('href')
                games_info.append([title, link, platform])
            # print("Importats {} títols".format(len(elems)))

            next_button = driver.find_element_by_class_name('next')

            if next_button.find_element_by_class_name('action').tag_name != 'a':
                break
            next_button.click()

        self.games_info = games_info
        driver.close()


if __name__ == '__main__':
    ss = StradaScrapper()
    # ss.get_games_names()
    ss.get_all_games_metacritic('ps4')
    ss.list_games
