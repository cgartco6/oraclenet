import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import sqlite3
from datetime import datetime, timedelta

class SIOrchestrator:
    def __init__(self):
        self.model_1x2 = None
        self.model_btts = None

    def train_models(self, data):
        """
        Train models for 1X2 (Win/Draw) and BTTS (Both Teams to Score)
        """
        # Feature Engineering (Simplified for example)
        data['home_form'] = data['home_goals_scored'] - data['home_goals_conceded']
        data['away_form'] = data['away_goals_scored'] - data['away_goals_conceded']
        features = ['home_form', 'away_form', 'home_win_rate', 'away_win_rate', 'avg_corners']

        # Prepare 1X2 Model
        X = data[features]
        y_1x2 = data['result']  # 'H', 'D', 'A'
        X_train, X_test, y_train, y_test = train_test_split(X, y_1x2, test_size=0.2)
        self.model_1x2 = GradientBoostingClassifier()
        self.model_1x2.fit(X_train, y_train)
        print(f"1X2 Model Accuracy: {accuracy_score(y_test, self.model_1x2.predict(X_test))}")

        # Prepare BTTS Model
        y_btts = data['btts']  # 1 for Yes, 0 for No
        X_train, X_test, y_train, y_test = train_test_split(X, y_btts, test_size=0.2)
        self.model_btts = GradientBoostingClassifier()
        self.model_btts.fit(X_train, y_train)
        print(f"BTTS Model Accuracy: {accuracy_score(y_test, self.model_btts.predict(X_test))}")

        # Save models
        joblib.dump(self.model_1x2, '../data/models/model_1x2.joblib')
        joblib.dump(self.model_btts, '../data/models/model_btts.joblib')

    def predict_todays_games(self, today_data):
        """
        Predict today's games and return a DataFrame with predictions.
        """
        # Load models (if not already loaded)
        if not self.model_1x2:
            self.model_1x2 = joblib.load('../data/models/model_1x2.joblib')
        if not self.model_btts:
            self.model_btts = joblib.load('../data/models/model_btts.joblib')

        # Feature engineering for today's data
        today_data['home_form'] = today_data['home_goals_scored'] - today_data['home_goals_conceded']
        today_data['away_form'] = today_data['away_goals_scored'] - today_data['away_goals_conceded']
        features = ['home_form', 'away_form', 'home_win_rate', 'away_win_rate', 'avg_corners']

        # Make predictions
        X_today = today_data[features]
        predictions_1x2 = self.model_1x2.predict(X_today)
        probas_1x2 = self.model_1x2.predict_proba(X_today)
        predictions_btts = self.model_btts.predict(X_today)
        probas_btts = self.model_btts.predict_proba(X_today)

        # Create results DataFrame
        results_df = today_data[['home_team', 'away_team']].copy()
        results_df['predicted_result'] = predictions_1x2
        results_df['result_confidence'] = [max(proba) for proba in probas_1x2]
        results_df['predicted_btts'] = ['Yes' if pred == 1 else 'No' for pred in predictions_btts]
        results_df['btts_confidence'] = [max(proba) for proba in probas_btts]

        # Calculate combined confidence for "Win & BTTS" etc.
        return results_df

# Example usage
if __name__ == '__main__':
    si = SIOrchestrator()
    # si.train_models(historical_data_df) # Run this first with historical data
    todays_fixtures = pd.read_csv('../data/processed/todays_fixtures.csv')
    predictions = si.predict_todays_games(todays_fixtures)
    print(predictions[['home_team', 'away_team', 'predicted_result', 'predicted_btts']])
    predictions.to_csv('../data/predictions/todays_predictions.csv', index=False)
