#Plots
import re
import plotly.express as px

#DASHBOARD
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_table
from dash.exceptions import PreventUpdate


import tweepy
##########
from data import *
from update_db import *
from graphs import *
from semanticsearch import  get_similar_sentences


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # for Heroku deployment

tabs_styles = {
    # 'height': '44px',
    'background': '#393939'
}

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}

################################ DATA PROCESSING #########################################

stockprice_number_of_days = '8d'

stocks_screenerview = pd.read_csv('socialmediadata/stocks_screenerview_sectors.csv')




consumer_key = ""
consumer_secret = ""
access_token = "326146455-"
access_token_secret = ""

# Creating the authentication object
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# Setting your access token and secret
auth.set_access_token(access_token, access_token_secret)
# Creating the API object by passing in auth information
api = tweepy.API(auth)

def top_words_on_key(df, colum_name, Source, key, keytype, top_n):
    df_words = " ".join(df[colum_name]).split(' ')

    if key == '@':
        df_ticker_list = re.findall(r'[@][A-Za-z]+', str(df_words))
    elif key == '#':
        df_ticker_list = re.findall(r'[#][A-Za-z]+', str(df_words))
    else:
        df_ticker_list = re.findall(r'[$][A-Za-z]+', str(df_words))
    # print(df_ticker_list)

    df_top_tickers = pd.Series(df_ticker_list).value_counts()[:top_n].to_frame('count').reset_index()
    df_top_tickers['Source'] = Source
    df_top_tickers['keytype'] = keytype
    # print(df_top_tickers)
    return df_top_tickers


LEFT_COLUMN = dbc.Navbar(
    [
        dbc.Row(

            [
        dbc.Col(html.H4(" Stock Market Insights"),md=6),
                html.Br(),
            dbc.Col(
                    html.Label(" Stock Ticker:"),md=2),

                dbc.Col(
                    dcc.Dropdown(id='dropdown',options=[
                                {'label': 'Microsoft (MSFT)', 'value': 'MSFT'},
                                {'label': 'Tesla (TSLA)', 'value': 'TSLA'},
                                {'label': 'TMobile (TMUS)', 'value': 'TMUS'}],value='TMUS',clearable=False
                            ),md=4)



                    ]
                )

    ]
)

def homepage_stockmarket_fig():

    namedent_agg_sorted = stocks_screenerview.groupby(['Sector']).apply(
            lambda x: x.sort_values(['Volume'], ascending=False)).reset_index(
            drop=True)
    namedent_agg_top5_df = namedent_agg_sorted.groupby(['Sector']).head(5)
    namedent_agg_top5_df['Ticker_Company'] = namedent_agg_top5_df['Ticker'] + '(' + namedent_agg_top5_df[
            'Company'] + ')'
    stockvolume_sunburst_fig = px.sunburst(namedent_agg_top5_df, path=['Sector', 'Ticker'], values='Volume',
                                               hover_name="Ticker_Company",color_discrete_sequence=px.colors.qualitative.Pastel)
    stockvolume_sunburst_fig.update_layout(
        title=dict(text="<b>Top Tickers based on <br> Actual Stock Volume</b>"),
        plot_bgcolor='#5B5959',
        font=dict(size=13)
    )

    tweet_df = get_data_from_db( db_table_name = 'socialmediadata.stock_twitterdata')
    reddit_df = get_data_from_db(db_table_name='socialmediadata.stock_redditdata')

    reddit_top_tickers = top_words_on_key(reddit_df, 'text', 'Reddit', '$', 'Tickers', 5)
    twitter_top_tickers = top_words_on_key(tweet_df, 'text', 'Twitter', '$', 'Tickers', 5)

    top_social_media = pd.concat([reddit_top_tickers, twitter_top_tickers])
    top_tickers_socialmedia_sunburstfig = px.sunburst(top_social_media, path=['Source','index'],
                                                          values='count',color_discrete_sequence=px.colors.qualitative.Pastel)
    top_tickers_socialmedia_sunburstfig.update_layout(
        title=dict(text="<b>Top Tickers based on <br> Volume(No Of Tweets) on Social Media</b>"),
        #treemapcolorway=['#0000A0', '#E6A000', '#009FEB'],
        plot_bgcolor='#5B5959',
        font=dict(size=12)
    )

    df_top_reddit_users = pd.Series(reddit_df['user']).value_counts()[:5].to_frame('count').reset_index()
    df_top_reddit_users['Source']='Reddit'

    df_top_twitter_users = pd.Series(tweet_df['user']).value_counts()[:5].to_frame('count').reset_index()
    df_top_twitter_users['Source'] = 'Twitter'

    top_social_users = pd.concat([df_top_reddit_users, df_top_twitter_users])

    top_users_socialmedia_sunburstfig = px.bar(top_social_users, x='count', y='index', color="Source", barmode='group')
    top_users_socialmedia_sunburstfig.update_layout(
        title=dict(text="<b>Top Users on Social Media</b>"),
        # treemapcolorway=['#0000A0', '#E6A000', '#009FEB'],
        plot_bgcolor='#5B5959',
        font=dict(size=12)
    )


    final_namedentitydf = pd.read_csv('socialmediadata/namedentitydf.csv')
    socialmedia_namedentity_fig = px.treemap(final_namedentitydf, path=['source', 'Label', 'Text'],
                                             color_discrete_sequence=px.colors.qualitative.Pastel,values='count')
    socialmedia_namedentity_fig.update_layout(
        title=dict(text="<b>Stock News Named Entities from Twitter,Reddit,News and Blogs </b>"),
        #treemapcolorway=['#0000A0', '#E6A000', '#009FEB'],
        font=dict(size=14)
    )

    return stockvolume_sunburst_fig,top_tickers_socialmedia_sunburstfig,socialmedia_namedentity_fig,top_users_socialmedia_sunburstfig

