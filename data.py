
import time
import requests
import json
from datetime import datetime
import itertools
import shortuuid
import pandas as pd
from nltk.tokenize import sent_tokenize

from newspaper import Article
import snscrape.modules.twitter as sntwitter
from psaw import PushshiftAPI
import yfinance as yf
from finvizfinance.news import News
from finvizfinance.screener.overview import Overview
from finvizfinance.quote import finvizfinance
from autonlpinsights import nlpinsights


def get_twitter_tweetdata(searchtext, startdate, enddate, nrows = False ,sentiment = False ,ticker=False):

    """

    :param searchtext: str
    :param startdate: date
    :param enddate: date
    :param nrows: int
    :param sentiment: Bool
    :return:
    """
    search = f'{searchtext} since:{startdate} until:{enddate}'

    # the scraped tweets, this is a generator
    scraped_tweets = sntwitter.TwitterSearchScraper(search).get_items()

    # slicing the generator to keep only the first nrows tweets
    if nrows:
        scraped_tweets = itertools.islice(scraped_tweets, nrows)

    # convert to a DataFrame and keep only relevant columns
    tweet_df = pd.DataFrame(scraped_tweets)[['id', 'date', 'username', 'content', 'url']]
    tweet_df.time_UTC = pd.to_datetime(tweet_df.date)
    tweet_df['created_at_us'] = tweet_df.time_UTC.dt.tz_convert('US/Eastern')
    tweet_df['date_hour'] = tweet_df.created_at_us.dt.strftime("%m/%d/%Y, %H:%M")
    tweet_df['date_hour'] = pd.to_datetime(tweet_df['date_hour'])
    tweetdf = tweet_df[['id', 'date_hour', 'username', 'content', 'url']]
    tweetdf.columns = ['ID', 'date_hour', 'USER', 'text', 'URL']
    if sentiment:
        nlpinsight = nlpinsights(tweetdf, column_name="text")
        tweetdf = nlpinsight.get_sentiment_df()
    if ticker:
        tweetdf['ticker' ] =str(searchtext)

    return tweetdf

def get_reddit_comments(startdate ,enddate, search=False ,subreddit = False ,sentiment=False ,nrows=False ,ticker=False):
    """

    :param start_date:
    :param end_date:
    :param search: Gets Reddit comments based on user's search query text
    :param subreddit: Get All Reddit comments from mentioned subreddit
    :param sentiment:
    :param nrows:
    :return:
    """
    start_date = int(time.mktime(datetime.strptime(startdate, "%Y-%m-%d").timetuple()))
    end_date = int(time.mktime(datetime.strptime(enddate, "%Y-%m-%d").timetuple()))
    api = PushshiftAPI()
    if subreddit:
        api_request_generator = api.search_comments(subreddit=subreddit, after = start_date, before=end_date)
    if subreddit and nrows:
        api_request_generator = api.search_comments(subreddit=subreddit, after = start_date, before=end_date ,limit=nrows)
    if search:
        api_request_generator = api.search_comments(q=search, after = start_date, before=end_date)
    if search and nrows:
        api_request_generator = api.search_comments(q=search, after = start_date, before=end_date ,limit=nrows)
    reddit_df = pd.DataFrame([thing.d_ for thing in api_request_generator])

    # tweet_df['created_at_us'] = df['created_utc'].apply(utctodatetime)
    reddit_df['created_at_us'] = pd.to_datetime(reddit_df['created_utc'], utc=True, unit='s')
    reddit_df['created_at_us'] = reddit_df.created_at_us.dt.tz_convert('US/Eastern')
    reddit_df['date_hour'] = reddit_df.created_at_us.dt.strftime("%m/%d/%Y, %H:%M")
    reddit_df['date_hour'] = pd.to_datetime(reddit_df['date_hour'])

    reddit_df = reddit_df[['id', 'date_hour', 'author', 'body', 'permalink']]
    reddit_df['permalink'] = 'https://www.reddit.com' + reddit_df['permalink']
    reddit_df.columns = ['ID', 'date_hour', 'USER', 'text', 'URL']
    if sentiment:
        nlpinsight = nlpinsights(reddit_df, column_name="text")
        reddit_df = nlpinsight.get_sentiment_df()
    if ticker:
        reddit_df['ticker' ] =str(search)
    return reddit_df


