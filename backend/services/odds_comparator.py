import requests
from bs4 import BeautifulSoup
import json
import re
import logging

class OddsComparator:
    def __init__(self):
        self.hollywoodbets_url = "https://www.hollywoodbets.net"
        self.betway_url = "https://www.betway.co.za"
        
    def get_odds(self, home_team, away_team):
        """Get odds from different bookmakers for a match"""
        try:
            # In a real implementation, this would scrape or use APIs
            # to get odds from Hollywoodbets and Betway
            
            # For demonstration, return mock odds
            return self._get_mock_odds(home_team, away_team)
        except Exception as e:
            logging.error(f"Error getting odds: {str(e)}")
            return self._get_mock_odds(home_team, away_team)
    
    def _get_mock_odds(self, home_team, away_team):
        """Mock function for odds - replace with real scraping/API calls"""
        return {
            "hollywoodbets": {
                "home_win": 2.10,
                "draw": 3.20,
                "away_win": 3.50,
                "btts_yes": 1.90,
                "btts_no": 1.80,
                "over_2.5": 2.05,
                "under_2.5": 1.75
            },
            "betway": {
                "home_win": 2.05,
                "draw": 3.25,
                "away_win": 3.60,
                "btts_yes": 1.85,
                "btts_no": 1.85,
                "over_2.5": 2.10,
                "under_2.5": 1.70
            },
            "match": f"{home_team} vs {away_team}"
        }
    
    def find_value_bets(self, predictions, threshold=0.05):
        """Find value bets based on predictions and odds"""
        value_bets = []
        
        for prediction in predictions:
            odds = self.get_odds(prediction['home_team'], prediction['away_team'])
            implied_prob = {
                'home_win': 1 / odds['hollywoodbets']['home_win'],
                'draw': 1 / odds['hollywoodbets']['draw'],
                'away_win': 1 / odds['hollywoodbets']['away_win']
            }
            
            # Calculate value (prediction probability - implied probability)
            if prediction['prediction']['home_win_prob'] > implied_prob['home_win'] + threshold:
                value_bets.append({
                    'type': 'home_win',
                    'team': prediction['home_team'],
                    'odds': odds['hollywoodbets']['home_win'],
                    'predicted_prob': prediction['prediction']['home_win_prob'],
                    'implied_prob': implied_prob['home_win'],
                    'value': prediction['prediction']['home_win_prob'] - implied_prob['home_win']
                })
                
            # Similar logic for draw and away_win
            
        return value_bets