stockvolume_sunburst_fig,top_tickers_socialmedia_sunburstfig,\
socialmedia_namedentity_fig,top_users_socialmedia_sunburstfig = homepage_stockmarket_fig()


HOME_BODY = [

    dbc.Row(
             [

                dbc.Col(dcc.Graph(id="stockvolume_sunburst_fig",figure=stockvolume_sunburst_fig),width=4),
                dbc.Col(dcc.Graph(id="top_tickers_socialmedia_sunburstfig",figure=top_tickers_socialmedia_sunburstfig),width=4),
                dbc.Col(dcc.Graph(id="top_users_socialmedia_sunburstfig",figure=top_users_socialmedia_sunburstfig),width=4)
            ]
          ),

    dbc.Row(
        [

            dbc.Col(dcc.Graph(id="socialmedia_namedentity_fig", figure=socialmedia_namedentity_fig), width=12)
        ]
    ),
    html.Br(),


    dbc.Col(html.H2("Semantic Search on Twitter,Reddit,News and Blogs"),md=11),
html.Br(),
    dbc.Row(
        [
            dbc.Col(dbc.Card(dcc.Input(id='semantic_search', type="text", value="Stock news related to Healthcare Sector", placeholder="Twitter Search")),
                    md=8)
        ]),

dbc.Row(
        [
dbc.Col(dbc.Card(html.Label(id='semanticsearchtable')), width=11)
        ]),
html.Br(),
    

dbc.Col(html.H2("Real Time Twitter Streaming Insights"),md=11),
html.Br(),
     dbc.Row(
        [
            dbc.Col(dcc.Input(id='twitter_search',type="text", value="stockmarket",placeholder="Twitter Search"), md=8)
        ]),
    html.Br(),
    dcc.Interval(
        id='interval-component',
        interval=1 * 80000,  # in milliseconds
        n_intervals=0
    ),
dbc.Row(
        [
dbc.Col(dbc.Card(html.Label(id='tweettable')), width=7)
        ])

]


