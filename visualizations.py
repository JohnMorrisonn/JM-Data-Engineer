from decouple import config
import pandas as pd

category_list = ['Space Exploration', 'Wearables', 'Hardware', 'Software', 'Web',
       'Sound', "Children's Books", 'Calendars', 'Art Books', 'Fiction',
       'Nature', 'People', 'Letterpress', 'Literary Journals',
       'Nonfiction', 'Footwear', 'Jewelry', 'Pet Fashion',
       'Ready-to-wear', 'Apparel', 'Animation', 'Comedy', 'Documentary',
       'Action', 'Textiles', 'Sculpture', 'Public Art', 'Performance Art',
       'Crafts', 'DIY', 'Woodworking', 'Knitting', 'Candles', 'Quilts',
       'Glass', 'Embroidery', 'Crochet', 'Pottery', 'Product Design',
       'Graphic Design', 'Design', 'Typography', 'Interactive Design',
       'Civic Design', 'Architecture', 'Shorts', 'Narrative Film',
       'Film & Video', 'Webseries', 'Thrillers', 'Family', 'Experimental',
       'Science Fiction', 'Fantasy', 'Music Videos', 'Horror',
       'Movie Theaters', 'Drama', 'Romance', 'Television', 'Festivals',
       'Food', 'Small Batch', "Farmer's Markets", 'Restaurants', 'Farms',
       'Drinks', 'Events', 'Food Trucks', 'Cookbooks', 'Vegan', 'Spaces',
       'Community Gardens', 'Bacon', 'Fashion', 'Accessories', 'Couture',
       'Childrenswear', 'Places', 'Digital Art', 'Flight',
       'Graphic Novels', 'Dance', 'R&B', 'Performances',
       'Gaming Hardware', 'Mobile Games', 'Gadgets', 'Young Adult',
       'Illustration', 'Translations', 'Zines', 'Weaving', 'Ceramics',
       'Radio & Podcasts', 'Immersive', 'Technology', 'Blues',
       'DIY Electronics', 'Jazz', 'Electronic Music', 'Apps',
       'Camera Equipment', 'Robots', '3D Printing', 'Workshops', 'Poetry',
       'Photobooks', 'Photography', 'World Music', 'Mixed Media',
       'Residencies', 'Fine Art', 'Classical Music', 'Printing',
       'Webcomics', 'Animals', 'Publishing', 'Kids', 'Academic',
       'Periodicals', 'Anthologies', 'Indie Rock', 'Comic Books', 'Games',
       'Tabletop Games', 'Installations', 'Conceptual Art',
       'Playing Cards', 'Puzzles', 'Metal', 'Video Games', 'Photo', 'Pop',
       'Rock', 'Country & Folk', 'Print', 'Video', 'Latin', 'Faith',
       'Art', 'Painting', 'Video Art', 'Makerspaces', 'Hip-Hop', 'Music',
       'Stationery', 'Punk', 'Fabrication Tools', 'Chiptune', 'Musical',
       'Theater', 'Comics', 'Plays', 'Journalism', 'Audio',
       'Literary Spaces', 'Live Games', 'Taxidermy']

def grab_data (categories=None):
    import mysql.connector
    import sqlalchemy as db

    host = config('hostname')
    user = config('username')
    passwd = config('password')
    db = config('database_name')

    # engine = db.create_engine('dialect+driver://user:pass@host:port/db')
    engine_str = 'mysql+mysqlconnector://' + user + ':' + passwd + '@' + host + ':3306/' + db
    query = 'SELECT * FROM clean_data WHERE categories IN ({})'.format(', '.join(['%s' for _ in categories]))
    return pd.read_sql(query, engine_str, params=[categories])

def upload_file(file, filename):
    import boto
    import boto.s3
    import sys
    from boto.s3.key import Key
    
    REGION_HOST = config('REGION_HOST')
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')

    bucket_name = 'jbti-kickstarter-success'

    s3_connection = boto.connect_s3(AWS_ACCESS_KEY_ID,
            AWS_SECRET_ACCESS_KEY,host=REGION_HOST)
    bucket = s3_connection.get_bucket(bucket_name)
    key = Key(bucket)
    key.key = 'visualizations/'+filename
    key.set_contents_from_filename(file)
    
    bucket = s3_connection.get_bucket(bucket_name)
    key = bucket.lookup('visualizations/'+filename)
    key.set_acl('public-read')
    
    return 'https://'+bucket_name+'.'+REGION_HOST+'/visualizations/'+filename

def make_visuals(data):
    graph1 = avg_cat_vis(data)
    graph3 = gauge_pred(data)

    return {
        'graph1': graph1,
        'graph3': graph3
    }

def avg_cat_vis(data):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly
    from app import flipped
    import random

    # Change json to dataframe
    data.update((x, [y]) for x, y in data.items())
    data_df = pd.DataFrame.from_dict(data)

    category = data_df['categories'].map(flipped)[0]

    categories = [category]
    categories.extend(random.sample(category_list, 5))

    df = grab_data(categories=categories)
    goal = data_df['monetaryGoal']
    
    success_data = []
    fail_data = []
    
    for cat in categories:
        d = df[(df['categories'] == cat) & (df['target'] == 'successful')]
        success_data.append(d['monetaryGoal'].mean())
        d = df[(df['categories'] == cat) & (df['target'] == 'failed')]
        fail_data.append(d['monetaryGoal'].mean())
    
    fig = go.Figure(data=[
            go.Bar(name='Success', x=categories, y=success_data),
            go.Bar(name='Failed', x=categories, y=fail_data)
        ])

    fig.update_layout(
        barmode='group',
        shapes=[
            go.layout.Shape(
                type="line",
                xref="paper",
                x0=0,
                y0=goal,
                x1=1,
                y1=goal,
                line=dict(
                    width=2,
                    dash="solid",
                )
            )]
        )
    
    test = plotly.offline.plot(fig, filename='temp.html', auto_open=False)
    
    return upload_file('temp.html','visual1-'+data_df['user_id']+'.html')


def gauge_pred(df):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly
    from functions import predict_proba
    
    df.update((x, [y]) for x, y in df.items())
    data_df = pd.DataFrame.from_dict(df)

    # If user input contains anything the model doesn't
    drop_columns = ['campaignName', 'description', 'user_id']
    data_df.drop(columns = drop_columns, inplace=True)

    probability = predict_proba(model, data)

    fig = go.Figure(go.Indicator(
        mode = "gauge+number", 
        value = probability,
        number = {'suffix': "%"},
        domain = {'x': [0, 1], 'y': [0, 1]}, 
        title = {'text': "Probability of Success", 
                 'font':{'family':'Droid Sans Mono', 'size':40, 'color':'#7f7f7f'}},
        gauge = {'axis': {'range': [None, 100]},
                'bar': {'color': "#626463"},
                'steps' : [
                    {'range': [0, 50], 'color': "#f73a5f"}, 
                    {'range': [50, 100], 'color': "#05ce78"}], 
                'threshold' : {'line': {'color': "black", 'width': 1},
                               'thickness': 1, 'value': 50}}))

    test = plotly.offline.plot(fig, filename='temp.html', auto_open=False)
    
    return upload_file('temp.html','visual1-'+data_df['user_id']+'.html')