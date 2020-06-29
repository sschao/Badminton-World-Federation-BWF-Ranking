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
import glob



driver = webdriver.Chrome('C:\webdrivers\chromedriver.exe') #change this path to appropriate chrome driver directory
def fetch_ranking_week_year_singles_soup(year, week, page_num): #get the first 10000k players which is more there are players
    driver.get(f'https://bwfbadminton.com/rankings/2/bwf-world-rankings/6/men-s-singles/{str(year)}/{str(week)}/?rows=10000&page_no={page_num}')
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    return soup


year = 2020
week = 12

def fetch_valid_years_person(player_tournament_soup):
    '''

    :param player_tournament_soup: put in correct player soup
    :return: list of string years player has data for competing
    '''
    valid_years_list= []
    try:
        valid_years = player_tournament_soup.findAll('select', {'class': 'ddlResultPage'})[0].findAll('option')
        for i in range(len(valid_years)):
            valid_years_list.append(valid_years[i]['value'])
    except IndexError: #only one year of data but there could errors so engineered code to handle that

        tournament_names = player_tournament_soup.findAll('div', {'class': 'box-profile'
                                                                           '-tournament'}) #find tournament name
        # first tournament name on screen. Should have year in it
        # print(player_tournament_soup.findAll('div', {'class': 'box-profile'
        #                                                                    '-tournament'})[0].find('a'))
        for tournament_name_soup in tournament_names:
            tournament_name = tournament_name_soup.find('a')['title']
            # print(tournament_name)
            year = datetime.today().year
            while year >= 1897: #doubt bwf has data that far back for players we are looking at. Also first all england was in 1898
                if str(year) in tournament_name and str(year) not in valid_years_list:
                    valid_years_list.append(str(year))
                    break #no way an annual tournament has two years associated with it
                year -= 1
    return valid_years_list

def score(bwf_score_string):
    try:
        forbidden = ['', 'Walkover']
        if bwf_score_string in forbidden:
            return [None, None]
        if 'Walkover, ' in bwf_score_string:
            bwf_score_string = bwf_score_string.split('Walkover, ')[1]
        score_list = bwf_score_string.split(', ')
        player_score = 0
        opponent_score = 0
        for game in score_list:
            game_score = game.split('-')
            player_score += int(game_score[0])
            opponent_score += int(game_score[1])
        return [player_score, opponent_score]
    except:
        print(bwf_score_string)
        return [None, None]

def month_string_to_number(string):
    m = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr':4,
         'may':5,
         'jun':6,
         'jul':7,
         'aug':8,
         'sep':9,
         'oct':10,
         'nov':11,
         'dec':12
        }
    s = string.strip()[:3].lower()

    try:
        out = m[s]
        return out
    except:
        raise ValueError('Not a month')

def get_week(df):
    df['Week'] = df['Week'].str.split(', ').str[0] #get rid of the country
    for index, row in df.iterrows():
        week_list = row['Week'].split(' ')
        start_day = int(week_list[0])
        try: #if tournament goes between two months based on formatting. This comes first
            month_number = month_string_to_number(week_list[1]) #month start date
        except ValueError: #if tournament on goes on within one month
            month_number = month_string_to_number(week_list[-1])
        df.loc[index, 'Week Number'] = datetime.date(int(row['Year']), month_number, start_day).strftime("%V")
    return df

df_matches = pd.DataFrame(columns = ['Tournament Name', 'Match Type','Year', 'Week','Player',
                                                           "Opponent", 'Score', 'Result (W/L)', 'Time',
                                                           'Player BWF Link', 'Opponent BWF Link'])


page_num_csv = 0
# player_num_page_csv = 1765
# df_matches =pd.read_csv(f'C:\\Users\\shawn\\Desktop\\Personal Coding Projects'
#                         f'\\Badminton Rankings\\Data\\mens_singles_matches_{year}_{week}_{page_num_csv}_{player_num_page_csv}.csv')