SOCIALMEDIA_BODY = [
    html.Br(),
    dbc.Row(
            [
                dbc.Col(dbc.Card(html.Div(id='stockdescription')), width=12)
            ],
           ),
    dbc.Row(
            [
            #dbc.Col(dcc.Graph(id="tophashtagmentionfunnelchart"),width=3),
            dbc.Col(dbc.Spinner(dcc.Graph(id="tickertopmentionssunburstplot"), type = "grow"),width=4),
            dbc.Col(dbc.Spinner(dcc.Graph(id="stockfundchart"), type = "grow"),width=7)
            ],
           ),
    dbc.Row(
        [
            dbc.Col(dbc.Spinner(dcc.Graph(id="stockchart"), type="grow"), width=11)
        ],
    ),
    dbc.Row(
        [

            dbc.Col(dbc.Spinner(dcc.Graph(id="stocksentimentlinechart"), type = "grow"),width=11)
        ],
    ),

dbc.Row(
        [
            dbc.Col(dbc.Spinner(dcc.Graph(id="stocksentimentfunnelallchart"), type="grow"),width=4),
            dbc.Col(dbc.Spinner(dcc.Graph(id="stocksentimentfunnelchart"),  type="grow"),width=8)
        ],
    ),

dbc.Row(
        [
            dbc.Col(dcc.RangeSlider(id='sentiment-slider',min=-1,max=1,step=0.2,value=[0, 0.5]),width=4),
        ],
    ),


    dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Row(dbc.Spinner(dcc.Graph(id="twitterwordcloudplot"),type = "grow")),
                    dbc.Row(dbc.Spinner(dcc.Graph(id="redditwordcloudplot"),type = "grow"))
                ],width=3
            ),
            dbc.Col(dbc.Card(html.Label(id='sentimenttable')), width=7)

        ]

    ),
dbc.Col(html.H2("Real Time Tweets from STOCKTWITS"),md=11),

    dbc.Col(dbc.Spinner(html.Label(id='stocktwits-output'),type = "grow"), width=11)


        ]

NEWS_BODY = [

                dbc.Col(dbc.Spinner(dbc.Card(html.Label(id='newsarticletable'))), width=11),

                dbc.Row(
                    [
                        dbc.Col(dbc.Spinner(dcc.Graph(id="newsngramfig")),width=4),
                        dbc.Col(dbc.Spinner(dcc.Graph(id="newswordcloudfig")), width=4)
                    ],
                ),

                dbc.Col(dbc.Spinner(dbc.Card(dcc.Graph(id='newsnamedentity'))),width=11)

            ]


BODY = dbc.Container\
        ([
           dbc.Row(
                    dbc.Col(
                             dcc.Tabs(id="tabs-styled-with-inline", value='home',
                                      children=[
                                                 dcc.Tab(label='HOME', value='home',style=tab_style, selected_style=tab_selected_style),
                                                 dcc.Tab(label='TICKER-SOCIALMEDIA SENTIMENTS', value='socialmedia',style=tab_style, selected_style=tab_selected_style),
                                                 dcc.Tab(label='TICKER-NEWS ', value='news',style=tab_style, selected_style=tab_selected_style),
                                               ]
                                      ),width={"size": 8, "offset": 2},md={"size": 10, "offset": 1},lg={"size": 12, "offset": 0}
                        ),className="bottom32"),
        #html.Div(dcc.Loading(html.Div(id="main_div"),type="cube", style={"marginTop": "150px"}),style={"minHeight": "500px"})
        html.Div(html.Div(id="main_div"))
       ], style={"maxWidth": "1340px"}
    )



app.layout = html.Div(children=[LEFT_COLUMN,BODY])


###########################################################################################
##########################################CALLBACKS########################################
###########################################################################################


@app.callback([Output('stockdescription', 'children'),
               Output('stockfundchart', 'figure'),
               Output('stockchart', 'figure')
               ],
              Input('dropdown', 'value')

              )
def update_graphs(value):
    #####
    stockdescription, stock_fundament = get_stock_fundamentals(value)
    stock_fund_treefig = px.treemap(stock_fundament, path=['index', 'value'], color_discrete_sequence = px.colors.qualitative.Pastel,height=400)
    data = get_stockpricedata(value, stockprice_number_of_days)
    stock_fig = candlestick_chart(data)

    return stockdescription, stock_fund_treefig,stock_fig


@app.callback(
               Output('tickertopmentionssunburstplot', 'figure'),
              Input('dropdown', 'value')

              )
