import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np

df_sorted_players = pd.read_csv('C:\\Users\\shawn\\Desktop\\Personal Coding Projects'
                                '\\Badminton Rankings\\Data\\Complete Data\\sorted_current_former_ms.csv')

df_sorted_players['Player Elo'], df_sorted_players['Opponent Elo'] = None, None
tournaments = df_sorted_players['Tournament Name Year'].drop_duplicates().to_list()
tournament_game_count = {}
# for tournament in tqdm(tournaments):
#     df_tournament = df_sorted_players[df_sorted_players['Tournament Name Year'] == tournament]
#     tournament_game_count[tournament] = len(df_tournament)

# max_games_tournament
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

#use bwf link because unique
elo_dict = dict.fromkeys(list(set(list(df_sorted_players['Player BWF Link'])+list(df_sorted_players['Opponent BWF Link']))),1200)

df_sorted_players = df_sorted_players.fillna('')
#drop duplicate games player 1 vs player 2 and player 2 vs player 1
for index, row in tqdm(df_sorted_players[45500:].iterrows(), total = df_sorted_players[45500:].shape[0]):
    # df_optimize = df_sorted_players[index:index+1000000] #search in a smaller subset to speed up
    # df_duplicates = df_optimize[(((df_optimize['Player']==row['Player']) & (df_optimize['Opponent']==row['Opponent']) & (df_optimize['Opponent Points Scored']== row['Opponent Points Scored']) & (df_optimize['Player Points Scored'] == row['Player Points Scored']))
    #                                   |((df_optimize['Player']==row['Opponent']) & (df_optimize['Opponent']==row['Player']) & (df_optimize['Opponent Points Scored']== row['Player Points Scored']) & (df_optimize['Player Points Scored'] == row['Opponent Points Scored'])))
    #                                   & ((df_optimize['Tournament Name Year']==row['Tournament Name Year']) & (df_optimize['Match Type'] == row['Match Type']) & (df_optimize['Opponent']!= '') & (~df_optimize['Result (W/L)'].isin(['-', 'BYE', 'TBC', ''])))]
    # df_duplicates = df_optimize[(((df_optimize['Player']==row['Player']) & (df_optimize['Opponent']==row['Opponent']) & (df_optimize['Opponent Points Scored']== row['Opponent Points Scored']) & (df_optimize['Player Points Scored'] == row['Player Points Scored']))
    #                                   |((df_optimize['Player']==row['Opponent']) & (df_optimize['Opponent']==row['Player']) & (df_optimize['Opponent Points Scored']== row['Player Points Scored']) & (df_optimize['Player Points Scored'] == row['Opponent Points Scored'])))
    #                                   & (df_optimize['Tournament Name Year']==row['Tournament Name Year'])]
    df_duplicates = df_sorted_players[(((df_sorted_players['Player']==row['Player']) & (df_sorted_players['Opponent']==row['Opponent']) & (df_sorted_players['Opponent Points Scored']== row['Opponent Points Scored']) & (df_sorted_players['Player Points Scored'] == row['Player Points Scored']))
                                      |((df_sorted_players['Player']==row['Opponent']) & (df_sorted_players['Opponent']==row['Player']) & (df_sorted_players['Opponent Points Scored']== row['Player Points Scored']) & (df_sorted_players['Player Points Scored'] == row['Opponent Points Scored'])))
                                      & ((df_sorted_players['Tournament Name Year']==row['Tournament Name Year'])& (df_sorted_players['Match Type'] == row['Match Type']) & (df_sorted_players['Opponent']!= '') & (df_sorted_players['Time'] == row['Time']) & (~df_sorted_players['Result (W/L)'].isin(['-', 'BYE', 'TBC', ''])))]
    if len(df_duplicates) == 2: #game is duplicated exactly twice
        df_sorted_players = df_sorted_players.drop([df_duplicates.iloc[[-1]].index[0]])
        # print(len(df_sorted_players))
    if len(df_duplicates) > 2: #weird edge case that needs inspection
        print(df_duplicates)
        break

df_sorted_players.to_csv('C:\\Users\\shawn\\Desktop\\Personal Coding Projects'
                                '\\Badminton Rankings\\Data\\Complete Data\\sorted_current_former_ms_drop_dup.csv')

