# Main application and routing logic
from flask import Flask, render_template, request, jsonify
from decouple import config
from functions import get_query, custom_stats, nlp_df
from visualizations import avg_cat_vis, make_visuals
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from mysql.connector.cursor import MySQLCursorPrepared
import os
import pandas as pd
import mysql.connector
import pickle


# Create the app
app = Flask(__name__)

# Load in the baseline model
filename = open('model_rf_tues.pkl', 'rb')
model = pickle.load(filename)

# print(config('hostname'))

# Create routes to post the prediction
@app.route('/', methods=['POST'])
def predict():
    """
    Uses randomforest/NLP to classify if the user's input
    will succeed or not and adds to the json dict output.
    """

    # User input from front-end
    data = request.get_json(force=True)

    # Change json to dataframe
    data.update((x, [y]) for x, y in data.items())
    data_df = pd.DataFrame.from_dict(data)

    data_df = nlp_df(data_df)

    # If user input contains anything the model doesn't
    drop_columns = ['campaignName', 'description']
    data_df.drop(columns = drop_columns, inplace=True)

    # Results for RF/NLP model
    # NEED TO: use pred_proba still
    model_result = model.predict(data_df)
    
    # --------------------------------------------------------------

    # Create connection and cursor for querying custom/general stats
    mydb = mysql.connector.connect(
        host = config('hostname'),
        user = config('username'),
        passwd = config('password'),
        db = config('database_name'),
        use_pure=True
    )
    cursor = mydb.cursor(cursor_class=MySQLCursorPrepared)
    
    # Filter out category and monetaryGoal from user data
    category = data_df['categories']
    goal = data_df['monetaryGoal']

    # Custom stats
    custom_results = custom_stats(category, goal, cursor)

    # --------------------------------------------------------------

    # Final output dict
    output = {'results': int(model_result[0]),
            'custom_stats': {
                1 : custom_results[0],
                2 : custom_results[1],
                3 : custom_results[2],
                4 : custom_results[3],
                5 : custom_results[4],
                6 : custom_results[5]
            },
            'general_stats': {
                1 : 'general_results1',
                2 : 'general_results2',
                3 : 'general_results3',
                4 : 'general_results4',
                5 : 'general_results5',
                6 : 'general_results6',
                7 : 'general_results7',
                8 : 'general_results8',
                9 : 'general_results9',
            },
    }
    return jsonify(output)

@app.route('/visualizations')
def visualizations():
    # User input from front-end
    goal  = request.args.get('goal', None)
    category  = request.args.get('category', None)

    return make_visuals(goal, category)



if __name__ == '__main__':
    app.run(debug=True)