# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 00:25:55 2020

@author: compu
"""

import searchtweets as st
import pandas as pd
import numpy as np
import re
from urllib.error import HTTPError
from textblob import TextBlob
import datetime as dt
import matplotlib.pyplot as plt


class TwitterResearchWithDate(object): 
    thirtyAuth = st.load_credentials(filename="C:\\Users\\compu\\OneDrive\\New\\School\\Spring 2020\\Courses\\CSCI 399 Independent Study\\Python\\30key.yaml", \
                    yaml_key="search_tweets_api", env_overwrite=False)
    fullAuth = st.load_credentials(filename="C:\\Users\\compu\\OneDrive\\New\\School\\Spring 2020\\Courses\\CSCI 399 Independent Study\\Python\\fullKey.yaml", \
                    yaml_key="search_tweets_api", env_overwrite=False)
    collectionCounter = 0
    
    def ruleSetter(self, powertrackRule, fromDate, toDate):    
        rule = st.gen_rule_payload(powertrackRule, from_date=fromDate,\
                                     to_date=toDate, results_per_call=100)
        return rule
    
    def ruleSetterAtUser(self, powertrackRule, fromDate, toDate, mediaNetwork):    
        rule = st.gen_rule_payload(powertrackRule + " " + mediaNetwork, from_date=fromDate,\
                                     to_date=toDate, results_per_call=100)
        return rule
    
    def tweetCollector(self, rule):
        try:
            tweets = st.collect_results(rule, max_results=100, result_stream_args=self.thirtyAuth)
        except HTTPError as e:
            print(e)
           
        self.collectionCounter = self.collectionCounter + 1
        return tweets
    
    def cleanup(self, tweet):
            return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|((\w+:\/\/\S+))", 
                                   " ", tweet).split())
        
    def tweetClassifier(self, tweet):            
            classifier = TextBlob(tweet)
            
            if classifier.sentiment.polarity > 0:
                return 'positive'
            elif classifier.sentiment.polarity == 0:
                return 'neutral'
            else:
                return 'negative'

    def createEnglishTweetList(self, tweets):
        listOfTweets = []
        listOfSentiment = []
        for tweet in tweets:
            if tweet.lang == 'en':
                #listTweets = []
                #listSentiments = []
                listOfTweets.append(self.cleanup(tweet.text))
                listOfSentiment.append(self.tweetClassifier(tweet.text))  
                     
        return listOfTweets, listOfSentiment
        
    def createTimeStamps(self, tweets):
        timelist = []
        for i in range(0, len(tweets)):
            if tweets[i].lang == 'en':      
                timelist.append(tweets[i].created_at_datetime.strftime("%Y/%m/%d, %H:%M:%S"))
        return timelist
                
    def getusernames(self, tweets):
        usernames = []
        for i in range(0, len(tweets)):
            if tweets[i].lang == 'en':
                usernames.append(tweets[i].screen_name)
        return usernames
    
    def listToDFandExport(self, finalList, listOfTweets, usernames, listOfSentiment, filename, fileCounter):
        df = pd.DataFrame(finalList, columns=['User Name', 'Statuses', 'Time Created At', 'Sentiment Analysis'])
        df['Statuses'] = listOfTweets
        df['User Name'] = usernames
        df['Sentiment Analysis'] = listOfSentiment
        df.to_csv(r'C:\Users\compu\OneDrive\New\School\Spring 2020\Courses\CSCI 399 Independent Study\Python' + filename + str(fileCounter)+'.csv',\
                  index = False, header = True)
            
    def userTweets(self, rule, filename):
        try:
            tweets = self.tweetCollector(rule)
        except HTTPError as e:
            print(e)
        usernames = (self.getusernames(tweets))
        [listOfTweets, listOfSentiment] = self.createEnglishTweetList(tweets)        
        timelist = (self.createTimeStamps(tweets))
        finalList = {'User Names':usernames, 'Status':listOfTweets, 'Time Created At':timelist, \
                 'Sentiment Analysis':listOfSentiment}        
        self.listToDFandExport(finalList, usernames, listOfTweets, listOfSentiment, filename, self.collectionCounter)
       
    def createTimeChangeList(self, dataframe):
        dates = dataframe.iloc[:, 2]
        indexOfDates = []
        
        for i in range(1, len(dates)):
            if dates[i] != dates[i-1]:
                indexOfDates.append(i)
                
        return indexOfDates
            
       
    def createAverages(self, dataframe, desiredColumn):
        column = dataframe.iloc[:, desiredColumn]
        indexOfDates = self.createTimeChangeList(dataframe)
        indexOfDates.insert(0, 0)
        averages = []
        for i in range(len(indexOfDates)):
                if i == len(indexOfDates) - len(indexOfDates):
                    averages.append(np.average(column[indexOfDates[i]:indexOfDates[i+1]-1]))
                elif i == len(indexOfDates) - 1:    
                    averages.append(np.average(column[indexOfDates[i-1]-1:indexOfDates[i]]))
                else:
                    averages.append(np.average(column[indexOfDates[i]-1:indexOfDates[i+1]-1]))
                    
        return averages, indexOfDates
        
    def plotAveragesByDay(self, dataframe, title):
        [averages, indexOfDates] = self.createAverages(dataframe, 4)
        #print('list type is {} and list is {}'.format(type(indexOfDates), indexOfDates))
        listOfDates = dataframe.iloc[indexOfDates, 2]
        listOfDates = [dt.datetime.strptime(date, '%m/%d/%Y').date() for date in listOfDates]
        x = []
        for i in range(len(indexOfDates)):
            x.append(i)
        
        plt.bar(x, averages)
        plt.xticks(x, listOfDates, rotation=90)
        plt.title(title)
        plt.show()
        
    def polarityDistributionByDay(self, dataframe):
        column = dataframe.iloc[:, 4]
        indexOfDates = self.createTimeChangeList(dataframe)
        indexOfDates.insert(0, 0)
        polarities = []
        for i in range(len(indexOfDates)):
                if i == len(indexOfDates) - len(indexOfDates):
                    polarities.append(column[indexOfDates[i]:indexOfDates[i+1]-1])
                elif i == len(indexOfDates) - 1:    
                    polarities.append(column[indexOfDates[i-1]-1:indexOfDates[i]])
                else:
                    polarities.append(column[indexOfDates[i]-1:indexOfDates[i+1]-1])
                    
        return polarities   
    
    def polarityDistributionByMonth(self, dataframe, indexOfDates):
        column = dataframe.iloc[:, 4]
        polarities = []
        for i in range(len(indexOfDates)-1):
            polarities.append(column[indexOfDates[i]:indexOfDates[i+1]])               
                    
        return polarities
    
    
    def plotDistributionByDay(self, dataframe, distributionOption, dateRangeOption, title):
        [polarities, indexOfDates] = self.polarityDistributionByDay(dataframe)
        #print('list type is {} and list is {}'.format(type(indexOfDates), indexOfDates))
        listOfDates = dataframe.iloc[indexOfDates, 2]
        listOfDates = [dt.datetime.strptime(date, '%m/%d/%Y').date() for date in listOfDates]
        if distributionOption == 0:    
           fig = []
           ax = []
           for i in range(len(listOfDates)):
               fig.append(plt.figure())
               ax.append(fig[i].add_subplot(1,1,1))
               ax[i].hist(polarities[i])
               ax[i].set_title(listOfDates[i])
               ax[i].set_xlabel("Polarity Distribution")
               ax[i].set_ylabel("Tweet Count")
        elif distributionOption == 1: 
           for i in range(len(listOfDates)):
               plt.hist(polarities[i])
               plt.title(title)        
               plt.xlabel('Polarity Distribution')
               plt.ylabel('Tweet Count')
               
    def plotDistributionByMonth(self, polarities, title):
        month = {0:"February", 1:"March", 2:"April"}
        if len(polarities) == 3:
            i = 0
        else:
            i = 1        
        for p in polarities:
            plt.hist(p)
            plt.title(title + month[i])
            i = i + 1
            plt.xlabel('Polarity Distribution')
            plt.ylabel('Tweet Count')
            plt.show()
        
        
    def performSearch(self):
        significantDates = ["2020-03-16", "2020-03-17", "2020-03-18", "2020-03-19", \
                        "2020-03-20", "2020-03-21", "2020-03-22", "2020-03-23", "2020-03-24", \
                        "2020-03-25", "2020-03-26", "2020-03-27", "2020-03-28", "2020-03-29", \
                        "2020-03-30", "2020-03-31", "2020-04-01", "2020-04-02", "2020-04-03", \
                        "2020-04-04", "2020-04-05", "2020-04-06", "2020-04-07", "2020-04-08", \
                        "2020-04-09", "2020-04-10", "2020-04-11"]
        for i in range(0, len(significantDates)-1):
            rule = self.ruleSetter("Coronavirus", significantDates[i], significantDates[i+1])
            #print(rule)
            self.userTweets(rule, "\\tweets")    
        
        NBCrule = self.ruleSetter("Coronavirus from:NBCNews", "2020-04-01", "2020-04-09")
        self.userTweets(NBCrule, "\pNBC")
           
        ABCrule = self.ruleSetter("Coronavirus from:ABC", "2020-04-01", "2020-04-09")
        self.userTweets(ABCrule, "\ABC")
        
        CBSrule = self.ruleSetter("Coronavirus from:CBSNews", "2020-04-01", "2020-04-09")
        self.userTweets(CBSrule, "\CBS")
        
        CNNrule = self.ruleSetter("Coronavirus from:CNN", "2020-04-01", "2020-04-09")
        self.userTweets(CNNrule, "\CNN")
        
        MSNBCrule = self.ruleSetter("Coronavirus from:MSNBC", "2020-04-01", "2020-04-09")
        self.userTweets(MSNBCrule, "\MSNBC")
        
        NYTimesRule = self.ruleSetter("Coronavirus from:nytimes", "2020-04-01", "2020-04-09")
        self.userTweets(NYTimesRule, "\pNYTimes")
        
        VICErule = self.ruleSetter("Coronavirus from:vicenews", "2020-04-01", "2020-04-09")
        self.userTweets(VICErule, "\VICE")

    def plotter(self):
        
        userdata = pd.read_csv('conglomerate2.csv')
        self.plotAveragesByDay(userdata, 'User Tweets (with retweets) Average Sentiment Polarity')
        
        userdata2 = pd.read_csv('conglomerate_corrected.csv')
        self.plotAveragesByDay(userdata2, 'User Tweets (no retweets) Average Sentiment Polarity')
        
        abcdata = pd.read_csv('ABCtweets.csv')
        self.plotAveragesByDay(abcdata, 'ABC Average Sentiment Polarity')
        
        cbsdata = pd.read_csv('CBStweets.csv')
        self.plotAveragesByDay(cbsdata, 'CBS Average Sentiment Polarity')
        
        cnndata = pd.read_csv('CNNtweets.csv')
        self.plotAveragesByDay(cnndata, 'CNN Average Sentiment Polarity')
        
        foxdata = pd.read_csv('FOXtweets.csv')
        self.plotAveragesByDay(foxdata, 'FOX Average Sentiment Polarity')
        
        msnbcdata = pd.read_csv('MSNBCtweets.csv')
        self.plotAveragesByDay(msnbcdata, 'MSNBC Average Sentiment Polarity')
        
        nbcdata = pd.read_csv('NBCtweets.csv')
        self.plotAveragesByDay(nbcdata, 'NBC Average Sentiment Polarity')
        
        nytimesdata = pd.read_csv('NYTimesTweets.csv')
        self.plotAveragesByDay(nytimesdata, 'NY Times Average Sentiment Polarity')
        
        vicedata = pd.read_csv('VICETweets.csv')
        self.plotAveragesByDay(vicedata, 'VICE Average Sentiment Polarity')
        
#def main():
api = TwitterResearchWithDate()
#api.performSearch()

#data = pd.read_csv('conglomerate2.csv')

#api.plotDistributionByDay(data, 1, '')

userdata = pd.read_csv('conglomerate2.csv')
user1index = api.createTimeChangeList(userdata)
listOfDates1 = userdata.iloc[user1index, 2]
userdates1 = [0, 111, 1326, 2481]
polarity1 = api.polarityDistributionByMonth(userdata, userdates1)
api.plotDistributionByMonth(polarity1, 'User Tweets without retweet ')

userdata2 = pd.read_csv('conglomerate_corrected.csv')
user2index = api.createTimeChangeList(userdata2)
listOfDates2 = userdata2.iloc[user2index, 2]
userdates2 = [0, 117, 1354, 2635]
polarity2 = api.polarityDistributionByMonth(userdata2, userdates2)
api.plotDistributionByMonth(polarity2, 'User Tweets with retweet ')

abcdata = pd.read_csv('ABCtweets.csv')
abcindex = api.createTimeChangeList(abcdata)
listOfDates3 = abcdata.iloc[abcindex, 2]
abcdates = [0, 179, 370]
polarity3 = api.polarityDistributionByMonth(abcdata, abcdates)
api.plotDistributionByMonth(polarity3, 'ABC Tweets ')

cbsdata = pd.read_csv('CBStweets.csv')
cbsindex = api.createTimeChangeList(cbsdata)
listOfDates4 = cbsdata.iloc[cbsindex, 2]
cbsdates = [0, 184, 377]
polarity4 = api.polarityDistributionByMonth(cbsdata, cbsdates)
api.plotDistributionByMonth(polarity4, 'CBS Tweets ')

cnndata = pd.read_csv('CNNtweets.csv')
cnnindex = api.createTimeChangeList(cnndata)
listOfDates5 = cnndata.iloc[cnnindex, 2]
cnndates = [0, 161, 325]
polarity5 = api.polarityDistributionByMonth(cnndata, cnndates)
api.plotDistributionByMonth(polarity5, 'CNN Tweets ')

foxdata = pd.read_csv('FOXtweets.csv')
foxindex = api.createTimeChangeList(foxdata)
listOfDates6 = foxdata.iloc[foxindex, 2]
foxdates = [0, 62, 71]
polarity6 = api.polarityDistributionByMonth(foxdata, foxdates)
api.plotDistributionByMonth(polarity6, 'FOX Tweets ')

msnbcdata = pd.read_csv('MSNBCtweets.csv')
msnbcindex = api.createTimeChangeList(msnbcdata)
listOfDates7 = msnbcdata.iloc[msnbcindex, 2]
msnbcdates = [0, 169, 246]
polarity7 = api.polarityDistributionByMonth(msnbcdata, msnbcdates)
api.plotDistributionByMonth(polarity7, 'MSNBC Tweets ')

nbcdata = pd.read_csv('NBCtweets.csv')
nbcindex = api.createTimeChangeList(nbcdata)
listOfDates8 = nbcdata.iloc[nbcindex, 2]
nbcdates = [0, 168, 352]
polarity8 = api.polarityDistributionByMonth(nbcdata, nbcdates)
api.plotDistributionByMonth(polarity8, 'NBC Tweets ')

nytimesdata = pd.read_csv('NYTimesTweets.csv')
nytimesindex = api.createTimeChangeList(nytimesdata)
listOfDates9 = nytimesdata.iloc[nytimesindex, 2]
nytimesdates = [0, 196, 391]
polarity9 = api.polarityDistributionByMonth(nytimesdata, nytimesdates)
api.plotDistributionByMonth(polarity9, 'NY Times Tweets ')

vicedata = pd.read_csv('VICETweets.csv')
viceindex = api.createTimeChangeList(vicedata)
listOfDates10 = vicedata.iloc[viceindex, 2]
vicedates = [0, 186, 365]
polarity99 = api.polarityDistributionByMonth(vicedata, vicedates)
api.plotDistributionByMonth(polarity99, 'VICE Tweets ')


'''
if __name__=="__main__":
    main()
'''