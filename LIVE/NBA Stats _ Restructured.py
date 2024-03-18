import requests
import json
import time
import pytz
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
from unidecode import unidecode
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.multioutput import MultiOutputClassifier


# Constants
API_KEY = "f8439d4381msh236d31535d6c16dp15e6c6jsn4ab1fe08eda9"  # Use a secure method to store and retrieve API keys
API_HOST = "api-nba-v1.p.rapidapi.com"
HEADERS = {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": API_HOST}
GAMES_API_ENDPOINT = "https://api-nba-v1.p.rapidapi.com/games"
GAMES_STATS_API_ENDPOINT ="https://api-nba-v1.p.rapidapi.com/games/statistics"
TEAM_PLAYER_STATS_API_ENDPOINT ="https://api-nba-v1.p.rapidapi.com/players/statistics"


JSON_FILENAME_GAMES_TODAY_RAW = "nba_games_today_raw.json"
JSON_FILENAME_GAMES_TOMORROW_RAW = "nba_games_tomorrow_raw.json"
JSON_FILENAME_GAMES_TODAY_PROCESSED = "nba_games_today_processed.json"
JSON_FILENAME_GAMES_ALL_RAW = "nba_games_all_raw.json"
JSON_FILENAME_GAMES_ALL_PROCESSED = "nba_games_all_processed.json"
JSON_FILENAME_GAMES_STATS_ALL_RAW = "nba_games_stats_all_raw.json"
JSON_FILENAME_GAMES_STATS_ALL_MERGED_PROCESSED = "nba_games_stats_all_merged_processed.json"
JSON_FILENAME_TEAM_GAMES_STATS_ALL_MERGED_PROCESSED = "nba_team_games_stats_all_merged_processed.json"
JSON_FILENAME_TEAM_GAMES_SEASON_STATS = "nba_team_games_season_stats.json"
JSON_FILENAME_TEAM_GAMES_L5_STATS = "nba_team_games_L5_stats.json"
JSON_FILENAME_TEAM_GAMES_H2H_STATS_RAW = "nba_team_games_H2H_stats_raw.json"
JSON_FILENAME_TEAM_GAMES_H2H_STATS_PROCESSED = "nba_team_games_H2H_stats_processed.json"
JSON_FILENAME_TEAM_GAMES_AGGREGATE_STATS_PROCESSED = "nba_team_games_aggregate_stats_processed.json"
JSON_FILENAME_TEAM_SEASON_PLAYERS_STATS_RAW = "nba_team_season_players_stats_raw.json"
JSON_FILENAME_PLAYER_INJURIES_TODAY_PROCESSED = "nba_player_injuries_today_processed.json"
JSON_FILENAME_TEAM_SEASON_PLAYERS_STATS_AGGREGATED = "nba_team_season_players_stats_aggregated.json"
JSON_FILENAME_TEAM_GAMES_INJURY_STATS_PROCESSED = "nba_team_games_injury_stats_processed.json"

# DATE = datetime.now().strftime("%Y-%m-%d")
# tomorrow_date = datetime.now() + timedelta(days=1)
# DATE_TOMORROW = tomorrow_date.strftime("%Y-%m-%d")

date = datetime.now() + timedelta(days=1)
DATE = date.strftime("%Y-%m-%d")
date_tomorrow = datetime.now() + timedelta(days=2)
DATE_TOMORROW = date_tomorrow.strftime("%Y-%m-%d")
def fetch_api_response(url, params={}):
    """Fetches games for a specific date.
    
    Args:
        date (str): The date for which to fetch games, in 'YYYY-MM-DD' format.
    
    Returns:
        dict: The JSON response containing game data.
    """
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")


def save_response_to_file(data, filename):
    """Saves API response data to a file.
    
    Args:
        data (dict): The data to save.
        filename (str): The filename for the saved data.
    """
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully saved to {filename}")
    except IOError as e:
        print(f"Failed to save file {filename}: {e}")

def load_json_from_file(filename):
    """Loads JSON data from a file.
    
    Args:
        filename (str): The filename to load data from.
    
    Returns:
        dict: The loaded JSON data.
    """
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except IOError as e:
        print(f"Failed to load file {filename}: {e}")
        return None

# Function to convert UTC to Eastern Time (automatically adjusting for EST/EDT)
def convert_to_est(date_str):
    utc_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    utc_date = utc_date.replace(tzinfo=pytz.UTC)  # Assign UTC timezone to the datetime object
    eastern_date = utc_date.astimezone(pytz.timezone('America/New_York'))  # Convert to Eastern Time
    return eastern_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z"  # Format back to a similar string format

# Function to get a flattened list of visitor and home ids
def get_flattened_ids(data):
    ids = []
    for game in data["game_details"].values():
        ids.extend([game["visitor"]["id"], game["home"]["id"]])
    return ids

def fetch_and_save_todays_raw_game_data(date=DATE, games_api_endpoint=GAMES_API_ENDPOINT, json_filename_games_today_raw=JSON_FILENAME_GAMES_TODAY_RAW, date_tomorrow=DATE_TOMORROW, json_filename_games_tomorrow_raw=JSON_FILENAME_GAMES_TOMORROW_RAW):
    """
    Fetches game data for today and tomorrow from a specified API and saves the data to files.
    
    :param date: The date for today's games.
    :param games_api_endpoint: The API endpoint for fetching game data.
    :param json_filename_games_today_raw: Filename for saving today's game data.
    :param date_tomorrow: The date for tomorrow's games.
    :param json_filename_games_tomorrow_raw: Filename for saving tomorrow's game data.
    """
    # Fetch and save today's game data
    querystring_today = {"date": date}
    today_response = fetch_api_response(games_api_endpoint, params=querystring_today)
    save_response_to_file(today_response, json_filename_games_today_raw)
    
    # Fetch and save tomorrow's game data
    querystring_tomorrow = {"date": date_tomorrow}
    tomorrow_response = fetch_api_response(games_api_endpoint, params=querystring_tomorrow)
    save_response_to_file(tomorrow_response, json_filename_games_tomorrow_raw)

def process_and_save_todays_raw_game_data(json_filename_games_today_processed=JSON_FILENAME_GAMES_TODAY_PROCESSED):
    """
    Processes game data to extract details for games on the current date and saves it to a file.

    :param data: The game data retrieved from the API.
    :param json_filename_games_today_processed: The filename for saving processed game data.
    """
    data = []
    data.append(load_json_from_file(JSON_FILENAME_GAMES_TODAY_RAW))
    data.append(load_json_from_file(JSON_FILENAME_GAMES_TOMORROW_RAW))
    game_details = {}

    # Extract the season from the first game in the response (assuming all games are from the same season)
    season = data[0]['response'][0]['season'] if data[0]['response'] else None

    # Iterate through each game in the response
    for file in data:
        for game in file['response']:
            # print (datetime.strptime(convert_to_est(game['date']['start']), "%Y-%m-%dT%H:%M:%S.%fZ").date())
            # print (datetime.utcnow().date())
            if datetime.strptime(convert_to_est(game['date']['start']), "%Y-%m-%dT%H:%M:%S.%fZ").date() == date.date():
                
                game_details[game['id']] = {
                    "start_time" : convert_to_est(game['date']['start']),
                    # Extract the visitor team ID
                    "visitor" : {"id":game['teams']['visitors']['id'],"name":game['teams']['visitors']['name']},
                    # Extract the home team ID
                    "home" :{"id":game['teams']['home']['id'],"name":game['teams']['home']['name']}
                }
                
        # # print (game_details)
        # # Prepare the data to be written to the file
        # data_to_write = {
        #     "season": season,
        #     "game_details": game_details
        # }

    # Prepare the data to be written to the file
    data_to_write = {
        "season": season,
        "game_details": game_details
    }

    # print(data_to_write)

    # Save processed game details to file
    save_response_to_file(data_to_write, json_filename_games_today_processed)

def fetch_and_save_all_raw_game_data():
    # Get all 2023 Season Games
    game_data_processed = load_json_from_file(JSON_FILENAME_GAMES_TODAY_PROCESSED)

    season = game_data_processed['season']
    team_ids = get_flattened_ids(game_data_processed)  # Flatten the list of team ID pairs

    # Initialize a dictionary to store all season games for each team
    all_season_games = {}

    # Prepare the querystring with the current team ID and season
    querystring = {"season": str(season)}
    
    # Perform the API call
    response = requests.get(GAMES_API_ENDPOINT, headers=HEADERS, params=querystring)
    

    if response.status_code == 200:
        # Store the response JSON in the all_season_games dictionary
        save_response_to_file(response.json(),JSON_FILENAME_GAMES_ALL_RAW )
        # print(response.json())
        print("All season games for each team successfully fetched and saved to all_season_games.json")
    else:
        print(f"Failed to fetch games : {response.status_code}")

#@!@#
def process_and_save_all_base_game_data():
    # Game Stats Table Loading

    # Load existing game stats from 'historical_combined_data.json'
    all_season_games = load_json_from_file(JSON_FILENAME_GAMES_ALL_RAW)['response']
    # print(len(all_season_games))
    # print(all_season_games.keys())

    # exit()

    allGamesStatsTable = {}

    for game in all_season_games:
        # print (len(all_season_games[game]["response"]))
        # count+=len(all_season_games[game]["response"])
        # print (all_season_games[game]["response"])
        if not(game["scores"]["home"]["points"] == 0 or 
            game["scores"]["visitors"]["points"] == None or
            game["scores"]["home"]["linescore"][0]=='' or
            game["scores"]["home"]["linescore"][1]=='' or
            game["scores"]["home"]["linescore"][2]=='' or
            game["scores"]["home"]["linescore"][3]==''
            ):
            if not(str(game["id"]) in allGamesStatsTable):
                # print (game['id'])
                # print(allGamesStatsTable[game['id'])
                allGamesStatsTable[game["id"]]={
                    "date":game["date"]["start"],
                    "homeID":game["teams"]["home"]["id"],
                    "homeName":game["teams"]["home"]["name"],
                    "homeScore":game["scores"]["home"]["points"],
                    "homeScoreQ1":int(game["scores"]["home"]["linescore"][0]),
                    "homeScoreQ2":int(game["scores"]["home"]["linescore"][1]),
                    "homeScoreQ3":int(game["scores"]["home"]["linescore"][2]),
                    "homeScoreQ4":int(game["scores"]["home"]["linescore"][3]),
                    "visitorID":game["teams"]["visitors"]["id"],
                    "visitorName":game["teams"]["visitors"]["name"],
                    "visitorScore":game["scores"]["visitors"]["points"],
                    "visitorScoreQ1":int(game["scores"]["visitors"]["linescore"][0]),
                    "visitorScoreQ2":int(game["scores"]["visitors"]["linescore"][1]),
                    "visitorScoreQ3":int(game["scores"]["visitors"]["linescore"][2]),
                    "visitorScoreQ4":int(game["scores"]["visitors"]["linescore"][3])
                    }
        #     if count == 3: break
        # break
    # print (allGamesTable.keys())
    # print (allGamesStatsTable)
    # Save the fetched all season games to a file for further analysis

    # Use the get_datetime function as the key for sorting
    sorted_allGamesStatsTable = dict(sorted(allGamesStatsTable.items(), key=get_datetime, reverse=True))

    save_response_to_file(sorted_allGamesStatsTable,JSON_FILENAME_GAMES_ALL_PROCESSED)

#@!@#
def process_and_save_all_raw_game_stat_data():

    # Load existing game stats from JSON_FILENAME_GAMES_ALL_PROCESSED
    allGamesTable = load_json_from_file(JSON_FILENAME_GAMES_ALL_PROCESSED)


    allGamesStatsTable = load_json_from_file(JSON_FILENAME_GAMES_STATS_ALL_RAW)
    if allGamesStatsTable == None:
        allGamesStatsTable = {}

    # print(allGamesTable)
    # print(allGamesStatsTable)

    # Define the rate limit
    requests_per_minute = 300
    seconds_per_minute = 60
    interval = seconds_per_minute / requests_per_minute
    iterationCount = 0
    # Iterate through each team ID
    for gameID in allGamesTable:
        if gameID not in allGamesStatsTable:
            # print(allGamesTable[gameID])
            # Prepare the querystring with the current team ID and season
            querystring = {"id": str(gameID)}

            # Perform the API call
            response = requests.get(GAMES_STATS_API_ENDPOINT, headers=HEADERS, params=querystring)
            
            if response.status_code == 200:
                # Store the response JSON in the all_season_games dictionary
                allGamesStatsTable[gameID] = response.json()
            else:
                print(f"Failed to fetch games for team ID {team_id}: {response.status_code}")
            
            # Pause execution to adhere to the rate limit
            time.sleep(interval)
            iterationCount+=1
        # break
    # print(allGamesStatsTable)

    save_response_to_file(allGamesStatsTable,JSON_FILENAME_GAMES_STATS_ALL_RAW)

def get_datetime(item):
    game_info = item[1]  # item[1] is the value part of the key-value pair in the dictionary
    # print(game_info)
    date_str = game_info['date']
    utc_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    utc_date = utc_date.replace(tzinfo=pytz.UTC)  # Set the timezone to UTC
    est_date = utc_date.astimezone(pytz.timezone('US/Eastern'))  # Convert to Eastern Time
    return est_date

def merge_process_and_save_all_raw_game_stat_data():
    all_games = load_json_from_file(JSON_FILENAME_GAMES_ALL_PROCESSED)

    all_stats = load_json_from_file(JSON_FILENAME_GAMES_STATS_ALL_RAW)
    games_all_raw = load_json_from_file(JSON_FILENAME_GAMES_ALL_RAW)['response']


    # print (len(all_games))
    # print (len(all_season_games))
    # print (all_games)
    for game in all_games:
        # print(all_stats[game]["response"][0]['statistics'])
        for stat in all_stats[game]["response"][0]['statistics'][0]:
            if all_stats[game]["response"][0]['statistics'][0][stat] != None:
                try:
                    all_games[game]["home"+stat] = float(all_stats[game]["response"][0]['statistics'][0][stat])
                    all_games[game]["visitor"+stat] = float(all_stats[game]["response"][1]['statistics'][0][stat])
                except ValueError:
                    print("Error: Could not convert string to float")
                # print (stat, all_stats[game]["response"][0]['statistics'][0][stat])
                # print (stat, all_stats[game]["response"][1]['statistics'][0][stat])
        # print (all_games[game])

    # print("all stats!!!!",all_stats)
    all_stats.update(all_games)
    

    game_id_date_mapping = {}

    for game in games_all_raw:
        game_id_date_mapping[game['id']]=game['date']['start']

    # Sort the dictionary by its keys
    # Sort the dictionary by its values (dates) in descending order
    sorted_dates_dict = dict(sorted(game_id_date_mapping.items(), key=lambda item: item[1], reverse=True))
    # print(all_stats)
    # Save the fetched all season games to a file for further analysis

    # print (sorted_all_stats)
    # print(games_all_raw)
    # print(sorted_dates_dict)
    # Update the 'date' in each game entry to Eastern Time
    for game_id, game_info in all_stats.items():
        game_info['date'] = convert_to_est(sorted_dates_dict[int(game_id)])

    for game_id,game_info in all_stats.items():
        # print(game_info)
        # Calculate FG% for home and visitor
        game_info['homeFG%'] = (game_info['homefgm'] / game_info['homefga']) * 100 if game_info['homefga'] != 0 else 0
        game_info['visitorFG%'] = (game_info['visitorfgm'] / game_info['visitorfga']) * 100 if game_info['visitorfga'] != 0 else 0
        
        # Calculate 3P% for home and visitor
        game_info['home3P%'] = (game_info['hometpm'] / game_info['hometpa']) * 100 if game_info['hometpa'] != 0 else 0
        game_info['visitor3P%'] = (game_info['visitortpm'] / game_info['visitortpa']) * 100 if game_info['visitortpa'] != 0 else 0
        
        # Calculate FT% for home and visitor
        game_info['homeFT%'] = (game_info['homeftm'] / game_info['homefta']) * 100 if game_info['homefta'] != 0 else 0
        game_info['visitorFT%'] = (game_info['visitorftm'] / game_info['visitorfta']) * 100 if game_info['visitorfta'] != 0 else 0
        
        # Calculate eFG% for home and visitor
        game_info['homeeFG%'] = ((game_info['homefgm'] + 0.5 * game_info['hometpm']) / game_info['homefga']) * 100 if game_info['homefga'] != 0 else 0
        game_info['visitoreFG%'] = ((game_info['visitorfgm'] + 0.5 * game_info['visitortpm']) / game_info['visitorfga']) * 100 if game_info['visitorfga'] != 0 else 0

        # FT/FGA (Draw Foul Rate) for both teams
        game_info['homeFT/FGA'] = game_info['homefta'] / game_info['homefga'] if game_info['homefga'] != 0 else 0
        game_info['visitorFT/FGA'] = game_info['visitorfta'] / game_info['visitorfga'] if game_info['visitorfga'] != 0 else 0
        
        # TS% (True Shooting Percentage) for both teams
        # Formula: (Points x 50) / [(FGA + 0.44 * FTA)]
        game_info['homeTS%'] = (game_info['homepoints'] * 50) / (game_info['homefga'] + 0.44 * game_info['homefta']) if (game_info['homefga'] + 0.44 * game_info['homefta']) != 0 else 0
        game_info['visitorTS%'] = (game_info['visitorpoints'] * 50) / (game_info['visitorfga'] + 0.44 * game_info['visitorfta']) if (game_info['visitorfga'] + 0.44 * game_info['visitorfta']) != 0 else 0

        # Determine outcomes for both home and visitor teams with binary values
        if game_info['visitorScore'] > game_info['homeScore']:
            game_info['visitorOutcome'] = 1  # Visitor win
            game_info['homeOutcome'] = 0  # Home loss
        else:
            game_info['visitorOutcome'] = 0  # Visitor loss
            game_info['homeOutcome'] = 1  # Home win
    # Check the updated dictionary for one of the games to see the calculated statistics
    # print(all_stats[next(iter(all_stats))])

    save_response_to_file(all_stats, JSON_FILENAME_GAMES_STATS_ALL_MERGED_PROCESSED)

# Function to convert UTC to Eastern Time (automatically adjusting for EST/EDT)
def convert_to_est(date_str):
    utc_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    utc_date = utc_date.replace(tzinfo=pytz.UTC)  # Assign UTC timezone to the datetime object
    eastern_date = utc_date.astimezone(pytz.timezone('America/New_York'))  # Convert to Eastern Time
    return eastern_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z"  # Format back to a similar string format

def group_and_save_processed_game_stat_data_by_team():
    todays_games = load_json_from_file(JSON_FILENAME_GAMES_TODAY_PROCESSED)
    team_stats = {}
    flattened_todays_games_teamIDs = []
    for game in todays_games['game_details']:
        flattened_todays_games_teamIDs.append(todays_games['game_details'][game]['visitor']['id'])
        flattened_todays_games_teamIDs.append(todays_games['game_details'][game]['home']['id']) 

    # print (flattened_todays_games_teamIDs)

    home_stats_keys = [
    "homeID", "homeScore", "homeScoreQ1", "homeScoreQ2", "homeScoreQ3", "homeScoreQ4", 
    "homepoints", "homefgm", "homefga", "homefgp", "homeftm", "homefta", "homeftp", "hometpm", 
    "hometpa", "hometpp", "homeoffReb", "homedefReb", "hometotReb", "homeassists", "homepFouls", 
    "homesteals", "hometurnovers", "homeblocks", "homeplusMinus", 
    "homeeFG%", "homeFT/FGA", "homeTS%"
    ]

    visitor_stats_keys = [
    "visitorID","visitorScore", "visitorScoreQ1", "visitorScoreQ2", "visitorScoreQ3", 
    "visitorScoreQ4", "visitorpoints", "visitorfgm", "visitorfga", "visitorfgp", "visitorftm", 
    "visitorfta", "visitorftp", "visitortpm", "visitortpa", "visitortpp", "visitoroffReb", 
    "visitordefReb", "visitortotReb", "visitorassists", "visitorpFouls", "visitorsteals", 
    "visitorturnovers", "visitorblocks", "visitorplusMinus", 
    "visitoreFG%", "visitorFT/FGA", "visitorTS%"
    ]

    all_stats = load_json_from_file(JSON_FILENAME_GAMES_STATS_ALL_MERGED_PROCESSED)
    for game in all_stats:
        # print (all_stats[game])
        # print(game)
        team_stats[all_stats[game]['homeID']] = {}
        team_stats[all_stats[game]['visitorID']] = {}
    for game in all_stats:
        team_stats[all_stats[game]['homeID']][game] = {}
        team_stats[all_stats[game]['visitorID']][game] = {}
        for key in home_stats_keys:
            if key != 'homeID':
                team_stats[all_stats[game]['homeID']][game][key.replace("home", "").replace("visitor", "")] = all_stats[game][key]
        for key in visitor_stats_keys:
            if key != 'visitorID':
                team_stats[all_stats[game]['visitorID']][game][key.replace("home", "").replace("visitor", "")] = all_stats[game][key]
        # break

    save_response_to_file(team_stats,JSON_FILENAME_TEAM_GAMES_STATS_ALL_MERGED_PROCESSED)

def process_season_stat_by_team():
    all_games_by_team = load_json_from_file(JSON_FILENAME_TEAM_GAMES_STATS_ALL_MERGED_PROCESSED)

    #season Stats

    season_stats = {}

    for team in all_games_by_team:
        stats = {
        "Score": 0, "ScoreQ1": 0, "ScoreQ2": 0, "ScoreQ3": 0, "ScoreQ4": 0, 
        "points": 0, "fgm": 0, "fga": 0, "fgp": 0, "ftm": 0, "fta": 0, "ftp": 0, "tpm": 0, 
        "tpa": 0, "tpp": 0, "offReb": 0, "defReb": 0, "totReb": 0, "assists": 0, "pFouls": 0, 
        "steals": 0, "turnovers": 0, "blocks": 0, "plusMinus": 0, "FG%": 0, "3P%": 0, "FT%": 0, 
        "eFG%": 0, "FT/FGA": 0, "TS%": 0
        }
        # print (all_games_by_team[team])
        for game in  (all_games_by_team[team]):
            # print(all_games_by_team[team][game])
            for key in all_games_by_team[team][game]:
                stats[key]+= all_games_by_team[team][game][key]

        for stat in stats:
            stats[stat]/=len(all_games_by_team[team])
        # print(stats)
        # print(len(all_games_by_team[team]))
        season_stats[team] = stats
    

    save_response_to_file(season_stats,JSON_FILENAME_TEAM_GAMES_SEASON_STATS)

def process_L5_stat_by_team():
    all_games_by_team = load_json_from_file(JSON_FILENAME_TEAM_GAMES_STATS_ALL_MERGED_PROCESSED)

    #Form/last 5

    season_stats = {}

    for team in all_games_by_team:
        stats = {
        "Score": 0, "ScoreQ1": 0, "ScoreQ2": 0, "ScoreQ3": 0, "ScoreQ4": 0, 
        "points": 0, "fgm": 0, "fga": 0, "fgp": 0, "ftm": 0, "fta": 0, "ftp": 0, "tpm": 0, 
        "tpa": 0, "tpp": 0, "offReb": 0, "defReb": 0, "totReb": 0, "assists": 0, "pFouls": 0, 
        "steals": 0, "turnovers": 0, "blocks": 0, "plusMinus": 0, "FG%": 0, "3P%": 0, "FT%": 0, 
        "eFG%": 0, "FT/FGA": 0, "TS%": 0
        }
        # print (all_games_by_team[team])
        # Ensure there are at least 5 games; if not, iterate over the available games.
        # Initialize a counter for iterations
        iterations = 0
        for game in all_games_by_team[team]:
            # print(all_games_by_team[team][game])
            for key in all_games_by_team[team][game]:
                stats[key]+= all_games_by_team[team][game][key]
            # Update the counter
            iterations += 1
            if iterations >= 5:
                break
        for stat in stats:
            stats[stat]/=5
        # print(stats)
        # print(len(all_games_by_team[team]))
        season_stats[team] = stats
    save_response_to_file(season_stats,JSON_FILENAME_TEAM_GAMES_L5_STATS)

def group_and_save_processed_h2h_stat_data_by_team():
    todays_games = load_json_from_file(JSON_FILENAME_GAMES_TODAY_PROCESSED)
    team_stats = {}
    flattened_todays_games_teamIDs = []
    for game in todays_games['game_details']:
        flattened_todays_games_teamIDs.append([todays_games['game_details'][game]['visitor']['id'],todays_games['game_details'][game]['home']['id']])
    
    sorted_flattened_todays_games_teamIDs = [sorted(inner) for inner in flattened_todays_games_teamIDs]
    # print (sorted_flattened_todays_games_teamIDs)

    home_stats_keys = [
    "homeID", "homeScore", "homeScoreQ1", "homeScoreQ2", "homeScoreQ3", "homeScoreQ4", 
    "homepoints", "homefgm", "homefga", "homefgp", "homeftm", "homefta", "homeftp", "hometpm", 
    "hometpa", "hometpp", "homeoffReb", "homedefReb", "hometotReb", "homeassists", "homepFouls", 
    "homesteals", "hometurnovers", "homeblocks", "homeplusMinus", "homeFG%", "home3P%", "homeFT%", 
    "homeeFG%", "homeFT/FGA", "homeTS%"
    ]

    visitor_stats_keys = [
    "visitorID","visitorScore", "visitorScoreQ1", "visitorScoreQ2", "visitorScoreQ3", 
    "visitorScoreQ4", "visitorpoints", "visitorfgm", "visitorfga", "visitorfgp", "visitorftm", 
    "visitorfta", "visitorftp", "visitortpm", "visitortpa", "visitortpp", "visitoroffReb", 
    "visitordefReb", "visitortotReb", "visitorassists", "visitorpFouls", "visitorsteals", 
    "visitorturnovers", "visitorblocks", "visitorplusMinus", "visitorFG%", "visitor3P%", "visitorFT%", 
    "visitoreFG%", "visitorFT/FGA", "visitorTS%"
    ]

    all_stats = load_json_from_file(JSON_FILENAME_GAMES_STATS_ALL_MERGED_PROCESSED)
    for game in all_stats:
        # print (all_stats[game])
        # print(game)
        game_teams = sorted([all_stats[game]['homeID'],all_stats[game]['visitorID']])


        if game_teams in sorted_flattened_todays_games_teamIDs:
            # print (game_teams)
            if not(all_stats[game]['homeID'] in team_stats):
                team_stats[all_stats[game]['homeID']] = {}
                # print (all_stats[game]['homeID'])
            if not(all_stats[game]['visitorID'] in team_stats):
                team_stats[all_stats[game]['visitorID']] = {}
                # print (all_stats[game]['visitorID'])
            # exit()
            team_stats[all_stats[game]['homeID']][game] = {}
            team_stats[all_stats[game]['visitorID']][game] = {}
            for key in home_stats_keys:
                if key != 'homeID':
                    team_stats[all_stats[game]['homeID']][game][key.replace("home", "").replace("visitor", "")] = all_stats[game][key]
            for key in visitor_stats_keys:
                if key != 'visitorID':
                    team_stats[all_stats[game]['visitorID']][game][key.replace("home", "").replace("visitor", "")] = all_stats[game][key]
        # break
    # print (team_stats)

    save_response_to_file(team_stats,JSON_FILENAME_TEAM_GAMES_H2H_STATS_RAW)

def process_H2H_stat_by_team():

    all_games_by_team=load_json_from_file(JSON_FILENAME_TEAM_GAMES_H2H_STATS_RAW)
     #H2H this season

    season_stats = {}

    for team in all_games_by_team:
        stats = {
        "Score": 0, "ScoreQ1": 0, "ScoreQ2": 0, "ScoreQ3": 0, "ScoreQ4": 0, 
        "points": 0, "fgm": 0, "fga": 0, "fgp": 0, "ftm": 0, "fta": 0, "ftp": 0, "tpm": 0, 
        "tpa": 0, "tpp": 0, "offReb": 0, "defReb": 0, "totReb": 0, "assists": 0, "pFouls": 0, 
        "steals": 0, "turnovers": 0, "blocks": 0, "plusMinus": 0, "FG%": 0, "3P%": 0, "FT%": 0, 
        "eFG%": 0, "FT/FGA": 0, "TS%": 0
        }
        # print (all_games_by_team[team])
        # Ensure there are at least 5 games; if not, iterate over the available games.
        # Initialize a counter for iterations
        iterations = 0
        for game in all_games_by_team[team]:
            # print(all_games_by_team[team][game])
            for key in all_games_by_team[team][game]:
                stats[key]+= all_games_by_team[team][game][key]
            # Update the counter
            iterations += 1
            if iterations >= 5:
                break
        for stat in stats:
            stats[stat]/= len(all_games_by_team[team])
        # print(stats)
        # print(len(all_games_by_team[team]))
        season_stats[team] = stats
    save_response_to_file(season_stats,JSON_FILENAME_TEAM_GAMES_H2H_STATS_PROCESSED)

def calculate_additional_stats(original_stats):
    updated_stats = {}
    # print(original_stats.keys())
    fgm = original_stats['fgm']
    fga = original_stats['fga']
    ftm = original_stats['ftm']
    fta = original_stats['fta']
    tpm = original_stats['tpm']
    tpa = original_stats['tpa']

    updated_stats = original_stats

    # Calculate eFG%
    updated_stats['eFG%'] = ((fgm + 0.5 * tpm) / fga * 100) if fga else 0

    # Calculate FT/FGA
    updated_stats['FT/FGA'] = (ftm  / fga ) if fga else 0

    # Calculate TS%
    updated_stats['TS%'] = (original_stats['points'] / (2 * (fga + 0.44 * fta)) * 100) if (fga + 0.44 * fta) else 0
    # print(updated_stats)
    return updated_stats



def process_injury_impacted_stats_by_team():
    # Initialize a dictionary to hold the sum of stats, excluding "min" and "totReb"
    stats = ['points', 'fgm', 'fga', 'ftm', 'fta', 'tpm', 'tpa', 'offReb', 'defReb', 'assists', 'pFouls', 'steals', 'turnovers', 'blocks', 'plusMinus']
    stats_processed_by_player = {}
    player_counts = {}
    team_sums = {}
    injured_players = load_json_from_file(JSON_FILENAME_PLAYER_INJURIES_TODAY_PROCESSED)
    team_stats_all = load_json_from_file(JSON_FILENAME_TEAM_SEASON_PLAYERS_STATS_RAW)
    # Iterate over each player's stats and sum them up
    for team in team_stats_all:
        if team in team_stats_all:
            stats_processed_by_player[team]={}
        team_sums[team]={}
        active_game_ids = []
        active_players = []

        for player_game in team_stats_all[team]:
            if not((player_game['player']['firstname']+" "+player_game['player']['lastname']) in stats_processed_by_player[team]):
                stats_processed_by_player[team][(player_game['player']['firstname']+" "+player_game['player']['lastname'])] = {}
                player_counts[(player_game['player']['firstname']+" "+player_game['player']['lastname'])] = 0
                if len(active_game_ids) < 3 and not(player_game['game']['id'] in active_game_ids):
                    # print(player_game['game']['id'])
                    active_game_ids.append(player_game['game']['id'])
            player_counts[(player_game['player']['firstname']+" "+player_game['player']['lastname'])] += 1
            # print(player_game)
            # print((player_game['player']['firstname']+" "+player_game['player']['lastname']))
                # print('hello', (player_game['player']['firstname']+" "+player_game['player']['lastname']))
            
            for key in stats:
                if player_game[key] == "--":
                    continue
                elif not(key in stats_processed_by_player[team][(player_game['player']['firstname']+" "+player_game['player']['lastname'])]):
                    stats_processed_by_player[team][(player_game['player']['firstname']+" "+player_game['player']['lastname'])][key] = int(player_game[key]) 
                else:
                    stats_processed_by_player[team][(player_game['player']['firstname']+" "+player_game['player']['lastname'])][key] += int(player_game[key])
        
            
            # print ((player_game['player']['firstname']+" "+player_game['player']['lastname']),player_game['game']['id'], active_game_ids)
            if player_game['game']['id'] in active_game_ids and not((player_game['player']['firstname']+" "+player_game['player']['lastname']) in active_players):
                active_players.append((player_game['player']['firstname']+" "+player_game['player']['lastname']))

        # print('\n\nactive game ids', active_game_ids)
        # print ('active players',active_players)
        # print ("\n\n\n",team)
        for player in stats_processed_by_player[team]:
            if not (player in active_players):
                continue
            # print(player in injured_players[team])
            # print(player, stats_processed_by_player[team][player])
            if team in injured_players and player in injured_players[team]: # and injured_players[player] == 0 or injured_players[player] == 2:
                # print(player)
                if injured_players[team][player] == 0:
                    # print(player, "out")
                    continue
                elif injured_players[team][player] == 2:
                    # print(player, "modified")
                    for key in stats:
                        stats_processed_by_player[team][player][key]/=player_counts[player]
                        # if key == 'points':
                            # print(player, "modified", stats_processed_by_player[team][player][key])
                        if not(key in team_sums[team]):
                            team_sums[team][key] = stats_processed_by_player[team][player][key]*.95
                        else:
                            team_sums[team][key] += stats_processed_by_player[team][player][key]*.95
                else:
                    for key in stats:
                        stats_processed_by_player[team][player][key]/=player_counts[player]
                        if not(key in team_sums[team]):
                            team_sums[team][key] = stats_processed_by_player[team][player][key]
                        else:
                            team_sums[team][key] += stats_processed_by_player[team][player][key]
                continue
            # print (player)
            for key in stats:
                stats_processed_by_player[team][player][key]/=player_counts[player]
                # if key == 'points':
                    # print(player, "normal", stats_processed_by_player[team][player][key])
                if not(key in team_sums[team]):
                    team_sums[team][key] = stats_processed_by_player[team][player][key]
                else:
                    team_sums[team][key] += stats_processed_by_player[team][player][key]

        # print(team_sums[team].keys())
        # print(team)
        team_sums[team] = calculate_additional_stats(team_sums[team])


        # print('team', team)
        # print('len',len(stats_processed_by_player[team]))
        # for key in stats:
        #     team_sums[team][key]/=len(stats_processed_by_player[team])
            # print (key,team_sums[team][key])

    # print(player_counts['Kevin Durant'])
    # print(stats_processed_by_player['10'])
    # print(team_sums)


    save_response_to_file(team_sums,JSON_FILENAME_TEAM_GAMES_INJURY_STATS_PROCESSED)

def calculate_rolling_stat_by_team():
    todays_games = load_json_from_file(JSON_FILENAME_GAMES_TODAY_PROCESSED)
    flattened_todays_games_teamIDs = []
    for game in todays_games['game_details']:
        flattened_todays_games_teamIDs.append(todays_games['game_details'][game]['visitor']['id'])
        flattened_todays_games_teamIDs.append(todays_games['game_details'][game]['home']['id']) 

    #calculate aggregate rolling stat
    stats_combined = {}
    stats_H2H = load_json_from_file(JSON_FILENAME_TEAM_GAMES_H2H_STATS_PROCESSED)
    stats_season = load_json_from_file(JSON_FILENAME_TEAM_GAMES_SEASON_STATS)
    stats_L5 = load_json_from_file(JSON_FILENAME_TEAM_GAMES_L5_STATS)
    stats_injury = load_json_from_file(JSON_FILENAME_TEAM_GAMES_INJURY_STATS_PROCESSED)
    first_key = next(iter(stats_H2H))
    omit_stat = ["Score","totReb","ScoreQ1","ScoreQ2","ScoreQ3","ScoreQ4"]
    stats_H2H_keys = stats_H2H[first_key].keys()
    partial_stat_keys = stats_injury[next(iter(stats_injury))].keys()
    full_stat_keys = stats_season[next(iter(stats_injury))].keys()
    

    # print(full_stat_keys)
    # print(partial_stat_keys)

    for team in flattened_todays_games_teamIDs:
        stats_combined[team] = {}
        # print (team)
        for stat in full_stat_keys:
            num_of_reference_games = 2
            # if stat in omit_stat:
            #     stats_combined[team][stat] = 0
            # print(stats_H2H[team])
            # print(stats_H2H_keys)
            # print (stat)
            stats_combined[team][stat]=stats_season[str(team)][stat]
            stats_combined[team][stat]+=stats_L5[str(team)][stat]
            if stat in partial_stat_keys:
                stats_combined[team][stat]+=stats_injury[str(team)][stat]
                num_of_reference_games+=1
            if team in stats_H2H:
                stats_combined[team][stat]+=stats_H2H[str(team)][stat]
                num_of_reference_games+=1
            # print (stat, stats_combined[team][stat])
            stats_combined[team][stat]/=num_of_reference_games
        # print("\n")
    # print(stats_combined)
        # exit()
    save_response_to_file(stats_combined,JSON_FILENAME_TEAM_GAMES_AGGREGATE_STATS_PROCESSED)

def predict_outcomes_by_team():
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score
    from sklearn.preprocessing import StandardScaler

    allGamesStatsTable=load_json_from_file(JSON_FILENAME_GAMES_STATS_ALL_MERGED_PROCESSED)

    # Convert the dictionary to a pandas DataFrame
    df = pd.DataFrame.from_dict(allGamesStatsTable, orient='index')

    # # Define the weight factor for the plusMinus feature
    # plusMinus_weight_factor = 100  # Example: making plusMinus 10 times more influential

    # # Apply the weight to the plusMinus features
    # df['homeplusMinus'] *= plusMinus_weight_factor
    # df['visitorplusMinus'] *= plusMinus_weight_factor

    # Features and target variable
    features = ['homefgm', 'visitorfgm', 'homefga', 'visitorfga',
                'homefgp', 'visitorfgp', 'homeftm', 'visitorftm', 'homefta', 'visitorfta',
                'hometpm', 'visitortpm', 'hometpa', 'visitortpa', 'homeoffReb', 'visitoroffReb',
                'homedefReb', 'visitordefReb', 'homeassists', 'visitorassists', 'homepFouls',
                'visitorpFouls', 'homesteals', 'visitorsteals', 'hometurnovers', 'visitorturnovers',
                'homeblocks', 'visitorblocks', 'homeplusMinus', 'visitorplusMinus', 
                'homeFT/FGA', 'visitorFT/FGA', 'homeTS%', 'visitorTS%']

    X = df[features]
    y = df[['homeOutcome','visitorOutcome']]

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Feature scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Initialize the logistic regression model
    base_lr = LogisticRegression(max_iter=1000)

    # Wrap the logistic regression model with MultiOutputClassifier
    model = MultiOutputClassifier(
        RandomForestClassifier(
            n_estimators=100,  # Adjusted to match best parameters
            max_depth=None,  # Allowing trees to grow as deep as necessary
            min_samples_split=4,  # As per best model parameters
            min_samples_leaf=2,  # As per best model parameters
            max_features='sqrt',  # Number of features to consider for the best split
            bootstrap=True,  # Whether bootstrap samples are used when building trees
            random_state=42  # Seed for the random number generator for reproducibility
        ),
        n_jobs=-1  # Use all processors for parallel computation
    )


    # Train the model on the scaled features and multi-label target
    model.fit(X_train_scaled, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test_scaled)
    for i, label in enumerate(y_test.columns):
        accuracy = accuracy_score(y_test[label], y_pred[:, i])
        print(f"Model Accuracy for {label}: {accuracy:.2%}")

    # Future game prediction part remains mostly the same, ensure to use best_model for predictions

    # exit()
    # Predicting a future game
    # Hypothetical future game features

    aggregate_stats = load_json_from_file(JSON_FILENAME_TEAM_GAMES_AGGREGATE_STATS_PROCESSED)
    game_data_processed = load_json_from_file(JSON_FILENAME_GAMES_TODAY_PROCESSED)

    todays_games = load_json_from_file(JSON_FILENAME_GAMES_TODAY_PROCESSED)
    flattened_todays_games_teamIDs = []
    flattened_todays_games_teamNames = {}
    for game in todays_games['game_details']:
        flattened_todays_games_teamIDs.append([todays_games['game_details'][game]['visitor']['id'],todays_games['game_details'][game]['home']['id']])
    # print(flattened_todays_games_teamIDs)

    for game in todays_games['game_details']:
        flattened_todays_games_teamNames[todays_games['game_details'][game]['home']['id']]=todays_games['game_details'][game]['home']['name']
        flattened_todays_games_teamNames[todays_games['game_details'][game]['visitor']['id']]=todays_games['game_details'][game]['visitor']['name']
    # print(flattened_todays_games_teamNames)

    for game_team_pair in flattened_todays_games_teamIDs:
        # print(flattened_todays_games_teamNames[game_team_pair[1]], game_team_pair[1])
        aggregate_stats[str(game_team_pair[1])]
        # print(aggregate_stats.keys())
        game_stats = {
            'homefgm': aggregate_stats[str(game_team_pair[1])]['fgm'],
            'visitorfgm': aggregate_stats[str(game_team_pair[0])]['fgm'],
            'homefga': aggregate_stats[str(game_team_pair[1])]['fga'],
            'visitorfga': aggregate_stats[str(game_team_pair[0])]['fga'],
            'homefgp': aggregate_stats[str(game_team_pair[1])]['fgp'],
            'visitorfgp': aggregate_stats[str(game_team_pair[0])]['fgp'],
            'homeftm': aggregate_stats[str(game_team_pair[1])]['ftm'],
            'visitorftm': aggregate_stats[str(game_team_pair[0])]['ftm'],
            'homefta': aggregate_stats[str(game_team_pair[1])]['fta'],
            'visitorfta': aggregate_stats[str(game_team_pair[0])]['fta'],
            'hometpm': aggregate_stats[str(game_team_pair[1])]['tpm'],
            'visitortpm': aggregate_stats[str(game_team_pair[0])]['tpm'],
            'hometpa': aggregate_stats[str(game_team_pair[1])]['tpa'],
            'visitortpa': aggregate_stats[str(game_team_pair[0])]['tpa'],
            'homeoffReb': aggregate_stats[str(game_team_pair[1])]['offReb'],
            'visitoroffReb': aggregate_stats[str(game_team_pair[0])]['offReb'],
            'homedefReb': aggregate_stats[str(game_team_pair[1])]['defReb'],
            'visitordefReb': aggregate_stats[str(game_team_pair[0])]['defReb'],
            'homeassists': aggregate_stats[str(game_team_pair[1])]['assists'],
            'visitorassists': aggregate_stats[str(game_team_pair[0])]['assists'],
            'homepFouls': aggregate_stats[str(game_team_pair[1])]['pFouls'],
            'visitorpFouls': aggregate_stats[str(game_team_pair[0])]['pFouls'],
            'homesteals': aggregate_stats[str(game_team_pair[1])]['steals'],
            'visitorsteals': aggregate_stats[str(game_team_pair[0])]['steals'],
            'hometurnovers': aggregate_stats[str(game_team_pair[1])]['turnovers'],
            'visitorturnovers': aggregate_stats[str(game_team_pair[0])]['turnovers'],
            'homeblocks': aggregate_stats[str(game_team_pair[1])]['blocks'],
            'visitorblocks': aggregate_stats[str(game_team_pair[0])]['blocks'],
            'homeplusMinus': aggregate_stats[str(game_team_pair[1])]['plusMinus'],
            'visitorplusMinus': aggregate_stats[str(game_team_pair[0])]['plusMinus'],
            'homeeFG%': aggregate_stats[str(game_team_pair[1])]['eFG%'],
            'visitoreFG%': aggregate_stats[str(game_team_pair[0])]['eFG%'],
            'homeFT/FGA': aggregate_stats[str(game_team_pair[1])]['FT/FGA'],
            'visitorFT/FGA': aggregate_stats[str(game_team_pair[0])]['FT/FGA'],
            'homeTS%': aggregate_stats[str(game_team_pair[1])]['TS%'],
            'visitorTS%': aggregate_stats[str(game_team_pair[0])]['TS%'],
        }

        # print(game_stats)
        # exit()

        future_game_features = pd.DataFrame([game_stats], columns=features)

        # Scale the features of the future game using the same scaler as the training data

        # Feature scaling
        future_game_scaled = scaler.transform(future_game_features)


        # Make prediction
        prediction = model.predict(future_game_scaled)
        prediction_proba = model.predict_proba(future_game_scaled)
        # Assuming 'prediction' is a 1D array with binary outcomes (1 for win, 0 for loss) for the first game
        # And 'prediction_proba' provides the probability of each class (loss, win)

        # Correctly access a scalar prediction value
        predicted_outcome = prediction[0]  # Ensure this is a scalar: 1 or 0

        print(predicted_outcome)

        # exit()
        # Determine the winning team based on the prediction
        winning_team = flattened_todays_games_teamNames[game_team_pair[1]] if predicted_outcome[0] == 1 else flattened_todays_games_teamNames[game_team_pair[0]]

        print(f"Predicted Outcome for the Home Team in the Future Game: Win, {winning_team}")

        # Print probability of [Loss, Win] for the first game
        print(f"Probability [Loss, Win]: {prediction_proba[0]}")

def get_start_by_id(data, search_id):
    # print(data)
    # print("game[id]",data['game']['id'])
    # print("search_id", search_id)
    if data['game']['id'] == search_id:
        # print("found")
        return game["date"]["start"]
    return None

def fetch_and_save_team_stats_raw():
    game_data_processed = load_json_from_file(JSON_FILENAME_GAMES_TODAY_PROCESSED)
    games_all_raw = load_json_from_file(JSON_FILENAME_GAMES_ALL_RAW)['response']

    season = game_data_processed['season']
    team_ids = get_flattened_ids(game_data_processed)  # Flatten the list of team ID pairs

    # print(team_ids)
  
    player_stats_all_teams_raw = {}
    game_id_date_mapping = {}

    for game in games_all_raw:
        game_id_date_mapping[game['id']]=game['date']['start']

    # Sort the dictionary by its keys
    # Sort the dictionary by its values (dates) in descending order
    sorted_dates_dict = dict(sorted(game_id_date_mapping.items(), key=lambda item: item[1], reverse=True))

    # print(sorted_dates_dict)

    for team in team_ids:
        # Prepare the querystring with the current team ID and season
        querystring = {"season": str(season),"team":team}
        # Perform the API call
        # player_stats_all_teams_raw_full[team]= fetch_api_response(TEAM_PLAYER_STATS_API_ENDPOINT, params=querystring)
        player_stats_all_teams_raw[team] = fetch_api_response(TEAM_PLAYER_STATS_API_ENDPOINT, params=querystring)['response']
        #@!@#

        for player_game in player_stats_all_teams_raw[team]:
            player_game['date'] = sorted_dates_dict[player_game['game']['id']]
            # print(games_all_raw['team'])
            # start_date = get_start_by_id(games_all_raw,player_game['game']['id'])
            # print(start_date)
            # print('!!!!!!!!!!!!!', start_dates)
            # player_stats_all_teams_raw[team]['date'] 
            ###Need to sort data by date

        player_stats_all_teams_raw[team] = sorted(player_stats_all_teams_raw[team], key=lambda x: x['date'], reverse=True)


        # sorted_all_allGamesStatsTable = dict(sorted(allGamesStatsTable.items(), key=get_datetime, reverse=True))


    save_response_to_file(player_stats_all_teams_raw,JSON_FILENAME_TEAM_SEASON_PLAYERS_STATS_RAW)

def fetch_process_and_save_player_injuries_by_team():
    # URL of the page to fetch
    url = "https://www.basketball-reference.com/friv/injuries.cgi"
    todays_games = load_json_from_file(JSON_FILENAME_GAMES_TODAY_PROCESSED)

    flattened_todays_games_teamNames = {}

    for game in todays_games['game_details']:
        flattened_todays_games_teamNames[todays_games['game_details'][game]['home']['name']] = todays_games['game_details'][game]['home']['id']
        flattened_todays_games_teamNames[todays_games['game_details'][game]['visitor']['name']] = todays_games['game_details'][game]['visitor']['id']
    
    # print(flattened_todays_games_teamNames)

    # Fetch the page content
    response = requests.get(url)
    html_content = response.text

    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Assuming the table of interest is the first one on the page.
    # You might need to adjust this to find the correct table, e.g., by using an ID or class.
    table = soup.find('table')

    # Extract data from the table
    data = {}

    # Iterate through each row in the table, skipping the header row
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('a')
        playerName = unidecode(cols[0].text.strip())
        cols = row.find_all('td')
        # print(cols)
        if not(cols[0].text.strip() in flattened_todays_games_teamNames):
            # print(not(cols[0].text.strip() in flattened_todays_games_teamNames))
            # print(cols[0].text.strip())
            continue
        teamName = flattened_todays_games_teamNames[cols[0].text.strip()]
        if teamName == 'Los Angeles Clippers':
            teamName = 'LA Clippers'
        # print(teamName)
        updateDate = cols[1].text.strip()
        description = cols[2].text.strip()
        if 'Out' in description:
            description = 0
        elif 'Day To Day' in description:
            description = 2
        else:
            description = 1
        
        if cols:  # Check if row is not empty
            item = description

        if not(teamName in data):
            data[teamName] = {}
        data[teamName][playerName] = item

    # Output or save the JSON data
    save_response_to_file(data,JSON_FILENAME_PLAYER_INJURIES_TODAY_PROCESSED)

if __name__ == "__main__":

    # fetch_and_save_todays_raw_game_data()
    # process_and_save_todays_raw_game_data()
    # fetch_and_save_all_raw_game_data()
    # process_and_save_all_base_game_data()
    # process_and_save_all_raw_game_stat_data()
    # merge_process_and_save_all_raw_game_stat_data()
    # fetch_and_save_team_stats_raw()
    # fetch_process_and_save_player_injuries_by_team()
    # group_and_save_processed_game_stat_data_by_team()
    # process_season_stat_by_team()
    # process_L5_stat_by_team()
    # group_and_save_processed_h2h_stat_data_by_team()
    # process_H2H_stat_by_team()
    # process_injury_impacted_stats_by_team()
    # calculate_rolling_stat_by_team()
    predict_outcomes_by_team()
    
    #rolling stats for prediction
    #season Stats
    #Form/last 5
    #last 3 head to head
    # Additional Considerations
    # Home vs. Away Performance: Teams often perform differently at home compared to on the road.
    # Considering the venue of the next game can add valuable context to your analysis.

    # Strength of Schedule: The difficulty of recent opponents can influence recent form.
    # Adjusting for the strength of schedule can provide a more accurate picture of a team's performance.


    # # Home and Away Records this season
    # # Offensive and Defensive Ratings, Team Efficiency Statistics: Update after every game. 
    # # Recent Form (Last 5-10 games performance): Update continuously, recalculating after each game.
    # # Head-to-Head Records against Opponents: Update after every game that involves the teams in question.

    # 2. Player Data
    # Player Statistics, Player Efficiency Rating (PER), Win Shares, Plus/Minus Statistics: Update after every game.
    # Injury Status and History: Check daily, especially close to game time, as injury reports can change rapidly.
    # Minutes Played (Season and Recent Games): Update after every game.

    # 3. Game Data
    # Game ID, Date and Time, Venue, Referee Assignments, Team Match-up Information, Historical Game Outcomes: These are set before the season or specific game and change only if there are scheduling adjustments.
    # Vegas Odds (Betting Lines, Over/Under): Check daily, as odds can fluctuate based on many factors, including player injuries and betting trends.
    # Player Match-ups: Evaluate within 24-48 hours before the game, considering the latest injury reports and team announcements.

    # 4. Advanced Metrics and Analytics
    # Update after every game: As these metrics depend on player and team performances, they should be recalculated after each game to reflect the most current data.

    # 5. Contextual and External Factors
    # Travel Schedule and Rest Days: Known in advance, but assess the impact closer to the game date.
    # Altitude of Venue, Player Trades and Transactions, Team Morale and Media Reports, Fan Attendance: Review these factors within 1-2 days before the game as they can have immediate effects.
    # Weather Conditions: Check within 24 hours of the game, especially for outdoor venues or potential travel delays.

    # 6. Miscellaneous Data
    # Coaching Staff and Style, Playoff Standings and Implications, Team Strategy and Play Types, In-season Changes: While some of these factors are static or change infrequently, staying updated on news and team reports is crucial, especially close to game time.
    # Social Media Sentiment Analysis: Perform this analysis 1-2 days before the game to gauge the latest public sentiment and potential impact on team performance.

    #Dataset Preparation
    # exit()

    