for page_num in tqdm(range(page_num_csv+1)): #singles and add one bc python indexing
    badminton_soup = fetch_ranking_week_year_singles_soup(year, week, page_num+1)
    players_soup = badminton_soup.findAll("div", { "class" : "player" }) #players on each page
    # for player_soup in players_soup:
    # for player_num_page in tqdm(range(player_num_page_csv + 1, len(players_soup))):  # add one because of python indexing
    for player_num_page in tqdm(range(len(players_soup))):
    # for player_num_page in tqdm(range(player_num_page_csv+1,len(players_soup))): #add one because of python indexing
        if player_num_page%50 == 5:
            driver.quit()
            time.sleep(75)
            driver = webdriver.Chrome('C:\webdrivers\chromedriver.exe')
        player_name = players_soup[player_num_page].find('a')['title']
        player_url = players_soup[player_num_page].find('a')['href']
        driver.get(player_url)
        player_html_link = driver.current_url
        player_tournament_results_html_link = player_html_link+'/tournament-results/' #player tournament url
        driver.get(player_tournament_results_html_link)
        player_tournament_html = driver.page_source
        player_tournament_soup = BeautifulSoup(player_tournament_html, 'html.parser')
        valid_years_list = fetch_valid_years_person(player_tournament_soup) #years where player has tournament data
        # if len(valid_years_list) == 0: # just one year of tournament data

        for valid_years in valid_years_list:
            tournament_year_url = f'{player_tournament_results_html_link}?year={valid_years}'
            driver.get(tournament_year_url)
            player_tournament_html_year = driver.page_source
            player_tournament_year_soup = BeautifulSoup(player_tournament_html_year, 'html.parser')
            tournaments = player_tournament_year_soup.findAll('div',{'class':'tournament-results'})
            tournaments_str = str(tournaments[0])
            split_string = '<div class="box-profile-tournament"'
            tournaments_split = tournaments_str.split(split_string) #split by each tournament so we can classify
            tournaments_split_valid_soups_strs = [split_string + tournament_split_str
                                                  for tournament_split_str in  tournaments_split]
            tournaments_split_valid_soups_strs.pop(0) #remove first element bc its unnecessary and doesnt fit
            tournaments_split_valid_soups = [BeautifulSoup(tournaments_split_valid_soups_str,'html.parser')
                                             for tournaments_split_valid_soups_str in tournaments_split_valid_soups_strs]
            for tournament_soup in tournaments_split_valid_soups: #each tournament
                tournament_match_number = 1
                # tournament_event = tournament_soup.findAll('div', {'class': 'title-tournament-mat'
                #                                                              'ches'})[0].find('a').text
                # if "Singles" not in tournament_event: #doubles or mixed match
                #     continue
                box_profile_tournament = tournament_soup.findAll('div', {'class': 'box-profile-tournament'})[0]
                tournament_name = box_profile_tournament.find('a')['title']
                # print(tournament_event,tournament_name)
                tournament_day = box_profile_tournament.find("h4").text.split(', ')[0]
                #week of tournament and sometimes includes a country after a comma
                tournament_year = valid_years
                match_types = tournament_soup.findAll('div', {'class': 'title-tournament-matches'})
                # match_type = tournament_soup.findAll('div', {'class': 'title-tournament-matches'})[0].find('a').text
                tournament_matches_set = tournament_soup.findAll('div', {'class': 'tournament-matches'})
                for i in range(len(tournament_matches_set)): #each set of matches (prelim rounds and main draw)
                    tournament_match_number_type = 1
                    tournament_matches = tournament_matches_set[i]
                    tournament_matches_rows = tournament_matches.findAll('div',{'class':'tournament-matches-row'})
                    for tournament_match in tournament_matches_rows: #each match
                        names_soup = tournament_match.findAll("div", { "class" : "name" })
                        player_names= [names.find('a').text.replace('\n', '').
                                            lstrip(' ').rstrip(' ').title() for names in names_soup]
                        if len(player_names) != 2: #bug in the bwf system and did not display scores or not singles
                            continue
                        match_type = tournament_soup.findAll('div', {'class': 'title-tournament-matches'})[i].find('a')\
                            .text.replace('\n', '').lstrip(' ').rstrip(' ').title()
                        player = player_names[0]
                        opponent = player_names[1]
                        opponent_link = names_soup[1].find('a')['href']
                        bwf_score = tournament_match.find('div',{'class':'player-result-win'}).find('span').text
                        player_points = score(bwf_score)[0]
                        opponent_points = score(bwf_score)[1]
                        # score = tournament_match.find('span').text
                        result = tournament_match.find('strong').text
                        length = tournament_match.findAll("div", { "class" : "timer" })[0].text
                        player_round = tournament_match.find('div', {'class':'player-result-round'}).text
                        print(player_round.replace('\n', '').
                                            lstrip(' ').rstrip(' ').title())
                        df_match = pd.DataFrame([[tournament_name, match_type, tournament_year, tournament_day, player,
                                                  opponent,bwf_score,player_points, opponent_points, result,length,
                                                  player_html_link, opponent_link, tournament_match_number, tournament_match_number_type]],
                                                columns = ['Tournament Name', 'Match Type','Year', 'Week','Player',
                                                           "Opponent", 'Score', 'Player Points Scored', 'Opponent Points Scored',
                                                           'Result (W/L)', 'Time',
                                                           'Player BWF Link', 'Opponent BWF Link', 'Tournament Match Number', 'Match Type Number'])
                        # print(df_match)
                        # cols = ['Tournament Name', 'Year', 'Week','Player',
                                                           # "Opponent", 'Score', 'Result (W/L)', 'Time']
                        # merged = pd.merge(df_matches,df_match, on = cols, how ='outer', indicator = True)
                        # df_matches = pd.concat([df_matches,merged.iloc[merged._merge=='left_only', cols]])
                        df_matches = pd.concat([df_matches, df_match])
                        tournament_match_number += 1
                        tournament_match_number_type += 1
        # print(df_matches.tail(10))
        # filelist_to_remove = glob.glob(f'C:\\Users\\shawn\\Desktop\\Personal Coding Projects'
        #                f'\\Badminton Rankings\\Data\\mens_singles_matches_*.csv')
        # for file_to_remove in filelist_to_remove:
        #     os.remove(file_to_remove)
        # df_matches.to_csv(f'C:\\Users\\shawn\\Desktop\\Personal Coding Projects'
        #                 f'\\Badminton Rankings\\Data\\mens_singles_matches_type_{year}_{week}_{page_num}_{player_num_page}.csv', index=False)