def update_graphs(value):
    #####

    tweet_df = get_data_from_db(db_table_name='socialmediadata.ticker_twitterdata1')
    reddit_df = get_data_from_db(db_table_name='socialmediadata.ticker_redditdata')
    tweet_df = tweet_df[tweet_df['ticker'] == '$'+value]
    reddit_df = reddit_df[reddit_df['ticker'] == value]
    tweet_df['DataSource'] = 'Twitter'
    reddit_df['DataSource'] = 'Reddit'

    reddit_top_mentions = top_words_on_key(reddit_df, 'text', 'Reddit', '@', 'Mentions', 5)
    reddit_top_hashtags = top_words_on_key(reddit_df, 'text', 'Reddit', '#', 'Hashtags', 5)

    twitter_top_mentions = top_words_on_key(tweet_df, 'text', 'Twitter', '@', 'Mentions', 5)
    twitter_top_hashtags = top_words_on_key(tweet_df, 'text', 'Twitter', '#', 'Hashtags', 5)


    top_social_media = pd.concat(
        [reddit_top_mentions, reddit_top_hashtags, twitter_top_mentions, twitter_top_hashtags])
    top_mentions_hastags_sunburstfig = px.sunburst(top_social_media, path=['keytype', 'Source', 'index'],
                                                   values='count',color_discrete_sequence=px.colors.qualitative.Pastel)
    top_mentions_hastags_sunburstfig.update_layout(
        plot_bgcolor='#5B5959',
        title=dict(text="<b>Top Mentions/Hashtags  on Social Media</b>"),
        font=dict(size=11)
    )

    return top_mentions_hastags_sunburstfig


@app.callback(
               Output('stocksentimentlinechart', 'figure')
               ,
              Input('dropdown', 'value')

              )
def update_graphs(value):
    #####

    tweet_df = get_data_from_db(db_table_name='socialmediadata.ticker_twitterdata1')
    reddit_df = get_data_from_db(db_table_name='socialmediadata.ticker_redditdata')
    tweet_df = tweet_df[tweet_df['ticker'] == '$'+ value]
    reddit_df = reddit_df[reddit_df['ticker'] == value]
    tweet_df['DataSource'] = 'Twitter'
    reddit_df['DataSource'] = 'Reddit'

    twitter_reddit_sentiment_df = pd.concat([tweet_df, reddit_df])

    twitter_reddit_sentiment_df['datehour'] = pd.to_datetime(
        twitter_reddit_sentiment_df.date_hour.dt.strftime("%m/%d/%Y, %H"))
    twitter_reddit_sentiment_df['Date'] = pd.to_datetime(twitter_reddit_sentiment_df.date_hour.dt.strftime("%m/%d/%Y"))
    finaldf = twitter_reddit_sentiment_df.groupby(['datehour', 'DataSource'])['sentiment_score'].mean().reset_index()
    stock_sentiment_line_fig = update_sentiment_linechart(finaldf, x='datehour', y='sentiment_score',
                                                          color='DataSource')
    return stock_sentiment_line_fig


@app.callback([
               Output('stocksentimentfunnelallchart', 'figure'),
               Output('stocksentimentfunnelchart', 'figure')
               ],
              Input('dropdown', 'value')

              )
def update_graphs(value):
    #####

    tweet_df = get_data_from_db(db_table_name='socialmediadata.ticker_twitterdata1')
    reddit_df = get_data_from_db(db_table_name='socialmediadata.ticker_redditdata')
    tweet_df = tweet_df[tweet_df['ticker'] == '$'+value]
    reddit_df = reddit_df[reddit_df['ticker'] == value]
    tweet_df['DataSource'] = 'Twitter'
    reddit_df['DataSource'] = 'Reddit'
    twitter_reddit_sentiment_df = pd.concat([tweet_df, reddit_df])

    twitter_reddit_sentiment_df['datehour'] = pd.to_datetime(
        twitter_reddit_sentiment_df.date_hour.dt.strftime("%m/%d/%Y, %H"))
    twitter_reddit_sentiment_df['Date'] = pd.to_datetime(twitter_reddit_sentiment_df.date_hour.dt.strftime("%m/%d/%Y"))
    finaldf_date = twitter_reddit_sentiment_df.groupby(['Date', 'DataSource', 'sentiment']).size().reset_index()
    final__ = finaldf_date.sort_values(0, ascending=False)
    stock_sentiment_funnel_all_fig = px.bar(final__, x=0, y='sentiment', color="DataSource")
    #stock_sentiment_funnel_all_fig.update_layout(showlegend=False)

    finaldf_ = twitter_reddit_sentiment_df.groupby(['datehour', 'DataSource', 'sentiment']).size().reset_index()
    finaldf_2 = finaldf_[finaldf_['sentiment'] != "Neutral"]
    stock_sentiment_funnel_fig = update_stock_sentiment_funnel(finaldf_2, x="datehour", y=0, text="DataSource",
                                                               color="sentiment")

    return stock_sentiment_funnel_all_fig,stock_sentiment_funnel_fig

