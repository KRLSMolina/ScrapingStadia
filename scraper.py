import re
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import pandas as pd
import unidecode

from difflib import SequenceMatcher
import numpy as np


class StadiaScrapper:
    def get_games_names(self):
        print("Fent scraping dels noms dels videojocs disponibles a la web de stadia...")
        page = requests.get("https://store.google.com/es/product/stadia_games")
        assert page.status_code == 200

        soup = BeautifulSoup(page.content, 'html.parser')
        game_names = soup.find_all(class_='mqn2-b9n')

        raw_list_games = [x.get_text() for x in game_names]
        print("Scraping a la web de Stadia finalitzat! {} videojocs identificats".format(len(raw_list_games)))
        list_games = []
        for game in raw_list_games:
            gm = "".join(re.findall('[^\\n][^\s]+', game))
            if gm[0] == ' ':
                gm = gm[1:]
            list_games.append(gm)
        list_games = [unidecode.unidecode(x) for x in list_games]
        return list_games

    def get_all_games_metacritic_beautifulsoup(self, platform='ps4'):
        user_agent = {'User-agent': 'Mozilla/5.0'}
        games_info = {'title': [], 'link': [], 'platform': []}

        web = 'https://www.metacritic.com/browse/games/score/metascore/all/{}'.format(platform)
        response = requests.get(web, headers=user_agent)
        soup = BeautifulSoup(response.text, 'html.parser')
        max_page = int(soup.find(class_='page last_page').find(class_='page_num').get_text(strip=True))

        print("Fent scraping dels videojocs de {} a la web www.metactritic.com ...".format(platform))

        for i in range(max_page):
            if i > 0:
                end_line = "?page={}".format(i)
                web = 'https://www.metacritic.com/browse/games/score/metascore/all/{}{}'.format(platform, end_line)
                response = requests.get(web, headers=user_agent)
                soup = BeautifulSoup(response.text, 'html.parser')

            games_class = soup.findAll(class_=re.compile('product game_product*'))
            for game in games_class:
                sub_sel = game.find(class_='basic_stat product_title')
                games_info['title'].append(sub_sel.get_text(strip=True))
                games_info['link'].append('https://www.metacritic.com' + sub_sel.find('a', href=True)['href'])
                games_info['platform'].append(platform)

        df = pd.DataFrame(games_info)
        print('Scraping dels jocs de {} a la web www.metactritic.com finalitzat! {} videojocs identificats'.format(
            platform, df.shape[0]
        ))
        return df

    def get_similarities_df(self, games_stadia, all_games_platform, output_df=None):
        print('Fent match dels títols de {} entre Stadia i www.metacritics.com'.format(
            all_games_platform.iloc[0]['platform']))
        if output_df is None:
            output_df = pd.DataFrame()
        for game in games_stadia:
            score = 0
            for idx, row in all_games_platform.iterrows():
                word_1 = game.lower().replace(':', '')
                word_2 = row['title'].lower().replace(':', '')
                new_score = SequenceMatcher(None, word_1, word_2).ratio()
                if new_score > score:
                    idx_candidate = idx
                    score = new_score
            output_df = output_df.append(
                pd.DataFrame({'title': [game],
                              'title_metacritic': all_games_platform.loc[idx_candidate, 'title'],
                              'score': score,
                              'link': all_games_platform.loc[idx_candidate, 'link'],
                              'platform': all_games_platform.loc[idx_candidate, 'platform'], })
            )
        return output_df

    def get_games_info(self, df, min_score=1):
        print("...Obtenint informació per a cada joc i plataforma...")
        df_filtered = df[df['score'] >= min_score]
        user_agent = {'User-agent': 'Mozilla/5.0'}
        game_info_dict = {
            'idx': [],
            'release': [],
            'metascore': [],
            'n_reviews': [],
            'user_score': [],
            'n_user_score': [],
            'developer': [],
            'genere': [],
            'n_online_multiplayer': [],
        }
        for idx, row in df_filtered.iterrows():
            #print('{} - {}'.format(row['platform'], row['title']))
            web = row['link']
            response = requests.get(web, headers=user_agent)
            soup = BeautifulSoup(response.text, 'html.parser')

            game_info_dict['idx'].append(idx)

            rel_date = soup.find(class_='summary_detail release_data').find(class_='data').get_text()
            game_info_dict['release'].append(rel_date)

            # Per si el joc no té metascore
            if soup.find(class_=re.compile('metascore_w xlarge game*')) is None:
                metascore = np.nan
            else:
                metascore = float(soup.find(class_=re.compile('metascore_w xlarge game*')).get_text()) / 10
            game_info_dict['metascore'].append(metascore)

            n_reviews_sec = soup.find(class_='score_summary metascore_summary').find(class_='summary').get_text()
            n_reviews = int(re.findall(r'\d+', n_reviews_sec)[0])
            game_info_dict['n_reviews'].append(n_reviews)

            user_score = soup.find(class_='userscore_wrap feature_userscore').find(class_='metascore_w').get_text()
            if user_score == 'tbd':
                user_score = np.nan
            else:
                user_score = float(user_score)
            game_info_dict['user_score'].append(user_score)

            n_user_score_sec = soup.find(class_='userscore_wrap feature_userscore').find(class_='summary').get_text()
            if len(re.findall(r'\d+', n_user_score_sec)) == 0:
                n_user_score = 0
            else:
                n_user_score = int(re.findall(r'\d+', n_user_score_sec)[0])
            game_info_dict['n_user_score'].append(n_user_score)

            developers = soup.find(class_='summary_detail developer').findAll(class_='data')
            developer = ', '.join([x.get_text(strip=True) for x in developers])
            game_info_dict['developer'].append(developer)

            generes = soup.find(class_='summary_detail product_genre').findAll(class_='data')
            genere = ', '.join([x.get_text() for x in generes])
            game_info_dict['genere'].append(genere)

            # de vegades aquest atribut no es troba present
            try:
                n_online_multiplayer = soup.find(class_='summary_detail product_players').find(class_='data').get_text()
                game_info_dict['n_online_multiplayer'].append(n_online_multiplayer)
            except AttributeError:
                game_info_dict['n_online_multiplayer'].append('Not available')

        df_games_info = pd.DataFrame(game_info_dict)
        return df_games_info

    def final_data_process(self, df1, df2):
        linked_dfs = df1.join(df2.set_index('idx'), how='left')
        df_filtered = linked_dfs[linked_dfs['score'] == 1].copy()

        sel = df_filtered.drop(['title_metacritic', 'score', 'link'], axis=1).set_index(['title', 'platform'])
        sel = sel.sort_values('title').unstack(level=-1)

        sel.columns = [x[1] + '_' + x[0] for x in sel.columns]

        sel.reset_index(inplace=True)

        sorted_colnames = ['title']
        for i in ['pc_', 'ps4_', 'xboxone_']:
            for j in ['genere', 'release', 'metascore', 'n_reviews',
                      'user_score', 'n_user_score',
                      'developer', 'n_online_multiplayer']:
                sorted_colnames.append(i + j)

        sel = sel[sorted_colnames]

        # afegim titols sense resultas de busqueda

        title_no_in = set(linked_dfs['title'].values) - set(sel['title'].values)

        df_title_no_in = pd.DataFrame(index=range(len(title_no_in)), columns=sel.columns)
        df_title_no_in['title'] = title_no_in
        df_final_selection = sel.append(df_title_no_in).sort_values('title').reset_index(drop=True)

        return df_final_selection


if __name__ == '__main__':
    ss = StadiaScrapper()
    games_stadia = ss.get_games_names()
    all_games_ps4 = ss.get_all_games_metacritic_beautifulsoup('ps4')
    linked_df = ss.get_similarities_df(games_stadia, all_games_ps4)
    all_games_xboxone = ss.get_all_games_metacritic_beautifulsoup('xboxone')
    linked_df = ss.get_similarities_df(games_stadia, all_games_xboxone, linked_df)
    all_games_pc = ss.get_all_games_metacritic_beautifulsoup('pc')
    linked_df = ss.get_similarities_df(games_stadia, all_games_pc, linked_df)
    linked_df.reset_index(drop=True, inplace=True)
    df_games_info = ss.get_games_info(linked_df)

    linked_df_with_games = ss.final_data_process(linked_df, df_games_info)
    print('guardant dades...')
    linked_df_with_games.to_csv('output_data/data.csv', index=False, sep=',')
    print('dades guardades!')
