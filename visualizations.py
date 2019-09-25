from decouple import config

def grab_data ():
    import mysql.connector
    import sqlalchemy as db

    host = config('hostname')
    user = config('username')
    passwd = config('password')
    db = config('database_name')

    # engine = db.create_engine('dialect+driver://user:pass@host:port/db')
    engine_str = 'mysql+mysqlconnector://'+user+':'+passwd+'@'+host+':3306/'+db  
    return pd.read_sql_table('clean_data', engine_str)

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

def make_visuals(goal=None,category=None):
    df = grab_data()

    graph1 = avg_cat_vis(df,goal,category)

    return {
        'graph1': graph1
    }

def avg_cat_vis(df,goal=None, category=None):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly
    plotly.offline.init_notebook_mode(connected=True)
    import random

    categories_list = df['categories'].unique()
    if category != None:
        categories = [category]
        categories.extend(categories_list[random.sample(range(0,len(categories_list)),5)])
    else:
        categories = categories_list[random.sample(range(0,len(categories_list)),5)]
    
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
    if goal == None:
        fig.update_layout(
                barmode='group'
            )
    else:
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
    
    plotly.offline.plot(fig, filename='temp.html', auto_open=False)
    
    return upload_file('temp.html','thisisthis-fdfas0516.html')