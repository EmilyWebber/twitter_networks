# Exploratory twitter play


import sys
import csv
import twitter
import json
import pymongo

'''
A significant portion of set up help was gleaned from the following site:
https://rawgit.com/ptwobrussell/Mining-the-Social-Web-2nd-Edition/master/
    ipynb/html/Chapter%209%20-%20Twitter%20Cookbook.html
'''


def main():
    ''''
    first arg: location of keys file
    second arg: hashtag to collect
    third arg: hashtag to print out report from db
    '''

    keys = key_grabber(sys.argv[1])
    hashtag = sys.argv[2]
    search_tag = sys.argv[3]

    results = search_hashtag(authenticator(keys), hashtag)
    many_to_mongodb(results['statuses'], 'results', hashtag)

    cursor = get_from_mongodb('results', hashtag)
    #cursor = get_mongodb('results')

    print cursor
    print_cursor_contents(cursor, 'text')
    print_cursor_contents(cursor, 'user')



def key_grabber(txt_file):
    key_file = open(txt_file, 'r')
    return key_file.read().split(',')[:4]


def authenticator(keys):
    consumer_key = keys[0]
    consumer_secret_key = keys[1]
    access_token = keys[2]
    access_token_secret = keys[3]

    authentication = twitter.oauth.OAuth(access_token, access_token_secret,
                                         consumer_key, consumer_secret_key)
    api = twitter.Twitter(auth=authentication)

    return api


def search_hashtag(twitter_api, hashtag):

    # include a RegEx to search different versions of the hashtag?
    # OR %23blacklivesmatter+%23BlackLivesMatter+...

    query = 'q=%23' + hashtag# + '&count=1000'
    return twitter_api.search.tweets(q=query)


def one_to_mongodb(tweet, db, collection):  # probablly need **kwargs
    client = pymongo.MongoClient()
    database = client.db
    mongo_collection = database.collection
    mongo_collection.insert_one(tweets)

def many_to_mongodb(tweets, db, collection):  # probablly need **kwargs
    client = pymongo.MongoClient()
    database = client.db
    mongo_collection = database.collection
    mongo_collection.insert_many(tweets)

def get_from_mongodb(db, collection):
    client = pymongo.MongoClient()
    database = client.db
    mongo_collection = database.collection
    #print mongo_collection.distinct('retweet_count')
    return mongo_collection.find()

def get_mongodb(db, search_tag):
    client = pymongo.MongoClient()
    database = client.db
    return database.find({ hashtag: search_tag })


def get_stats(db, collection):
    client = pymongo.MongoClient()
    database = client.db
    mongo_collection = database.collection

    print mongo_collection.distinct('text')
    print mongo_collection.distinct('user')
    print mongo_collection.distinct('retweet_count')


def print_cursor_contents(cursor, key):
    if key:
        for data in cursor:
            print data[key]
    else:
        for data in cursor:
            print data




main()
