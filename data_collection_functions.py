import pandas as pd
import numpy as np
from datetime import datetime
from sportsipy.mlb.boxscore import Boxscore
from sportsipy.mlb.boxscore import Boxscores

# Function to return games in certain time range
def get_current_games(date,end_date,end_week=None):
    
    games = Boxscores(date,end_date)
    schedule = games.games

    game_days = []
    for day in schedule.values():
        for game in day:
            game_days.append(game['boxscore'])
            
    season_games = []

    for i in game_days:
        temp = Boxscore(i).dataframe
        season_games.append(temp)

    df = pd.concat(season_games, axis = 0).reset_index()

    return df




def team_regular_season(df,team,average=True,num=162):
    #Set year range for what games you want to access
    #Rename columns to avoid deletetion later
    df=df.rename(columns={'home_home_runs':'home_HR','away_home_runs':'away_HR'})
    
        #Get all the home winner and away winner games alone
    Home = df[(df['winner'] == 'Home')] 
    Away= df[(df['winner'] == 'Away')]
    
        #Get games where the team was the home team
    home_wins=Home[(Home['winning_abbr'] == team)]
    home_loss=Away[(Away['losing_abbr'] == team)]
    home_games= pd.concat([home_wins,home_loss])
    home_offense = home_games.filter(like = 'home')
    
      #Get games where the team was the away team
    away_wins=Away[(Away['winning_abbr']==team)]
    away_loss=Home[(Home['losing_abbr']==team)]
    away_games= pd.concat([away_wins,away_loss])
    away_offense = away_games.filter(like = 'away')
    
        # split the dataframes to only have the statistics of the given team
    home_offense.columns = home_offense.columns.str.replace('home_','')
    away_offense.columns = away_offense.columns.str.replace('away_','')
    
    #combine offensive stats into one df
    team_offense = pd.concat([home_offense, away_offense])
    
        # create oppposing team statistics from the given games
    home_games_opponents = home_games.filter(like = 'away')
    away_games_opponents = away_games.filter(like = 'home')
    
        # rename the columns from the opponent statistics dataframes
    home_games_opponents.columns = home_games_opponents.columns.str.replace('away_','')
    away_games_opponents.columns = away_games_opponents.columns.str.replace('home_','')
    
    team_opponents= pd.concat([home_games_opponents,away_games_opponents])
    
        # concat the team stats and the opponent stats to create a full picture of the team's season
    team_full = pd.concat([team_offense, team_opponents.add_prefix('Opp_')], axis = 1)
    team_full = team_full.assign(name=team)
    
    # Certain teams only played 161 games this season and therefor need different number
#     club_161=['DET','CLE','MIA','ATL']
#     if team in club_161:
#         num=161
#     else:
#         num=162
#     add= ((team,)*num)
#     team_full['name']= add
    
    
        # return either the season averages or the game by game statistics
    if average:
            team_full = team_full.groupby('name').mean().reset_index()
    
    
    return team_full




def single_game(team1_name, team2_name,df):
    
    # from the Team abbreviations get a dataframe with the average seasonlong team statistics.
    team1 = team_regular_season(df,team1_name)
    team2 = team_regular_season(df,team2_name)
    
    #make the single game by concating those dataframes
    game = pd.concat([team1.add_prefix('H_'), team2.add_prefix('A_')], axis = 1)
    
    return game




