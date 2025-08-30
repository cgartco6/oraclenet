from flask import Flask, jsonify, request
from flask_cors import CORS
from services.data_collector import DataCollector
from services.odds_comparator import OddsComparator
from models.prediction_model import PredictionModel
import logging
from datetime import datetime, timedelta
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize components
data_collector = DataCollector()
odds_comparator = OddsComparator()
prediction_model = PredictionModel()

@app.route('/')
def home():
    return jsonify({"message": "OracleNet API is running", "status": "success"})

@app.route('/api/today-matches')
def get_today_matches():
    try:
        # Get today's matches from data collector
        matches = data_collector.get_todays_matches()
        
        # Get predictions for each match
        for match in matches:
            prediction = prediction_model.predict_match(
                match['home_team'], 
                match['away_team'],
                match['league']
            )
            match['prediction'] = prediction
            
            # Get odds comparison
            match['odds_comparison'] = odds_comparator.get_odds(
                match['home_team'], 
                match['away_team']
            )
        
        return jsonify({
            "status": "success",
            "data": matches,
            "last_updated": datetime.now().isoformat()
        })
    except Exception as e:
        logging.error(f"Error fetching today's matches: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/predict-match')
def predict_match():
    try:
        home_team = request.args.get('home_team')
        away_team = request.args.get('away_team')
        league = request.args.get('league')
        
        if not home_team or not away_team:
            return jsonify({"status": "error", "message": "home_team and away_team parameters are required"})
        
        prediction = prediction_model.predict_match(home_team, away_team, league)
        
        return jsonify({
            "status": "success",
            "data": prediction,
            "teams": f"{home_team} vs {away_team}"
        })
    except Exception as e:
        logging.error(f"Error predicting match: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/leagues')
def get_leagues():
    try:
        leagues = data_collector.get_supported_leagues()
        return jsonify({
            "status": "success",
            "data": leagues
        })
    except Exception as e:
        logging.error(f"Error fetching leagues: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
