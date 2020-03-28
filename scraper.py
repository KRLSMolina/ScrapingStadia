import requests
import pandas as pd
from bs4 import BeautifulSoup

page = requests.get("https://store.google.com/es/product/stadia_games")

assert page.status_code == 200

soup = BeautifulSoup(page.content, 'html.parser')
soup.find_all(class_='mqn2-b9n')

game_names = soup.find_all(class_='mqn2-b9n')
list_games = [x.get_text() for x in game_names]
print(soup)