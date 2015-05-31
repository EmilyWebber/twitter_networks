import twitter
import sys
import json
import pymongo

#######################
## AUTHORIZE TWITTER ##
#######################

def parse_keys(txt_file):
    keys = open(txt_file, 'r')
    return keys.read().rstrip('\n').split(',')[:4]


def oauth_login(keys):
    
    TOKEN=keys[0]
    TOKEN_SECRET=keys[1]
    CONSUMER_KEY=keys[2]
    CONSUMER_SECRET=keys[3]

    auth = twitter.oauth.OAuth(TOKEN, TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

########################
## ACCESS TWITTER API ##
########################

def twitter_search(twitter_api, query, max_results=200, **kw):
    search_results = twitter_api.search.tweets(q=query, count=100, **kw)

    statuses = search_results['statuses']
    max_results = min(1000, max_results)

    for _ in range(10):
        try:
            next_results = search_results['search_metadata']['next_results']
        except KeyError, e:
            break

        kwargs = dict([ kv.split('=') for kv in next_results[1:].split("&") ])

        search_results = twitter_api.search.tweets(**kwargs)
        statuses += search_results['statuses']

        if len(statuses) > max_results:
            break

    return statuses


def firehose(twitter_api, query):
    twitter_stream = twitter.TwitterStream(auth=twitter_api.auth)
    stream = twitter_stream.statuses.filter(track=query)

    for tweet in stream:
        print tweet['text']

######################
## TWITTER TO MONGO ##
######################

def save_to_mongo(data, mongo_db, mongo_db_coll, **mongo_conn_kw):
    client = pymongo.MongoClient(**mongo_conn_kw)
    db = client[mongo_db]
    coll = db[mongo_db_coll]
    return coll.insert(data)

def load_from_mongo(mongo_db, mong_db_coll, return_cursor=False, criteria=None, projection=None, **mongo_conn_kw):
    client = pymongo.MongoClient(**mongo_conn_kw)
    db = client[mongo_db]
    coll = db[mongo_db_coll]

    if criteria is None:
        criteria = {}

    if projection is None:
        cursor = coll.find(criteria)
    else:
        cursor = coll.find(criteria, projection)

    if return_cursor:
        return cursor
    else:
        return [ item for item in cursor ]

def many_to_mongodb(tweets, db, collection):  # probablly need **kwargs
    client = pymongo.MongoClient()
    database = client[db]
    mongo_collection = database[collection]
    return mongo_collection.insert_many(tweets)

def get_from_mongodb(db, collection):
    client = pymongo.MongoClient()
    database = client.db
    mongo_collection = database.collection
    #print mongo_collection.distinct('retweet_count')
    return mongo_collection.find()

#----------------------

if __name__ == '__main__':
    keys = parse_keys(sys.argv[1])
    query = sys.argv[2]
    twitter_api = oauth_login(keys)
    
#    firehose(twitter_api, query)

    results = twitter_search(twitter_api, query, max_results=10)
#    save_to_mongo(results, 'test', 'test')
#    load_from_mongo('test', 'test')
    print many_to_mongodb(results, 'testdb', 'testcoll')
#    cursor = get_from_mongodb('testdb','testcoll')
#    print [ item for item in cursor ]
