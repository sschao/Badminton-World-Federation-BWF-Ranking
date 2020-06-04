import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common import exceptions
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import math
from tqdm import tqdm
import os

driver = webdriver.Chrome('C:\webdrivers\chromedriver.exe') #change this path to appropriate chrome driver directory
# driver.get("https://bwfbadminton.com/players/?char=all&country=")
# html = driver.page_source
# soup = BeautifulSoup(html, 'html.parser')
#
# def find_total_players(soup): #finds total number of players of bwf website historically
#     total_players_soup = soup.findAll("div", {"class": "widget-stats__big"})[0].text
#     total_players = int(total_players_soup.replace(" ", "").replace("\n", '').replace(',', ''))
#     return total_players
#
# def players_link_csv():
#     total_bwf_players = find_total_players(soup)
#     num_players = 15000 #number of players per page
#     # num_players = total_bwf_players #number of players per page
#     num_pages = math.ceil(total_bwf_players/num_players)
#     player_names = []
#     player_links = []
#     for j in tqdm(range(1,num_pages+1)):
#         driver.get(f'https://bwfbadminton.com/players/?char=all&country=&page_size={num_players}&page_no={j}')
#         html = driver.page_source
#         soup = BeautifulSoup(html, 'html.parser')
#         players = soup.findAll("div", { "class" : "player" }) #find all the player soups per page
#         # num_players_per_page = num_players
#         # if j == num_pages: #if last page
#         #     num_players_per_page = total_bwf_players - num_players*(j-1)+1
#             #number of players remaining on the last page plus 1 for python indexing
#         # for i in range(num_players_per_page):
#         for i in tqdm(range(num_players)):
#             try:
#                 per_player_info = players[i].findAll("div",{"class":"name"})
#                 player_name = per_player_info[0].find('a')['title']
#                 player_link = per_player_info[0].find('a')['href']
#                 # print(player_name,player_link)
#                 player_names.append(player_name.title())
#                 player_links.append(player_link)
#             except IndexError: #run out of players on the page
#                 break
#
#
#     df_player_information = pd.DataFrame([player_names,player_links],
#                                          index = ['Player Names', 'Player BWF Link']).T #transpose since we want the index as column titles
#     df_player_information.to_csv('C:\\Users\\shawn\\Desktop\\Personal Coding '
#                                  'Projects\\Badminton Rankings\\Data\\'
#                                  'bwf_all_historical_player_name_link.csv', index=False)
#     return(player_names, player_links)
# players_link_csv()
#
#
#
# df_player_information = pd.read_csv('C:\\Users\\shawn\\Desktop\\Personal Coding '
#                                  'Projects\\Badminton Rankings\\Data\\'
#                                  'bwf_all_historical_player_name_link.csv')
#
# # df_players_stats = pd.DataFrame(0, index = df_player_information.index, columns = ['Player Names', 'Player BWF Link',
# #                                                                                    'Singles Wins', 'Singles Losses'
# #                                           'Singles Prize Money', 'Doubles Wins', 'Doubles Losses', 'Doubles Prize Money',
# #                                           'Mixed Wins', 'Mixed Losses', 'Mixed Prize Money'])
#
#
# df_players_stats = df_player_information.copy()
# df_players_stats['Singles Wins'], df_players_stats['Singles Losses'], df_players_stats['Singles Prize Money']\
#     , df_players_stats['Doubles Wins'], df_players_stats['Doubles Losses'], df_players_stats['Doubles Prize Money']\
#     , df_players_stats['Mixed Wins'], df_players_stats['Mixed Losses'], df_players_stats['Mixed Prize Money'] = [0,0,0,
#                                                                                                                  0,0,0,0,0,0]
num_players_scraped = 27508
df_players_stats = pd.read_csv(f'C:\\Users\\shawn\\Desktop\\Personal Coding Projects'
                               f'\\Badminton Rankings\\Data\\bwf_all_players_events_stats'
                               f'_{str(num_players_scraped)}.csv')
df_players_stats.to_csv(f'C:\\Users\\shawn\\Desktop\\Personal Coding Projects'
                        f'\\Badminton Rankings\\Data\\bwf_all_players_events_stats'
                        f'_{str(num_players_scraped)}.csv', index=False)

def player_stats(player_url, driver):
    '''

    :param player_url: bwf player url
    :param driver: webdriver (Chrome in my case)
    :return: dictionary of event to list of wins, losses, and prize money
    '''
    performance_stats = {}
    # performance_stats = []
    try:
        driver.get(player_url)
        html = driver.page_source
    except TimeoutException as ex:
        driver.quit()
        time.sleep(60)
        driver = webdriver.Chrome('C:\webdrivers\chromedriver.exe')  # change this path to appropriate chrome driver directory
        driver.get(player_url)
    player_soup = BeautifulSoup(html, 'html.parser')
    performance = player_soup.find_all("div",{"class":"performance-overview"}) #len 3: singles, doubles, mixed
    for i in range(len(performance)):
        event_name = performance[i].find('h4').text.title().split(' ')[1]
        event = performance[i].find_all('td',{"align":'center'})
        # total_games_played = event.find_all('td',{"align":'center'})[1].text
        wins = event[2].text.replace(',','')
        losses = event[3].text.replace(',','')
        total_money = event[5].text.replace(',','')
        performance_stats[event_name] = [wins, losses, total_money]
        # performance_stats.append(int(wins))
        # performance_stats.append(int(losses))
        # performance_stats.append(float(total_money))
    return performance_stats

for index, row in tqdm(df_players_stats[num_players_scraped:].iterrows(), total = df_players_stats[num_players_scraped:].shape[0]):
    # print(row)
    player_url = row['Player BWF Link']
    if index%310 == 0:
        driver.quit()
        time.sleep(72)
        driver = webdriver.Chrome('C:\webdrivers\chromedriver.exe')
    # df_players_stats.at[index, 'Player Name'] = row['Player Name']
    # df_players_stats.at[index, 'Player BWF Link'] = row['Player BWF Link']
    stats_dict = player_stats(player_url, driver)
    if len(stats_dict) == 0: #no stats
        num_players_scraped+=1
        df_players_stats.to_csv(
            f'C:\\Users\\shawn\\Desktop\\Personal Coding Projects'
            f'\Badminton Rankings\\Data\\bwf_all_players_events_stats_{str(num_players_scraped)}.csv',
            index=False)
        os.remove(
            f'C:\\Users\\shawn\\Desktop\\Personal Coding Projects'
            f'\\Badminton Rankings\\Data\\bwf_all_players_events_stats_{str(num_players_scraped - 1)}.csv')
        continue
    # prev_data = list(df_player_information.loc[index])
    # combine_data = prev_data+stats
    for key in stats_dict.keys():
        df_players_stats.at[index, f'{key} Wins'] = stats_dict[key][0]
        df_players_stats.at[index, f'{key} Losses'] = stats_dict[key][1]
        df_players_stats.at[index, f'{key} Prize Money'] = stats_dict[key][2]
    num_players_scraped+=1
    df_players_stats.to_csv(f'C:\\Users\\shawn\\Desktop\\Personal Coding Projects'
                            f'\\Badminton Rankings\\Data\\bwf_all_players_events'
                            f'_stats_{str(num_players_scraped)}.csv', index = False)
    os.remove(f'C:\\Users\\shawn\\Desktop\\Personal Coding Projects\\Badminton Rankings'
              f'\\Data\\bwf_all_players_events_stats_{str(num_players_scraped-1)}.csv')
    # df_players_stats = pd.concat(df_players_stats, df_player_stats)