def create_season_df(df,date):
    
    #Reset the index
    df.reset_index(inplace=True)
  
    # create a DataFrame for the season we are looking for
    # season_df for whatever season you are looking for
    season_df = df[df['date'] >= date]
    #reset index
    #season_df.reset_index(inplace = True)
    
    #Get home winners and Away winners in their own dataframe
    Home = season_df[(season_df['winner'] == 'Home')] 
    Away= season_df[(season_df['winner'] == 'Away')]
    
    #Rename columns in the home win from winner and loser to home and away
    Home=Home.rename(columns={'winning_abbr':'home_abbr','winning_name':'home_name','losing_name':'away_name',
                         'losing_abbr':'away_abbr'})
    
    #Rename columns in the away win from winner and loser to home and away
    Away= Away.rename(columns={'winning_abbr':'away_abbr','winning_name':'away_name','losing_name':'home_name',
                         'losing_abbr':'home_abbr'})
    
    #Concat these to make season_df now the same but with these new column names
    season_df= pd.concat([Home,Away])
    
    #Get Home and away alone once again
    Home = season_df[(season_df['winner'] == 'Home')] 
    Away= season_df[(season_df['winner'] == 'Away')]
    
    #Create a winning abbreviation column
    Home['winning_abbr']= Home['home_abbr']
    Away['winning_abbr']= Away['away_abbr']
    
    #Concat to update season_df
    season_df=pd.concat([Home,Away])
    
    #order it by date again
    season_df=season_df.sort_values('date')
    
    
    # create a list with the two teams, home team always first, the season, and the day number of the game
    matchups = list(zip(season_df.home_abbr, season_df.away_abbr, season_df.date, season_df.winning_abbr))
    
    season_games = [] 

    #loop through matchups and create single games for each matchup using that function, then append to season games
    for team in matchups:
        game = single_game(team[0], team[1],df)
        season_games.append(game)
    
    # from the season games list concatenate all the outputted DataFrames and insert the location
    # of the winner (home(1), away(0))
    df = pd.concat(season_games, axis = 0)
    #reset_index
    df.reset_index(inplace = True, drop = True)
    #Create new column where it will have a 1 if home team won and 0 if away team won
    df['home_win'] = np.where(season_df.home_abbr ==season_df.winning_abbr,
                  [1],
                  [0])
                       
    return df

# def create_season_df(df,date):
    
#     #Reset the index
#     df.reset_index(inplace=True)
  
#     # create a DataFrame for the season we are looking for
#     # season_df for whatever season you are looking for
#     season_df = df[df['date'] >= date]
#     #reset index
#     #season_df.reset_index(inplace = True)
    
#     #Get home winners and Away winners in their own dataframe
#     Home = season_df[(season_df['winner'] == 'Home')] 
#     Away= season_df[(season_df['winner'] == 'Away')]
    
#     #Rename columns in the home win from winner and loser to home and away
#     Home=Home.rename(columns={'winning_abbr':'home_abbr','winning_name':'home_name','losing_name':'away_name',
#                          'losing_abbr':'away_abbr'})
    
#     #Rename columns in the away win from winner and loser to home and away
#     Away= Away.rename(columns={'winning_abbr':'away_abbr','winning_name':'away_name','losing_name':'home_name',
#                          'losing_abbr':'home_abbr'})
    
#     #Concat these to make season_df now the same but with these new column names
#     season_df= pd.concat([Home,Away])
    
#     #Get Home and away alone once again
#     Home = season_df[(season_df['winner'] == 'Home')] 
#     Away= season_df[(season_df['winner'] == 'Away')]
    
#     #Create a winning abbreviation column
#     Home['winning_abbr']= Home['home_abbr']
#     Away['winning_abbr']= Away['away_abbr']
    
#     #Concat to update season_df
#     season_df=pd.concat([Home,Away])
    
#     #order it by date again
#     season_df=season_df.sort_values('date')
    
    
#     # create a list with the two teams, home team always first, the season, and the day number of the game
#     matchups = list(zip(season_df.home_abbr, season_df.away_abbr, season_df.date, season_df.winning_abbr))
    
#     season_games = [] 

#     #loop through matchups and create single games for each matchup using that function, then append to season games
#     for team in matchups:
#         game = single_game(team[0], team[1],df2)
#         season_games.append(game)
    
#     # from the season games list concatenate all the outputted DataFrames and insert the location
#     # of the winner (home(1), away(0))
#     df = pd.concat(season_games, axis = 0)
#     #reset_index
#     df.reset_index(inplace = True, drop = True)
#     #Create new column where it will have a 1 if home team won and 0 if away team won
#     df['home_win'] = np.where(season_df.home_abbr ==season_df.winning_abbr,
#                   [1],
#                   [0])
                       
#     return df