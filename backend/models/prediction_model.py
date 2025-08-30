import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import logging
import os

class PredictionModel:
    def __init__(self):
        self.model = None
        self.load_model()
        
    def load_model(self):
        """Load trained model from file"""
        try:
            model_path = os.path.join(os.path.dirname(__file__), '../../data/models/model.pkl')
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                logging.info("Model loaded successfully")
            else:
                logging.warning("No trained model found. Using default predictions.")
        except Exception as e:
            logging.error(f"Error loading model: {str(e)}")
    
    def predict_match(self, home_team, away_team, league=None):
        """Predict match outcome"""
        try:
            # If we have a trained model, use it
            if self.model:
                # Prepare features for prediction
                features = self._prepare_features(home_team, away_team, league)
                prediction = self.model.predict_proba(features)[0]
                
                return {
                    "home_win_prob": float(prediction[0]),
                    "draw_prob": float(prediction[1]),
                    "away_win_prob": float(prediction[2]),
                    "predicted_result": ["home_win", "draw", "away_win"][np.argmax(prediction)],
                    "confidence": float(np.max(prediction))
                }
            else:
                # Fallback to simple prediction based on team names
                return self._simple_prediction(home_team, away_team)
        except Exception as e:
            logging.error(f"Error predicting match: {str(e)}")
            return self._simple_prediction(home_team, away_team)
    
    def _prepare_features(self, home_team, away_team, league):
        """Prepare features for model prediction"""
        # This would extract features from historical data
        # For now, return dummy features
        return np.array([[0.5, 0.3, 0.7, 0.4, 0.6]])  # Example features
    
    def _simple_prediction(self, home_team, away_team):
        """Simple fallback prediction based on team names"""
        # Simple heuristic for demonstration
        home_score = sum(ord(c) for c in home_team) % 10 * 0.1
        away_score = sum(ord(c) for c in away_team) % 10 * 0.1
        
        total = home_score + away_score
        if total == 0:
            home_win_prob = 0.33
            draw_prob = 0.34
            away_win_prob = 0.33
        else:
            home_win_prob = home_score / total * 0.9
            away_win_prob = away_score / total * 0.9
            draw_prob = 1 - home_win_prob - away_win_prob
        
        return {
            "home_win_prob": home_win_prob,
            "draw_prob": draw_prob,
            "away_win_prob": away_win_prob,
            "predicted_result": "home_win" if home_win_prob > away_win_prob and home_win_prob > draw_prob else 
                              "away_win" if away_win_prob > home_win_prob and away_win_prob > draw_prob else "draw",
            "confidence": max(home_win_prob, draw_prob, away_win_prob)
        }
