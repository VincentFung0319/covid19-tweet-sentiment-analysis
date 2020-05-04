# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 15:32:15 2020

@author: compu
"""

import searchtweets as st
import pandas as pd
import re
from urllib.error import HTTPError
from textblob import TextBlob

thirtyAuth = st.load_credentials(filename="C:\\Users\\compu\\OneDrive\\New\\School\\Spring 2020\\Courses\\CSCI 399 Independent Study\\Python\\30key.yaml", \
                    yaml_key="search_tweets_api", env_overwrite=False)

fullAuth = st.load_credentials(filename="C:\\Users\\compu\\OneDrive\\New\\School\\Spring 2020\\Courses\\CSCI 399 Independent Study\\Python\\fullKey.yaml", \
                    yaml_key="search_tweets_api", env_overwrite=False)
    
def ruleSetter(powertrackRule, fromDate, toDate, mediaNetwork = None):    
    rule = st.gen_rule_payload(powertrackRule, from_date=fromDate,\
                                 to_date=toDate, results_per_call=100)
    return rule

def cleanup(tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|((\w+:\/\/\S+))", 
                               " ", tweet).split())
    
def tweetClassifier(tweet):
        
        classifier = TextBlob(tweet)
        
        if classifier.sentiment.polarity > 0:
            return 'positive'
        elif classifier.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'
'''     
def getusernames(tweets):
        usernames = []
        users.append[]
        for i in range(0, len(tweets)):
            if tweets[i].lang == 'en':
                usernames.append(tweets[i].screen_name)
        return usernames

def tweetPrinter(tweets):
    for tweet in tweets:
        print(tweet.text)
        print(tweet.lang)
'''


rule = ruleSetter("Coronavirus @FoxNews", "2020-03-16", "2020-04-15")
print(rule)
try:
    tweets = st.collect_results(rule, max_results=100, result_stream_args=thirtyAuth)
except HTTPError as e:
    print(e)
    


