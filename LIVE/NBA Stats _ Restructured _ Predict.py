import requests
import json
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
import numpy as np


# Constants for API access
API_KEY = "your_api_key"
API_HOST = "api-nba-v1.p.rapidapi.com"
HEADERS = {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": API_HOST}

# JSON filename for processed game stats
JSON_FILENAME_GAMES_STATS_ALL_MERGED_PROCESSED = "nba_games_stats_all_merged_processed.json"

def load_json_from_file(filename):
    """Load JSON data from a file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except IOError as e:
        print(f"Failed to load file {filename}: {e}")
        return None

def predict_outcomes_by_team():
    # Load and preprocess the dataset
    dataset = load_json_from_file(JSON_FILENAME_GAMES_STATS_ALL_MERGED_PROCESSED)
    # Flatten the nested dictionary structure
    flattened_data = {}
    features = ['homefgm', 'visitorfgm', 'homefga', 'visitorfga', 'homefgp', 'visitorfgp', 'homeftm',
                    'visitorftm', 'homefta', 'visitorfta', 'hometpm', 'visitortpm', 'hometpa', 'visitortpa',
                    'homeoffReb', 'visitoroffReb', 'homedefReb', 'visitordefReb', 'homeassists', 'visitorassists',
                    'homepFouls', 'visitorpFouls', 'homesteals', 'visitorsteals', 'hometurnovers', 'visitorturnovers',
                    'homeblocks', 'visitorblocks', 'homeplusMinus', 'visitorplusMinus', 'homeeFG%', 'visitoreFG%',
                    'homeFT/FGA', 'visitorFT/FGA', 'homeTS%', 'visitorTS%',"visitorOutcome","homeOutcome"]
    
    for game_id, game in dataset.items():
        for key in features:
            if not(key in flattened_data):
                flattened_data[key] =[]
            # Add team_id and game_id to the stats
            flattened_data[key].append(game[key])

    # Create DataFrame
    df = pd.DataFrame(flattened_data)

    # df = df.drop(['Score', 'ScoreQ1', 'ScoreQ2', 'ScoreQ3', 'ScoreQ4'], axis=1) 

    print(df)
    # Define features and target variables
    features = ['homefgm', 'visitorfgm', 'homefga', 'visitorfga', 'homefgp', 'visitorfgp', 'homeftm',
                'visitorftm', 'homefta', 'visitorfta', 'hometpm', 'visitortpm', 'hometpa', 'visitortpa',
                'homeoffReb', 'visitoroffReb', 'homedefReb', 'visitordefReb', 'homeassists', 'visitorassists',
                'homepFouls', 'visitorpFouls', 'homesteals', 'visitorsteals', 'hometurnovers', 'visitorturnovers',
                'homeblocks', 'visitorblocks', 'homeplusMinus', 'visitorplusMinus', 'homeeFG%', 'visitoreFG%',
                'homeFT/FGA', 'visitorFT/FGA', 'homeTS%', 'visitorTS%']
    X = df[features]
    # # Prepare your feature set; now including the '_weighted' features
    # weighted_features = [f"{feature}_weighted" for feature in features]

    # X = df[weighted_features]
    y = df[['homeOutcome', 'visitorOutcome']]

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale the feature data
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

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

    model.fit(X_train_scaled, y_train)

    # # Evaluate the model
    # y_pred = model.predict(X_test_scaled)
    # accuracy = accuracy_score(y_test, y_pred)
    # print(f"Accuracy: {accuracy}")
    
    # Perform cross-validation
    cv_scores = cross_val_score(model, X, y, cv=5)  # 5-fold cross-validation

    # Print cross-validation scores
    print(f"CV Scores: {cv_scores}")
    print(f"Average CV Score: {np.mean(cv_scores)}")

    param_grid = {
        'estimator__n_estimators': [100, 200, 300],
        'estimator__max_depth': [None, 10, 20, 30]
    }
    grid_search = GridSearchCV(model, param_grid=param_grid, cv=5, scoring='accuracy', n_jobs=-1)
    grid_search.fit(X_train_scaled, y_train)

    # Output the best model
    best_model = grid_search.best_estimator_
    print(f"Best model parameters: {best_model.get_params()}")

if __name__ == "__main__":
    predict_outcomes_by_team()
