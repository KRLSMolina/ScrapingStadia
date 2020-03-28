import re

import requests
from bs4 import BeautifulSoup


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


if __name__ == '__main__':
    ss = StradaScrapper()
    ss.get_games_names()
    ss.list_games