for index, row in tqdm(df_sorted_players.iterrows(), total = df_sorted_players.shape[0]):
    if row['Result (W/L)'] in ['-', 'BYE', 'TBC', '']: #no game or no game score reported
        continue
    #determine winners and losers
    if row['Result (W/L)'] == 'W':
        winner = row['Player BWF Link']
        loser = row['Opponent BWF Link']
    elif row['Result (W/L)'] == 'L':
        loser = row['Player BWF Link']
        winner = row['Opponent BWF Link']

    winner_new_elo, loser_new_elo = elo(elo_dict[winner], elo_dict[loser], 40) #compute elo
    elo_dict[winner] = winner_new_elo
    elo_dict[loser] = loser_new_elo

    if row['Result (W/L)'] == 'W':
        df_sorted_players.loc[index, 'Player Elo'] = winner_new_elo
        df_sorted_players.loc[index, 'Opponent Elo'] = loser_new_elo
    elif row['Result (W/L)'] == 'L':
        df_sorted_players.loc[index, 'Player Elo'] = loser_new_elo
        df_sorted_players.loc[index, 'Opponent Elo'] = winner_new_elo

df_sorted_players.to_csv('C:\\Users\\shawn\\Desktop\\Personal Coding Projects'
                                '\\Badminton Rankings\\Data\\Complete Data\\current_former_ms_elo.csv')


def reverse_score_string(bwf_score_string):
    try:
        forbidden = ['', 'Walkover']
        if bwf_score_string in forbidden:
            return bwf_score_string
        score_list = bwf_score_string.split(', ')
        reversed_score_string = ''
        count = 0 #count to find the last game in the string so dont add comma
        for game in score_list:
            count += 1
            game_score = game.split('-')
            if count == len(score_list):
                reversed_score_string += f'{game_score[1]}-{game_score[0]}'
            else:
                reversed_score_string += f'{game_score[1]}-{game_score[0]}, '
        return reversed_score_string
    except:
        print(bwf_score_string)

def create_player_df(df_players, player_bwf_link):
    df_player = df_players[(df_players['Player BWF Link']==player_bwf_link)]
    df_opponent = df_players[(df_players['Opponent BWF Link'] == player_bwf_link)]
    cols = list(df_opponent)
    a,b,c,d = cols.index('Opponent'), cols.index('Opponent BWF Link'), cols.index('Opponent Points Scored'), cols.index('Opponent Elo')
    e,f,g,h = cols.index('Player'), cols.index('Player BWF Link'), cols.index('Player Points Scored'), cols.index('Player Elo')
    cols[a], cols[b], cols[c], cols[d], cols[e], cols[f], cols[g], cols[h] = cols[e], cols[f], cols[g], cols[h], cols[a], cols[b], cols[c], cols[d]
    df_opponent.columns = cols
    df_opponent['Result (W/L)'] = df_opponent['Result (W/L)'].map({'W':'L', 'L':'W', '':'', 'BYE':'BYE', '-':'-', 'TBC':'TBC'})
    df_opponent['Score'] = df_opponent['Score'].apply(reverse_score_string)
    df_player_final = pd.concat([df_player, df_opponent])
    df_player
    df_player_sorted = df_player_final.sort_values(
        by=['Year', 'Week Number', 'Match Type Ordering', 'Match Type Number'], ascending=True)
    #keep only the final elo rating per tournament
    df_player_final_weekly = df_player_sorted.drop_duplicates(subset=['Year', 'Week', 'Tournament Name'], keep = 'last')
    df_player_final_weekly["S"] = df_player_final_weekly['Week Number'].astype(str) + '-' + df_player_final_weekly['Year'].astype(int).astype(str)
    df_player_final_weekly["Date Time"] = df_player_final_weekly["S"].apply(lambda x: pd.to_datetime(x+'0', format='%W-%Y%w'))
    df_player_final_weekly['Player Elo'].replace('', np.nan, inplace = True)
    df_player_final_weekly.dropna(subset = ['Player Elo'], inplace = True)
    plt.plot(df_player_final_weekly['Date Time'], df_player_final_weekly['Player Elo'].astype(float))
    plt.xlabel('Year')
    plt.ylabel('Elo Rating')
    plt.title(f'{player_bwf_link} Historical Elo Ratings')
    return df_player_sorted