def extract_text_fromurl(url):
    """

    :param url:
    :return:
    """
    """
     Extract the text from url using newspaper package
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text
    except Exception as e:
        text = "Invalid"
    return text


def get_stockrelated_news_blogs(sentiment = False ,summary = False):
    """

    :param sentiment:
    :param summary:
    :return:
    """
    fnews = News()
    all_news = fnews.getNews()
    news_df = all_news['news']
    blogs_df = all_news['blogs']
    blogs_df['text'] = [extract_text_fromurl(url) for url in blogs_df['Link']]
    news_df['text'] = [extract_text_fromurl(url) for url in news_df['Link']]
    news_df['id'] = [shortuuid.uuid(url) for url in news_df['Link']]
    blogs_df['id'] = [shortuuid.uuid(url) for url in news_df['Link']]
    # news_df['Date'] = pd.to_datetime(news_df['Date'], format='%Y-%m-%d %H:%M:%S %p')
    # blogs_df['Date'] = pd.to_datetime(blogs_df['Date'], format='%Y-%m-%d %H:%M:%S %p')


    if sentiment:
        nlpinsight = nlpinsights(news_df, column_name="text")
        news_df = nlpinsight.get_sentiment_df()
        nlpinsight = nlpinsights(blogs_df, column_name="text")
        blogs_df = nlpinsight.get_sentiment_df()
    if summary:
        nlpinsight = nlpinsights(news_df, column_name="text")
        news_df['summary'] = ["".join(nlpinsight.get_summary(text=text)) for text in
                              news_df['text']]
        nlpinsight = nlpinsights(blogs_df, column_name="text")
        blogs_df['summary'] = ["".join(nlpinsight.get_summary(text=text)) for text in blogs_df['text']]

    # news_df = news_df[news_df['text']!='Invalid']
    # blogs_df = blogs_df[blogs_df['text']!='Invalid']

    return news_df, blogs_df


def get_ticker_news_data(value ,sentiment = False ,summary = False):
    """

    :param value:
    :param sentiment:
    :param summary:
    :return:
    """
    stock = finvizfinance(value)
    news_df = stock.TickerNews()
    news_df['text'] = [extract_text_fromurl(url) for url in news_df['Link']]
    news_df['id'] = [shortuuid.uuid(url) for url in news_df['Link']]
    news_df['Date'] = pd.to_datetime(news_df['Date'] ,errors = 'coerce')


    if sentiment:
        nlpinsight = nlpinsights(news_df, column_name="text")
        news_df = nlpinsight.get_sentiment_df()
    if summary:
        nlpinsight = nlpinsights(news_df, column_name="text")
        news_df['summary'] = ["".join(nlpinsight.get_summary(text=text)) for text in
                              news_df['text']]

    news_df['ticker' ] =str(value)

    return news_df


def get_stock_fundamentals(value):
    """

    :param value:
    :return:
    """
    stock = finvizfinance(value)
    stock_fundament = stock.TickerFundament()
    keys = ['Company', 'Sector', 'Industry', 'Index', 'Employees', 'Market Cap', 'Income', 'Target Price', 'Sales',
            'Earnings', 'Avg Volume', 'Price', 'Gross Margin', 'Volume', 'Change']
    dic = {key: stock_fundament[key] for key in keys}
    stock_fund = pd.DataFrame(dic, index=['value']).T.reset_index()

    stockdescription = stock.TickerDescription()
    stockticker_description = "".join(sent_tokenize(stockdescription)[:3])
    return stockticker_description ,stock_fund

def get_stockpricedata(ticker ,period='1d'):
    """

    :param ticker:
    :param period:
    :return:
    """
    # Interval required 1 minute
    data = yf.download(tickers= ticker ,period=period ,interval='5m')
    return data


def getstocktwitsdata(option):
    url = "https://api.stocktwits.com/api/2/streams/symbol/%s.json?limit=200"%(option)
    #url = "https://api.stocktwits.com/api/2/streams/symbol/" + ticker + ".json"
    response = requests.get(url)
    data = json.loads(response.text)
    #print("MESSSAGES")
    #print(data)
    stocktwitsdata = pd.DataFrame(data['messages'])
    stocktwitsdata.time_UTC = pd.to_datetime(stocktwitsdata.created_at)
    stocktwitsdata['created_at'] = stocktwitsdata.time_UTC.dt.tz_convert('US/Eastern')
    stocktwitsdata["date"] = [d.date() for d in stocktwitsdata["created_at"]]
    stocktwitsdata["time"] = [d.time() for d in stocktwitsdata["created_at"]]
    stocktwitsdata = stocktwitsdata.rename(columns={'body': 'text'})

    nlpinsight = nlpinsights(stocktwitsdata, column_name="text")
    stocktwitsdata = nlpinsight.get_sentiment_df()

    return stocktwitsdata


def TWITTER_REDDIT_NEWS_TICKER_DF(ticker, startdate, enddate, nrows=False):
    print(f'Extracting {ticker} data from Twitter')
    TICKER_twitter_df = get_twitter_tweetdata('$' + str(ticker), startdate, enddate, sentiment=True, ticker=True,
                                              nrows=nrows)
    print(f'Extracting {ticker} data from Reddit')
    TICKER_reddit_df = get_reddit_comments(startdate, enddate, search=ticker, sentiment=True, ticker=True, nrows=nrows)
    print(f'Extracting {ticker} data from News')
    TICKER_news_df = get_ticker_news_data(ticker, sentiment=True, summary=True)
    return TICKER_twitter_df, TICKER_reddit_df, TICKER_news_df

def TWITTER_REDDIT_NEWS_BLOGS_STOCKMARKET_DF(ticker, startdate, enddate, nrows=False):
    searchtext = "#stockmarket"
    startdate = '2021-08-23'
    enddate = '2021-08-24'
    STOCK_twitter_df = get_twitter_tweetdata(searchtext, startdate, enddate,sentiment = True,nrows=nrows)
    STOCK_reddit_df = get_reddit_comments(startdate,enddate, subreddit="wallstreetbets",sentiment=True,nrows=nrows)
    STOCK_news_df, STOCK_blogs_df = get_stockrelated_news_blogs(sentiment = True,summary = True)

    STOCK_news_df['Source'] = 'News'
    STOCK_blogs_df['Source'] = 'Blogs'
    STOCK_twitter_df['Source'] = 'Twitter'
    STOCK_reddit_df['Source'] = 'Reddit'
    news_fil_df = STOCK_news_df[['id', 'Date', 'text', 'sentiment_score', 'Link', 'Source']]
    news_fil_df.columns = ['id', 'date', 'text', 'sentiment_score', 'link', 'Source']
    blogs_fil_df = STOCK_blogs_df[['id', 'Date', 'text', 'sentiment_score', 'Link', 'Source']]
    blogs_fil_df.columns = ['id', 'date', 'text', 'sentiment_score', 'link', 'Source']
    reddit_fil_df = STOCK_reddit_df[['ID', 'date_hour', 'text', 'sentiment_score', 'URL', 'Source']]
    reddit_fil_df.columns = ['id', 'date', 'text', 'sentiment_score', 'link', 'Source']
    twitter_fil_df = STOCK_twitter_df[['ID', 'date_hour', 'text', 'sentiment_score', 'URL', 'Source']]
    twitter_fil_df.columns = ['id', 'date', 'text', 'sentiment_score', 'link', 'Source']
    reddit_fil_df['link'] = 'https://www.reddit.com' + reddit_fil_df['link']
    STOCK_COMBINED_SEMANTIC_DF = pd.concat([news_fil_df, blogs_fil_df, reddit_fil_df, twitter_fil_df])

    return STOCK_twitter_df,STOCK_reddit_df,STOCK_news_df,STOCK_blogs_df,STOCK_COMBINED_SEMANTIC_DF
