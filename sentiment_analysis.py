from tweepy import API #enables access to user timelines
from tweepy import Cursor #enables accessing specicifc user tweets, followers of users, etc.
from tweepy.streaming import StreamListener #enables listening to tweets
from tweepy import OAuthHandler #enables authentication based on app creds
from tweepy import Stream 

from textblob import TextBlob

import twitter_credentials
import numpy as np #allows various functionality
import pandas as pd #allows storing of tweets and extractions from tweets into data frames
import re
import matplotlib.pyplot as plt #allows plotting of data

#TWITTER CLIENT
#utilizing cursor
class TwitterClient():
    def __init__(self, twitter_user=None): #allows specifying a twitter user, defaults to none
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user 

    def get_twitter_client_api(self): #allows access to api and creation of extractions from data
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets): #allows retrieval of tweets for user specified
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends): #gets friends for specific user
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets): #gets home timeline tweets for specified user
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets
        

#TWITTER AUTHENTICATOR
class TwitterAuthenticator():
    
    def authenticate_twitter_app(self): 
        auth = OAuthHandler(twitter_credentials.API_KEY, twitter_credentials.API_SECRET_KEY) #passing keys and tokens to authenticate
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET) 
        return auth

#TWITTER STREAMER
class TwitterStreamer():

#class for streaming and processing live tweets

    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        #This handles Twitter authentication and the connection to the Twitter Streaming API.
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app() #Making authentication more modular
        stream = Stream(auth, listener)
        
        #this line filters twitter streams to capture keywords
        stream.filter(track=hash_tag_list)

#TWITTER STREAM LISTENER
class TwitterListener(StreamListener): #basic listener class that prints received tweets to stdout
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data): #takes in and prints data from StreamListener
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on data: %s" %stre(e))
        return true

    def on_error(self, status): #prints error msg
        if status == 420: #returning false on_data method in case rate limit occurs
            return false
        print(status)


class TweetAnalyzer(): #allows analyzing and categorizing content from tweets
    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split()) #removing special characters and hyperlinks from tweets

    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0: #deciding whether tweets are negative or positive
            return 1 #positive polarity
        elif analysis.sentiment.polarity == 0:
            return 0 #neutral
        else: 
            return -1 #negative polarity

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets']) #looping through every tweet and extracting text

        df['id'] = np.array([tweet.id for tweet in tweets]) #storing tweet ids in numpy array and creating column 'id'
        df['len'] = np.array([len(tweet.text) for tweet in tweets]) #storing tweet length
        df['date'] = np.array([tweet.created_at for tweet in tweets]) #storing tweet date
        df['source'] = np.array([tweet.source for tweet in tweets]) #storing tweet source (mobile, pc etc.)
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets]) #storing tweet like count
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets]) #stroign tweet retweet count

        return df

if __name__ == "__main__": 
    
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()

    api = twitter_client.get_twitter_client_api()

    tweets = api.user_timeline(screen_name="billgates", count=200) #function that allows specifying which user and how many tweets


    df = tweet_analyzer.tweets_to_data_frame(tweets) #storing tweets to data frame
    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']]) #looping through each tweet and analyzing sentiment
    
    print(df.head(20))


