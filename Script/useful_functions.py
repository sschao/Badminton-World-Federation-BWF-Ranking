import pandas as pd
from selenium import webdriver
from datetime import datetime
from bs4 import BeautifulSoup
import time
from tqdm import tqdm

def elo(winner_elo, loser_elo, k_factor): #normal elo model
    '''
    :param winner_elo: previous elo of the winner
    :param loser_elo: previous elo of the loser
    :param k_factor: magnitude of reward/penalty of the winner/loser (check wikipedia)
    Can use some simple static k-factor like 30 or 40 right now, but we can make it dynamic later
    :return: elo of winner and elo of loser as respective tuple
    '''
    winner_prob = 1/(1+10**((loser_elo-winner_elo)/400)) #happen
    loser_prob = 1/(1+10**((winner_elo-loser_elo)/400))
    winner_elo_new = winner_elo + k_factor*(1-winner_prob)
    loser_elo_new = loser_elo + k_factor*(0-loser_prob)
    return(winner_elo_new, loser_elo_new)

def fetch_valid_years_person(player_tournament_soup):
    '''

    :param player_tournament_soup: put in correct player soup (refer to beautifulsoup documentation)
    :return: list of string years player has data for competing based on bwf website
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
    '''
    cleans bwf match score string
    :param bwf_score_string: the score string format that bwf returns
    :return: list of player total points scored and opponent total points scored
    '''
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
    '''

    :param string: month string or month abbreviation (regardless of capitalization)
    :return: month integer (Ex: Aug -> 8)
    '''
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
    '''
    label the week number in a dataframe
    :param df: dataframe
    :return: dataframe with weeks labeled
    '''
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

def scrape_bwf_scores(player_url):
    '''

    :param player_url: player bwf url (should be previously scraped)
    :return: dataframe with all of the games that the player player
    '''
    df_player = pd.DataFrame()
    driver.get(player_url)
    player_html_link = driver.current_url
    player_tournament_results_html_link = player_html_link + '/tournament-results/'  # player tournament url
    driver.get(player_tournament_results_html_link)
    player_tournament_html = driver.page_source
    player_tournament_soup = BeautifulSoup(player_tournament_html, 'html.parser')
    valid_years_list = fetch_valid_years_person(player_tournament_soup)  # years where player has tournament data
    # if len(valid_years_list) == 0: # just one year of tournament data

    for valid_years in valid_years_list:
        tournament_year_url = f'{player_tournament_results_html_link}?year={valid_years}'
        driver.get(tournament_year_url)
        player_tournament_html_year = driver.page_source
        player_tournament_year_soup = BeautifulSoup(player_tournament_html_year, 'html.parser')
        tournaments = player_tournament_year_soup.findAll('div', {'class': 'tournament-results'})
        tournaments_str = str(tournaments[0])
        split_string = '<div class="box-profile-tournament"'
        tournaments_split = tournaments_str.split(split_string)  # split by each tournament so we can classify
        tournaments_split_valid_soups_strs = [split_string + tournament_split_str
                                              for tournament_split_str in tournaments_split]
        tournaments_split_valid_soups_strs.pop(0)  # remove first element bc its unnecessary and doesnt fit
        tournaments_split_valid_soups = [BeautifulSoup(tournaments_split_valid_soups_str, 'html.parser')
                                         for tournaments_split_valid_soups_str in tournaments_split_valid_soups_strs]
        for tournament_soup in tournaments_split_valid_soups:  # each tournament
            tournament_match_number = 1
            # tournament_event = tournament_soup.findAll('div', {'class': 'title-tournament-mat'
            #                                                              'ches'})[0].find('a').text
            # if "Singles" not in tournament_event: #doubles or mixed match
            #     continue
            box_profile_tournament = tournament_soup.findAll('div', {'class': 'box-profile-tournament'})[0]
            tournament_name = box_profile_tournament.find('a')['title']
            # print(tournament_event,tournament_name)
            tournament_day = box_profile_tournament.find("h4").text.split(', ')[0]
            # week of tournament and sometimes includes a country after a comma
            tournament_year = valid_years
            match_types = tournament_soup.findAll('div', {'class': 'title-tournament-matches'})
            # match_type = tournament_soup.findAll('div', {'class': 'title-tournament-matches'})[0].find('a').text
            tournament_matches_set = tournament_soup.findAll('div', {'class': 'tournament-matches'})
            for i in range(len(tournament_matches_set)):  # each set of matches (prelim rounds and main draw)
                tournament_match_number_type = 1
                tournament_matches = tournament_matches_set[i]
                tournament_matches_rows = tournament_matches.findAll('div', {'class': 'tournament-matches-row'})
                for tournament_match in tournament_matches_rows:  # each match
                    names_soup = tournament_match.findAll("div", {"class": "name"})
                    player_names = [names.find('a').text.replace('\n', '').
                                        lstrip(' ').rstrip(' ').title() for names in names_soup]
                    if len(player_names) != 2:  # bug in the bwf system and did not display scores or not singles
                        continue
                    match_type = tournament_soup.findAll('div', {'class': 'title-tournament-matches'})[i].find('a') \
                        .text.replace('\n', '').lstrip(' ').rstrip(' ').title()
                    player = player_names[0]
                    opponent = player_names[1]
                    opponent_link = names_soup[1].find('a')['href']
                    bwf_score = tournament_match.find('div', {'class': 'player-result-win'}).find('span').text
                    player_points = score(bwf_score)[0]
                    opponent_points = score(bwf_score)[1]
                    # score = tournament_match.find('span').text
                    result = tournament_match.find('strong').text
                    length = tournament_match.findAll("div", {"class": "timer"})[0].text
                    player_round = tournament_match.find('div', {'class': 'player-result-round'}).text
                    print(player_round.replace('\n', '').
                          lstrip(' ').rstrip(' ').title())
                    df_match = pd.DataFrame([[tournament_name, match_type, tournament_year, tournament_day, player,
                                              opponent, bwf_score, player_points, opponent_points, result, length,
                                              player_html_link, opponent_link, tournament_match_number,
                                              tournament_match_number_type]],
                                            columns=['Tournament Name', 'Match Type', 'Year', 'Week', 'Player',
                                                     "Opponent", 'Score', 'Player Points Scored',
                                                     'Opponent Points Scored',
                                                     'Result (W/L)', 'Time',
                                                     'Player BWF Link', 'Opponent BWF Link', 'Tournament Match Number',
                                                     'Match Type Number'])

                    df_player = pd.concat([df_player, df_match])
    return df_player
