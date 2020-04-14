import argparse
import sys

from src.scraper_external import StadiaScrapper
from src.scraper_stadia import add_stadia_data

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stadia', type=str,
                        help="Passar 'all','external','stadia-only' o 'stadia-update' com a argument")
    args = parser.parse_args()

    if args.stadia == 'external' or args.stadia == 'all':

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
        linked_df_with_games.to_csv('output_data/stadia_games_info.csv', index=False, sep=',')
        print('dades guardades!')

        if args.stadia == 'all':
            add_stadia_data()

    elif args.stadia == 'stadia-only':
        add_stadia_data(update_external=False)

    elif args.stadia == 'stadia-update':
        add_stadia_data()
    else:
        raise Exception("No s'ha reconegut l'argument passat. Prova amb 'all','external','stadia-only' o 'stadia-update'")
