import requests
import json

# 1. Schedule Data - Get Teams Playing
	

# season = "2023"
# dateYear = "2024"
# dateMonth = "03"
# dateDay = "05"

# url = "https://api-nba-v1.p.rapidapi.com/games"

# querystring = {"date":dateYear+"-"+dateMonth+"-"+dateDay}
# print(querystring)

# headers = {
# 	"X-RapidAPI-Key": "f8439d4381msh236d31535d6c16dp15e6c6jsn4ab1fe08eda9",
# 	"X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
# }

# response = requests.get(url, headers=headers, params=querystring)
# # Ensure the directory where you're writing this file has write permissions
# # and the path is accessible from your script.
# # It's also good practice to handle potential errors such as request failures.
# if response.status_code == 200:
#     # Open a file to write (this will overwrite existing files)
#     with open('nba_games_response.json', 'w') as file:
#         file.write(response.text)  # Write the response text (JSON data) to the file
#     print("Response written to nba_games_response.json")
# else:
#     print(f"Failed to fetch data: {response.status_code}")


# Specify the path to your JSON file
file_path = 'nba_games_response.json'

# Open the file for reading
with open(file_path, 'r') as file:
    # Load the JSON content from the file
    data = json.load(file)

# Assuming 'data' contains the JSON data as shown above

# team_ids = []

# # Extract the season from the first game in the response (assuming all games are from the same season)
# season = data['response'][0]['season'] if data['response'] else None

# # Iterate through each game in the response
# for game in data['response']:
#     # Extract the visitor team ID
#     visitor_id = game['teams']['visitors']['id']
#     # Extract the home team ID
#     home_id = game['teams']['home']['id']
    
#     # Append both IDs to the team_ids list
#     team_ids.append((visitor_id, home_id))

# # Prepare the data to be written to the file
# data_to_write = {
#     "season": season,
#     "team_ids": team_ids
# }

# Assuming the file 'nba_season_team_ids.json' has been loaded correctly
# Load the season and team IDs from the JSON file

###
###
###
###
###
###	

import time

# Get all Season Games per Team
with open('nba_season_team_ids.json', 'r') as file:
    data = json.load(file)

season = data['season']
team_ids = [team_id for pair in data['team_ids'] for team_id in pair]  # Flatten the list of team ID pairs

# # Headers for the API request
# headers = {
#     "X-RapidAPI-Key": "f8439d4381msh236d31535d6c16dp15e6c6jsn4ab1fe08eda9",
#     "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
# }

# # Base URL for the API request
# url = "https://api-nba-v1.p.rapidapi.com/games"

# # Initialize a dictionary to store all season games for each team
# all_season_games = {}

# # Define the rate limit
# requests_per_minute = 10
# seconds_per_minute = 60
# interval = seconds_per_minute / requests_per_minute

# # Iterate through each team ID
# for team_id in team_ids:
#     # Prepare the querystring with the current team ID and season
#     querystring = {"season": str(season), "team": str(team_id)}
    
#     # Perform the API call
#     response = requests.get(url, headers=headers, params=querystring)
    
#     if response.status_code == 200:
#         # Store the response JSON in the all_season_games dictionary
#         all_season_games[team_id] = response.json()
#     else:
#         print(f"Failed to fetch games for team ID {team_id}: {response.status_code}")
    
#     # Pause execution to adhere to the rate limit
#     time.sleep(interval)

# # Save the fetched all season games to a file for further analysis
# with open('all_season_games.json', 'w') as outfile:
#     json.dump(all_season_games, outfile, indent=4)


# print("All season games for each team successfully fetched and saved to all_season_games.json")
###
###
###
###
###
###
# Home and Away Records this season

# # Load team information from 'nba_teams_only.json'
# with open('nba_teams_only.json', 'r') as file:
#     nba_teams = json.load(file)
# team_id_to_city = {team["id"]: team["city"] for team in nba_teams}

# # print (team_id_to_city)

# # Load all season games for each team from 'all_season_games.json'
# with open('all_season_games.json', 'r') as file:
#     all_season_games = json.load(file)

# # Initialize a dictionary for home and away records
# home_away_records = {}

# # Process games to identify home and away records
# for team_id, games in all_season_games.items():
#     # Initialize record keeping for each team
#     if team_id not in home_away_records:
#         home_away_records[team_id] = {'home_wins': 0, 'home_losses': 0, 'away_wins': 0, 'away_losses': 0}

#     for game in games['response']:
#         # Identify if it's a home game by comparing arena city with team city
#         is_home_game = game['arena']['city'] == team_id_to_city[int(team_id)]
#         if (game['scores']['home']['points']==None):continue
#         home_team_won = game['scores']['home']['points'] > game['scores']['visitors']['points']
        
#         # Update records based on game outcome and whether it's home/away
#         if is_home_game:
#             if home_team_won:
#                 home_away_records[team_id]['home_wins'] += 1
#             else:
#                 home_away_records[team_id]['home_losses'] += 1
#         else:
#             if not home_team_won:
#                 home_away_records[team_id]['away_wins'] += 1
#             else:
#                 home_away_records[team_id]['away_losses'] += 1

# # Save the home and away records to a file
# with open('home_away_records.json', 'w') as outfile:
#     json.dump(home_away_records, outfile, indent=4)

# print("Home and away records have been calculated and saved.")

#Offensive and Defensive Ratings, Team Efficiency Statistics: Update after every game. 


# Load the game data from the JSON
with open('all_season_games.json', 'r') as file:
    games_data = json.load(file)
# print(games_data)

ratings = {}
# Define the team ID for which you want to calculate the ratings
# team_id = 19  # Example team ID (Memphis Grizzlies)
for team_id in team_ids:

    # Initialize variables to store offensive and defensive statistics
    offensive_rating = 0
    defensive_rating = 0
    total_points_scored = 0
    total_points_allowed = 0

    # Iterate through each game in the response

    for team in games_data: #keyError: 19
        # print (games_data)
        for game in games_data[str(team)]["response"]:
            # print(game)
            # Extract the scores for the team in the game
            team_scores = game["scores"]["home"] if game["teams"]["home"]["id"] == team_id else game["scores"]["visitors"] #TypeError: string indices must be integers, not 'str'
            
            # Extract the points scored and allowed by the team
            if (game['scores']['home']['points']==None):continue
            points_scored = int(team_scores["points"])
            points_allowed = int(game["scores"]["visitors"]["points"]) if game["teams"]["home"]["id"] == team_id else int(game["scores"]["home"]["points"])
            
            # Calculate the total points scored and allowed
            total_points_scored += points_scored
            total_points_allowed += points_allowed

        # Calculate Offensive Rating (ORtg) and Defensive Rating (DRtg)
        offensive_rating = total_points_scored / len(games_data[str(team)]["response"])
        defensive_rating = total_points_allowed / len(games_data[str(team)]["response"])

        # Create a dictionary to store the ratings
        if (team_id in team_ids):
            ratings[team_id] = {
                "team_id": team_id,
                "offensive_rating": offensive_rating,
                "defensive_rating": defensive_rating
            }

# Save the ratings to a file
with open('ratings.json', 'w') as outfile:
    json.dump(ratings, outfile, indent=4)

print("Ratings saved to ratings.json")


# Recent Form (Last 5-10 games performance): Update continuously, recalculating after each game.
# Head-to-Head Records against Opponents: Update after every game that involves the teams in question.

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