driver.quit()

# for page_num in tqdm(range(page_num_csv+1,23)): #singles
#     badminton_soup = fetch_ranking_week_year_singles_soup(year, week, page_num)
#     players_soup = badminton_soup.findAll("div", { "class" : "player" }) #players on each page
#     # for player_soup in players_soup:
#     for player_num_page in tqdm(range(len(players_soup))):
#         if player_num_page%10 == 5:
#             driver.quit()
#             time.sleep(75)
#             driver = webdriver.Chrome('C:\webdrivers\chromedriver.exe')
#         player_name = players_soup[player_num_page].find('a')['title']
#         player_url = players_soup[player_num_page].find('a')['href']
#         driver.get(player_url)
#         player_html_link = driver.current_url
#         player_tournament_results_html_link = player_html_link+'/tournament-results/' #player tournament url
#         driver.get(player_tournament_results_html_link)
#         player_tournament_html = driver.page_source
#         player_tournament_soup = BeautifulSoup(player_tournament_html, 'html.parser')
#         valid_years_list = fetch_valid_years_person(player_tournament_soup) #years where player has tournament data
#         for valid_years in valid_years_list:
#             tournament_year_url = f'{player_tournament_results_html_link}?year={valid_years}'
#             driver.get(tournament_year_url)
#             player_tournament_html_year = driver.page_source
#             player_tournament_year_soup = BeautifulSoup(player_tournament_html_year, 'html.parser')
#             tournaments = player_tournament_year_soup.findAll('div',{'class':'tournament-results'})
#             tournaments_str = str(tournaments[0])
#             split_string = '<div class="box-profile-tournament"'
#             tournaments_split = tournaments_str.split(split_string) #split by each tournament so we can classify
#             tournaments_split_valid_soups_strs = [split_string + tournament_split_str
#                                                   for tournament_split_str in  tournaments_split]
#             tournaments_split_valid_soups_strs.pop(0) #remove first element bc its unnecessary and doesnt fit
#             tournaments_split_valid_soups = [BeautifulSoup(tournaments_split_valid_soups_str,'html.parser')
#                                              for tournaments_split_valid_soups_str in tournaments_split_valid_soups_strs]
#             for tournament_soup in tournaments_split_valid_soups: #each tournament
#                 # tournament_event = tournament_soup.findAll('div', {'class': 'title-tournament-mat'
#                 #                                                              'ches'})[0].find('a').text
#                 # if "Singles" not in tournament_event: #doubles or mixed match
#                 #     continue
#                 box_profile_tournament = tournament_soup.findAll('div', {'class': 'box-profile-tournament'})[0]
#                 tournament_name = box_profile_tournament.find('a')['title']
#                 # print(tournament_event,tournament_name)
#                 tournament_day = box_profile_tournament.find("h4").text
#                 tournament_year = valid_years
#                 match_type = tournament_soup.findAll('div', {'class': 'title-tournament-matches'})[0].find('a').text
#                 tournament_matches_set = tournament_soup.findAll('div', {'class': 'tournament-matches'})
#                 for tournament_matches in tournament_matches_set: #each set of matches (prelim rounds and main draw)
#                     tournament_matches_rows = tournament_matches.findAll('div',{'class':'tournament-matches-row'})
#                     for tournament_match in tournament_matches_rows: #each match
#                         names_soup = tournament_match.findAll("div", { "class" : "name" })
#                         player_names= [names.find('a').text.replace('\n', '').
#                                             lstrip(' ').rstrip(' ').title() for names in names_soup]
#                         if len(player_names) != 2: #bug in the bwf system and did not display scores or not singles
#                             continue
#                         player = player_names[0]
#                         opponent = player_names[1]
#                         score = tournament_match.find('span').text
#                         result = tournament_match.find('strong').text
#                         length = tournament_match.findAll("div", { "class" : "timer" })[0].text
#
#                         df_match = pd.DataFrame([[tournament_name, tournament_year, tournament_day, player,
#                                                   opponent,score,result,length]],
#                                                 columns = ['Tournament Name', 'Year', 'Week','Player',
#                                                            "Opponent", 'Score', 'Result (W/L)', 'Time'])
#                         # cols = ['Tournament Name', 'Year', 'Week','Player',
#                                                            # "Opponent", 'Score', 'Result (W/L)', 'Time']
#                         # merged = pd.merge(df_matches,df_match, on = cols, how ='outer', indicator = True)
#                         # df_matches = pd.concat([df_matches,merged.iloc[merged._merge=='left_only', cols]])
#                         df_matches = pd.concat([df_matches, df_match])
#         filelist_to_remove = glob.glob(f'C:\\Users\\shawn\\Desktop\\Personal Coding Projects'
#                        f'\\Badminton Rankings\\Data\\mens_singles_matches_*.csv')
#         for file_to_remove in filelist_to_remove:
#             os.remove(file_to_remove)
#         df_matches.to_csv(f'C:\\Users\\shawn\\Desktop\\Personal Coding Projects'
#                         f'\\Badminton Rankings\\Data\\mens_singles_matches_{year}_{week}_{page_num}_{player_num_page}.csv', index=False)

df_matches_drop_dup = df_matches.drop_duplicates(subset=['Tournament Name', 'Year', 'Week', 'Player',
                                                         "Opponent", 'Score', 'Result (W/L)', 'Time', 'Match Type',
                                                         'Tournament Match Number', 'Match Type Number'], keep='first')
df_matches_drop_dup = get_week(df_matches_drop_dup)

df_matches_drop_dup.to_csv(f'C:\\Users\\shawn\\Desktop\\Personal Coding Projects'
                        f'\\Badminton Rankings\\Data\\mens_singles_matches_type_{year}_{week}_scraped_total.csv',
                           index=False)
# driver.get("https://bwfbadminton.com/rankings/")
# html = driver.page_source
# soup = BeautifulSoup(html, 'html.parser')