@app.callback([
                Output('sentimenttable', 'children'),
                Output('redditwordcloudplot', 'figure'),
            Output('twitterwordcloudplot', 'figure')
               ],
                  Input('dropdown', 'value')

               )
def update_graphs(value):


    tweetdf = get_data_from_db( db_table_name = 'socialmediadata.ticker_twitterdata1')
    redditdf = get_data_from_db(db_table_name='socialmediadata.ticker_redditdata')

    tweet_df = tweetdf[tweetdf['ticker'] == '$'+value]
    reddit_df = redditdf[redditdf['ticker'] == value]

    tweet_df['DataSource'] = 'Twitter'
    reddit_df['DataSource'] = 'Reddit'

    twitter_reddit_sentiment_df = pd.concat([tweet_df, reddit_df])


    nlpinsight = nlpinsights(reddit_df, column_name="text")
    reddit_wordcloud_fig = nlpinsight.visualize_wordclouds()

    nlpinsight = nlpinsights(tweet_df, column_name="text")
    twitter_wordcloud_fig = nlpinsight.visualize_wordclouds()

    twitter_reddit_sentiment_df['datehour'] = pd.to_datetime(
        twitter_reddit_sentiment_df.date_hour.dt.strftime("%m/%d/%Y, %H"))
    twitter_reddit_sentiment_df['Date'] = pd.to_datetime(twitter_reddit_sentiment_df.date_hour.dt.strftime("%m/%d/%Y"))

    print(twitter_reddit_sentiment_df.columns)
    twitter_reddit_sentiment_fil = twitter_reddit_sentiment_df[['date_hour', 'text', 'sentiment_score','DataSource','url']]
    twitter_reddit_sentiment_fil = twitter_reddit_sentiment_fil.round(3)
    def f(row):
        l = "[{0}]({0})".format(row["url"])
        return l

    print(twitter_reddit_sentiment_fil.head(2))
    twitter_reddit_sentiment_fil["url"] = twitter_reddit_sentiment_fil.apply(f, axis=1)

    #twitter_reddit_sentiment_fil = twitter_reddit_sentiment_fil[
     #   (twitter_reddit_sentiment_fil['sentiment_score'] > int(slidervalue[0])) & (
      #              twitter_reddit_sentiment_fil['sentiment_score'] < int(slidervalue[1]))]


    sentiments_table = dash_table.DataTable(

        id='datatable-output1',
        style_data={
            'whiteSpace': 'normal',
            # 'height': 'auto'
        },

        data=twitter_reddit_sentiment_fil.to_dict('records'),
        row_selectable="multi",
        selected_rows=[],
        columns=[{'id': c, 'name': c ,'type':'text', 'presentation':'markdown'} for c in twitter_reddit_sentiment_fil.columns],
        # columns=[{'name': 'Link', 'id': 'Link', 'type': 'text', 'presentation': 'markdown'}],

        filter_action='native',
        sort_action='native',

        css=[
            {'selector': '.row-1', 'rule': 'background: #E6A000;'}
        ],

        page_size=4,
        style_header={'backgroundColor': '#7DF180', 'fontWeight': 'bold', 'border': '1px solid black',
                      'font_size': '18px'},
        style_cell={'font_size': '11px', 'whiteSpace': 'normal',
                    'height': 'auto', 'padding': '15px'},
        # export_format='csv',
        export_format='csv',
        style_cell_conditional=[
            {'if': {'column_id': 'date_hour'},
             'width': '10%',
             'textAlign': 'left'},
            {'if': {'column_id': 'sentiment_score'},
             'width': '5%',
             'textAlign': 'left'},
            {'if': {'column_id': 'text'},
             'width': '65%',
             'textAlign': 'left'},
            {'if': {'column_id': 'DataSource'},
             'width': '10%',
             'textAlign': 'left'},
            {'if': {'column_id': 'url'},
             'width': '10%',
             'textAlign': 'left'}


        ]
    )


    #top_mentions_hastags_sunburstfig
    return sentiments_table,reddit_wordcloud_fig,twitter_wordcloud_fig


@app.callback(
            Output('newsngramfig', 'figure'),
            Output('newswordcloudfig', 'figure'),
              Input('dropdown', 'value')
               )
