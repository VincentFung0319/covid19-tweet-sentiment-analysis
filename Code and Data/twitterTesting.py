# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 17:16:30 2020

@author: compu
"""
import tweepy as twit
import re
from textblob import TextBlob
from datetime import datetime

def cleanup(tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|((\w+:\/\/\S+))", 
                               " ", tweet).split())

api_key = "F2mB31IpYLbcyLC0xSYbGzgvg"
api_secret = "ffxUqUVWnnJbCUR9cys0IXE5s9eOdKvy8VrUZ16umCsMLex9Ix"
access_key = "3301331585-zQ2ee9uhRyeeGiUc7eZfGRkNYO1r0xzvEw93BNZ"
access_secret = "vftouoF9ncB4otazXy2rOITtidmQolsMBPcUUp0R1TLi1"


authentication = twit.OAuthHandler(api_key, api_secret)
    
authentication.set_access_token(access_key, access_secret)
    
api = twit.API(authentication)
        
#api.update_status(status="Hello world!")

tweets = api.search(q = 'Corona Virus', count = 1)

'''
date attribute is '.created_at'
status text attribute is '.text'
NOTE: all require a loop to grab the individual tweets in the area (obvious)
NOTE: variable.__dict__ gives attributes of that variable
'''

for tweet in tweets:
    print(tweet.text)
    print(tweet.geo)
    #print(tweet.created_at)
    print(tweet.__dict__)

print(TextBlob("This sucks").sentiment)
print(TextBlob("I feel that ths is bad").sentiment)
print(TextBlob("This is great").sentiment)


