import tweepy
import re,string
import os
from random import randint
import giphy_client as gc
from giphy_client.rest import ApiException
from random import randint
import requests
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
import time
consumer_key= ''
consumer_secret= ''
access_token= ''
access_token_secret= ''
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


api_instance = gc.DefaultApi()
api_key = ''

FILE_NAME = 'last_seen_id.txt'

def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id

def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return

def strip_links(text):
    link_regex= re.compile('((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', re.DOTALL)
    links= re.findall(link_regex, text)
    for link in links:
        text = text.replace(link[0], ', ')    
    return text

def strip_all_entities(text):
    entity_prefixes = ['@','#']
    for separator in  string.punctuation:
        if separator not in entity_prefixes :
            text = text.replace(separator,' ')
    words = []
    for word in text.split():
        word = word.strip()
        if word:
            if word[0] not in entity_prefixes:
                words.append(word)
    return ' '.join(words)


def check_semantic(hashtag):
    count=0
    semantic=0
    for tweet in tweepy.Cursor(api.search, q='hashtag', lang="en").items(500):
        if (not tweet.retweeted) and ('RT @' not in tweet.text):
            count= count+1
            text= strip_all_entities(strip_links(tweet.text))
            blob = TextBlob(text)
            semantic= semantic+ blob.sentiment.polarity
    print(semantic/count)
    if (semantic/count>=0 and semantic/count<=0.2):
        return('not that happy')
    elif (semantic/count<0):
        return('not happy')
    else:
        return('happy')
def reply():
    print('retrieving and replying to tweets...', flush=True)
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    mentions = api.mentions_timeline(last_seen_id, tweet_mode='extended')
    for mention in reversed(mentions):
        print(str(mention.id) + ' - ' + mention.full_text, flush=True)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)
        if '#checkstatus' in mention.full_text.lower():
            print("found")
            l= mention.full_text.lower().split()
            b= check_semantic('#'+l[2])
            print(b)
            response = api_instance.gifs_search_get(api_key,b,limit=1,offset=randint(1,10),fmt='gif')
            gif_id = response.data[0]
            url_gif = gif_id.images.downsized.url
            with open('test.gif','wb') as f:
                f.write(requests.get(url_gif).content)
            api.update_with_media('test.gif', status='@' + mention.user.screen_name + ' People are ' + b + ' about ' + l[2])

while True:
    reply()
    time.sleep(15)

  