def update_graphs(value):
    news_df = get_data_from_db(db_table_name='socialmediadata.ticker_newsdata')
    news_df = news_df[news_df['ticker'] == value]
    news_df = news_df.round(3)
    news_df = news_df.head(15)
    nlpinsight = nlpinsights(news_df, column_name="text")
    news_wordcloud_fig = nlpinsight.visualize_wordclouds()
    news_ngram_fig = nlpinsight.visualize_ngrams(2,5)
    return news_ngram_fig,news_wordcloud_fig



@app.callback(
            Output('newsnamedentity', 'figure'),
              Input('dropdown', 'value')
               )
def update_graphs(value):
    news_df = get_data_from_db(db_table_name='socialmediadata.ticker_newsdata')
    news_df = news_df[news_df['ticker'] == value]
    news_df = news_df.round(3)
    news_df = news_df.head(5)
    nlpinsight = nlpinsights(news_df, column_name="text")
    news_namedentity_fig = nlpinsight.visualize_namedentities()
    return news_namedentity_fig

@app.callback(Output('newsarticletable', 'children'),
              Input('dropdown', 'value')
               )
def update_graphs(value):
    news_df = get_data_from_db(db_table_name='socialmediadata.ticker_newsdata')
    news_df = news_df[news_df['ticker'] == value]
    news_df = news_df.round(3)
    #newsarticle_df = news_df[news_df['ticker'] == value]
    newsarticle_df = news_df[['date','title','summary','sentiment_score','link']]
    newsarticle_df = newsarticle_df[newsarticle_df['summary']!='Invalid']
    #print(newsarticle_df)
    def f(row):
        l = "[{0}]({0})".format(row["link"])
        return l


    newsarticle_df["link"] = newsarticle_df.apply(f, axis=1)

    newsarticle_table = dash_table.DataTable(

        id='datatable-output1',
        style_data={
            'whiteSpace': 'normal',
            # 'height': 'auto'
        },

        data=newsarticle_df.to_dict('records'),
        row_selectable="multi",
        selected_rows=[],
        columns=[{'id': c, 'name': c ,'type':'text', 'presentation':'markdown'} for c in newsarticle_df.columns],
        # columns=[{'name': 'Link', 'id': 'Link', 'type': 'text', 'presentation': 'markdown'}],

        filter_action='native',
        sort_action='native',

        css=[
            {'selector': '.row-1', 'rule': 'background: #E6A000;'}
        ],

        page_size=4,
        style_header={'backgroundColor': '#7DF180', 'fontWeight': 'bold', 'border': '1px solid black',
                      'font_size': '18px'},
        style_cell={'font_size': '11px', 'whiteSpace': 'normal',
                    'height': 'auto', 'padding': '15px'},
        # export_format='csv',
        export_format='csv',
        style_cell_conditional=[
            {'if': {'column_id': 'Date'},
             'width': '15%',
             'textAlign': 'left'},
            {'if': {'column_id': 'Title'},
             'width': '20%',
             'textAlign': 'left'},
            {'if': {'column_id': 'Link'},
             'width': '10%',
             'textAlign': 'left'},
            {'if': {'column_id': 'summary'},
             'width': '45%',
             'textAlign': 'left'},
            {'if': {'column_id': 'sentiment_score'},
             'width': '10%',
             'textAlign': 'left'},
            {'if': {'column_id': 'sentiment'},
             'width': '5%',
             'textAlign': 'left'}

        ]

    )
    return newsarticle_table





@app.callback(Output('tweettable', 'children'),
              [Input('twitter_search', 'value'),
                Input('interval-component', 'n_intervals')]
               )
def update_graphs(value,n):
    mainlis = []
    res = api.search(value)
    for i in res:
        lis = []
        lis.append([i.id, i.created_at, i.text])
        mainlis.append(lis)

        tweetstream_df = pd.DataFrame(mainlis)
        tweetstream_table = dash_table.DataTable(

            id='datatable-output',
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'lineHeight': '15px'
            },

            data=tweetstream_df.to_dict('records'),

            css=[
                {'selector': '.row-1', 'rule': 'background: #E6A000;'}
            ],
            columns=[{'id': c, 'name': c} for c in tweetstream_df.columns],
            page_size=8,
            style_header={'backgroundColor': '#E6A000', 'fontWeight': 'bold', 'border': '1px solid black',
                          'font_size': '18px'},
            style_cell={'font_size': '11px', 'font_family': "Arial", 'whiteSpace': 'normal',
                        'height': 'auto', 'padding': '15px'

                        },
            # export_format='csv',
            export_format='csv',
            export_headers='display',
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            style_cell_conditional=[
                {'if': {'column_id': 'UserTweetDate'},
                 'width': '10%',
                 'textAlign': 'center'},
                {'if': {'column_id': 'Time'},
                 'width': '10%',
                 'textAlign': 'center'},
                {'if': {'column_id': 'Tweet'},
                 'width': '55%',
                 'textAlign': 'left'},
                {'if': {'column_id': 'sentiment'},
                 'width': '15%',
                 'textAlign': 'left'},
            ]
        )


    return tweetstream_table




