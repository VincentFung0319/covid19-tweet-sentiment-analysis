# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 15:42:17 2020

@author: compu
"""


import tweepy as t
import re
from textblob import TextBlob
import matplotlib as plot
import searchtweets as st



'''
Create a class for researching Twitter. Specifically, we want to extract,
clean and display the desired tweets. The constructor enables authentication
using the issued developer  keys from Twitter
'''
class TwitterResearch(object):
    # Constructor for the TwitterResearch class  
    def __init__(self):
        # Keys supplied by the twitter developer console to access the api
        api_key = "F2mB31IpYLbcyLC0xSYbGzgvg"
        api_secret = "ffxUqUVWnnJbCUR9cys0IXE5s9eOdKvy8VrUZ16umCsMLex9Ix"
        access_key = "3301331585-zQ2ee9uhRyeeGiUc7eZfGRkNYO1r0xzvEw93BNZ"
        access_secret = "vftouoF9ncB4otazXy2rOITtidmQolsMBPcUUp0R1TLi1"
             
        # Try block that attempts to connect to Twitter and authenticate the connection
        try:
            # Authentication using the Twitter supplied consumer api keys
            self.authentication = t.OAuthHandler(api_key, api_secret)
            # Set the access token to the authentication variable
            self.authentication.set_access_token(access_key, access_secret)
            # Create the api login with the authentication keys
            self.api = t.API(self.authentication)
            # If the connection was successful, tell us
            print("Authentication successful")
            
        except:
            # If the connection was unsuccessful, tell us
            print("Authentication unsuccessful")
            
    '''
    Define a cleanup function that removes all of the extra garble from the tweet
    retrieival process. This is done using the sub method from the regular 
    expressions package.
    '''
    def cleanup(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|((\w+:\/\/\S+))", 
                               " ", tweet).split())
    
    def tweetClassifier(self, tweet):
        classifier = TextBlob(self.cleanup(tweet))
        
        if classifier.sentiment.polarity > 0:
            return 'positive'
        elif classifier.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'
        
    def tweetExtractor(self, query, fromdate=None, todate=None, numberOfTweets=None): 
    
        tweets = []
        #rule = st.collect_results(query, from_date=fromdate, to_date=todate, results_per_call=100)
        
        try:
            tweetsRetrieved = self.api.search(q = query, count = numberOfTweets)
            #tweetsRetrieved = st.collect_results(rule, max_results=100, result_stream_args=fullAuth)
            
            for tweet in tweetsRetrieved:
                
                parsedTweets = {}
                
                
                parsedTweets['text'] = tweet.text
                parsedTweets['sentiment'] = self.tweetClassifier(tweet.text)
                
                if tweet.retweet_count > 0:
                    if parsedTweets not in tweets:
                        tweets.append(parsedTweets)
                else:
                    tweets.append(parsedTweets)
                        
            return tweets
        
        except t.TweepError as e:
            print("Error! This: " + str(e) + " happened!" )
            
    def ruleSetter(self, powertrackRule, fromDate, toDate):    
        rule = st.gen_rule_payload(powertrackRule, from_date=fromDate,\
                                     to_date=toDate, results_per_call=100)
        return rule
                
 
#def main():
    
api = TwitterResearch()
tweets = api.tweetExtractor('Coronavirus')#, '2020-02-20', '2020-02-29')
#tweetsByDate = st.collect_results(ruleSetter("Coronavirus", "2020-02-"), \
#                           max_results=50, result_stream_args=api.fullAuth)


# Plot change over time for sentiment analysis

# picking positive tweets from tweets 
ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] 
# percentage of positive tweets 
print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets))) 
# picking negative tweets from tweets 
ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative'] 
# percentage of negative tweets 
print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets))) 
# percentage of neutral tweets 
print("Neutral tweets percentage: {} %".format(100*(len(tweets) - 
                                        len(ntweets) - len(ptweets))/len(tweets))) 
  
# printing first 5 positive tweets 
print("\n\nPositive tweets:") 
for tweet in ptweets[:50]: 
    print(tweet['text']) 
  
# printing first 5 negative tweets 
print("\n\nNegative tweets:") 
for tweet in ntweets[:50]: 
        print(tweet['text']) 
    
    
#main()