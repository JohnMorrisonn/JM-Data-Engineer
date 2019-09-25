



# # Create the app
# app = Flask(__name__)

# # Load in the baseline model
# filename = open('model_rf_sat.pkl', 'rb')
# model = pickle.load(filename)


# # Create routes to post the prediction
# @app.route('/', methods=['POST'])
# def predict():
#     """
#     Uses randomforest/NLP to classify if the user's input
#     will succeed or not and adds to the json dict output.
#     """

#     # User input from front-end
#     data = request.get_json(force=True)

#     # Change json to dataframe
#     data.update((x, [y]) for x, y in data.items())
#     data_df = pd.DataFrame.from_dict(data)

#     # If user input contains anything the model doesn't
#     drop_columns = ['name', 'blurb']
#     data_df.drop(columns = drop_columns, inplace=True)

#     # Results for RF/NLP model
#     # NEED TO: use pred_proba still
#     model_result = model.predict(data_df)
    
#     # --------------------------------------------------------------

#     # Create connection and cursor for querying custom/general stats
#     mydb = mysql.connector.connect(
#         host = config('hostname'),
#         user = config('username'),
#         passwd = config('password'),
#         db = config('database_name'),
#         use_pure=True
#     )
#     cursor = mydb.cursor(cursor_class=MySQLCursorPrepared)
    
#     # Filter out category and monetaryGoal from user data
#     category = data_df['categories']
#     goal = data_df['monetaryGoal']

#     # Custom stats
#     custom_results = custom_stats(category, goal, cursor)

#     # --------------------------------------------------------------

# # Final output dict
#     output = {'results': int(model_result[0]),
#             'custom_stats': {
#                 'raising_more_success' : custom_results[0],
#                 'category_success' : custom_results[1],
#                 'category_average' : custom_results[2],
#                 'average_duration' : custom_results[3],
#                 'average_backers' : custom_results[4],
#                 'average_over' : custom_results[5]
#             }
#     }
#     return jsonify(output)