@app.callback(Output('semanticsearchtable', 'children')
               ,
              Input('semantic_search', 'value')
               )
def update_graphs(value):
    stock_socialmediasemanticdata = get_data_from_db(db_table_name='socialmediadata.stock_socialmediasemanticdata')
    semantic_df = get_similar_sentences(stock_socialmediasemanticdata,[value])

    def f(row):
        l = "[{0}]({0})".format(row["link"])
        return l


    semantic_df["link"] = semantic_df.apply(f, axis=1)
    print("Semantic Searchhh")
    print(semantic_df.head())

    tweetstream_table = dash_table.DataTable(

        id='datatable-output1',
        style_data={
            'whiteSpace': 'normal',
            # 'height': 'auto'
        },


        data=semantic_df.to_dict('records'),
        columns=[{'id': c, 'name': c, 'type': 'text', 'presentation': 'markdown'} for c in semantic_df.columns],
        # columns=[{'name': 'Link', 'id': 'Link', 'type': 'text', 'presentation': 'markdown'}],

        #filter_action='native',
        sort_action='native',

        css=[
            {'selector': '.row-1', 'rule': 'background: #E6A000;'}
        ],

        page_size=4,
        style_header={'backgroundColor': '#E6A000', 'fontWeight': 'bold', 'border': '1px solid black',
                      'font_size': '18px'},
        style_cell={'font_size': '11px', 'whiteSpace': 'normal',
                    'height': 'auto', 'padding': '15px'},
        # export_format='csv',
        export_format='csv'

    )

    return tweetstream_table


@app.callback(Output('stocktwits-output', 'children'),
              [Input('dropdown', 'value')])
def get_data_table2(option):
    df2 = getstocktwitsdata(option)
    #print('---STOCKTWITS---')
    #print(df2)
    df = df2[['date','time','text','sentiment']]
    df.columns = ['UserTweetDate', 'Time', 'Tweet', 'sentiment']

    filtereddf = df.copy()
    filteredtable = dash_table.DataTable(

            id='datatable-output',
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'lineHeight': '15px'
            },

            data=filtereddf.to_dict('records'),


            css=[
                { 'selector': '.row-1', 'rule': 'background: #E6A000;' }
            ],
            columns=[{'id': c, 'name': c} for c in filtereddf.columns],
            page_size=8,
            style_header={'backgroundColor': '#E6A000', 'fontWeight': 'bold', 'border': '1px solid black',
                          'font_size': '18px'},
            style_cell={'font_size': '11px', 'font_family':"Arial",'whiteSpace': 'normal',
                        'height': 'auto', 'padding': '15px'

                        },
            #export_format='csv',
            export_format='csv',
            export_headers='display',
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            style_cell_conditional=[
                {'if': {'column_id': 'UserTweetDate'},
                 'width': '10%',
                 'textAlign': 'center'},
                {'if': {'column_id': 'Time'},
                 'width': '10%',
                 'textAlign': 'center'},
                {'if': {'column_id': 'Tweet'},
                 'width': '55%',
                 'textAlign': 'left'},
                {'if': {'column_id': 'sentiment'},
                 'width': '15%',
                 'textAlign': 'left'},
            ]
        )

    return filteredtable

@app.callback(
    Output('main_div', 'children'),
    [Input('tabs-styled-with-inline', 'value')])
def update_graph(tab_btn):
    if tab_btn == "socialmedia":
        return SOCIALMEDIA_BODY

    elif tab_btn == "home":
        return HOME_BODY

    elif tab_btn == "news":
        return NEWS_BODY

if __name__ == "__main__":
    app.run_server(port = 8053)

