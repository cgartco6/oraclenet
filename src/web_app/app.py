from flask import Flask, render_template
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Load today's predictions
    try:
        df = pd.read_csv('../data/predictions/todays_predictions.csv')
        # Convert DataFrame to list of dictionaries for the template
        predictions = df.to_dict('records')
    except FileNotFoundError:
        predictions = []

    # Pass the list to the template
    return render_template('index.html', predictions=predictions, date=datetime.now().strftime("%Y-%m-%d"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
