import twitter
import sys
import json
import pymongo as pm
import time
import datetime
from urllib2 import URLError
from httplib import BadStatusLine


'''
A significant portion of set up help was gleaned or outright copied
 from the following site:
https://rawgit.com/ptwobrussell/Mining-the-Social-Web-2nd-Edition/master/
    ipynb/html/Chapter%209%20-%20Twitter%20Cookbook.html
'''





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

# Straight copied save for max errors
def make_twitter_request(twitter_api_func, max_errors=10000, *args, **kw): 
    
    # A nested helper function that handles common HTTPErrors. Return an updated
    # value for wait_period if the problem is a 500 level error. Block until the
    # rate limit is reset if it's a rate limiting issue (429 error). Returns None
    # for 401 and 404 errors, which requires special handling by the caller.
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):
    
        if wait_period > 3600: # Seconds
            print >> sys.stderr, 'Too many retries. Quitting.'
            raise e
    
        # See https://dev.twitter.com/docs/error-codes-responses for common codes
    
        if e.e.code == 401:
            print >> sys.stderr, 'Encountered 401 Error (Not Authorized)'
            return None
        elif e.e.code == 404:
            print >> sys.stderr, 'Encountered 404 Error (Not Found)'
            return None
        elif e.e.code == 429: 
            print >> sys.stderr, 'Encountered 429 Error (Rate Limit Exceeded)'
            if sleep_when_rate_limited:
                print >> sys.stderr, "Retrying in 15 minutes...ZzZ..."
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                print >> sys.stderr, '...ZzZ...Awake now and trying again.'
                return 2
            else:
                raise e # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print >> sys.stderr, 'Encountered %i Error. Retrying in %i seconds' % \
                (e.e.code, wait_period)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e

    # End of nested helper function
    
    wait_period = 2 
    error_count = 0 

    while True:
        try:
            return twitter_api_func(*args, **kw)
        except twitter.api.TwitterHTTPError, e:
            error_count = 0 
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError, e:
            error_count += 1
            print >> sys.stderr, "URLError encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise
        except BadStatusLine, e:
            error_count += 1
            print >> sys.stderr, "BadStatusLine encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise






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


def firehose(twitter_api, write_db, query):
    twitter_stream = twitter.TwitterStream(auth=twitter_api.auth)
    stream = twitter_stream.statuses.filter(track=query)

    for tweet in stream:
        save_to_mongo(tweet, write_db, query)
        print time.time()
        #print tweet['user']['screen_name']
        #time.sleep(6)
        #output = tweet['user']['screen_name']
        #print type(output), ' : ', output
        #return tweet

def get_friends_ids(friends):
    friend_list = []
    for friend in friends['ids']:
        if friend is not None:
            try:
                friend_list.append(friend)
            except:
                friend_list.append("NONE")
    cursor = friends['next_cursor']
    if cursor != 0:
        time.sleep(30)
        friend_list += get_friends_ids(make_twitter_request(twitter_api.friends.ids(screen_name=handle, cursor=cursor, count=5000)))
    return friend_list

def get_friends_screen_names(friends):
    friend_list = []
    for friend in friends['users']:
        if friend is not None:
            try:
                friend_list.append(friend['screen_name'])
            except:
                friend_list.append("NONE")
    cursor = friends['next_cursor']
    if cursor != 0:
        time.sleep(30)
        friend_list += get_friends_screen_names(make_twitter_request(twitter_api.friends.ids(screen_name=handle, cursor=cursor, count=5000)))
    return friend_list


def get_followers_ids(followers):
    follower_list = []
    for follower in followers['ids']:
        if follower is not None:
            try:
                follower_list.append(follower)
            except:
                follower_list.append("NONE")
    cursor = followers['next_cursor']
    if cursor != 0:
        time.sleep(30)
        follower_list += get_followers_ids(make_twitter_request(twitter_api.followers.ids(screen_name=handle, cursor=cursor, count=5000)))
    return follower_list


def get_followers_screen_names(followers):
    follower_list = []
    for follower in followers['users']:
        if follower is not None:
            try:
                follower_list.append(follower['screen_name'])
            except:
                follower_list.append("NONE")
    cursor = followers['next_cursor']
    if cursor != 0:
        time.sleep(30)
        follower_list += get_followers_screen_names(make_twitter_request(twitter_api.followers.ids(screen_name=handle, cursor=cursor, count=5000)))
    return follower_list




def fs_collector(ids_or_screen_names, friends, followers, label, db_name, coll_name):
    if ids_or_screen_names == 'ids':
        friend_list =  get_friends_ids(friends)
        follower_list = get_followers_ids(followers)
    else:
        friend_list = get_friends_screen_names(friends)
        follower_list = get_followers_screen_names(followers)
    save_to_mongo({label: {"friends": friend_list, "followers": follower_list}}, db_name, coll_name)


#def fs_collector_looper(screen_name

def harvester(db, collection, destination_db, destination_collection):
    user_ids = get_cursor_contents(load_from_mongo(db, collection),
        'user', 'id')

    for user_id in user_ids:
        time.sleep(30)        
        friends = make_twitter_request(twitter_api.friends.ids(user_id=user_id, count=5000))
        followers = make_twitter_request(twitter_api.followers.ids(user_id=user_id, count=5000))
        fs_collector(id_or_sn, friends, followers, str(user_id), destination_db, destination_collection)

    



######################
## TWITTER TO MONGO ##
######################
def get_cursor_contents(cursor, tweet_key, component):
    rv = []
    for data in cursor:
         rv.append(data[tweet_key][component])
    return rv


def save_to_mongo(data, mongo_db, mongo_db_coll, **mongo_conn_kw):
    client = pm.MongoClient(**mongo_conn_kw)
    db = client[mongo_db]
    coll = db[mongo_db_coll]
    return coll.insert(data)

def load_from_mongo(mongo_db, db_coll, return_cursor=False, criteria=None, projection=None, **mongo_conn_kw):
    client = pm.MongoClient(**mongo_conn_kw)
    db = client[mongo_db]
    coll = db[db_coll]
    '''
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
    '''
    return coll.find()

def many_to_mongodb(tweets, db, collection):  # probablly need **kwargs
    client = pm.MongoClient()
    database = client[db]
    mongo_collection = database[collection]
    mongo_collection.insert_many(tweets)

def get_from_mongodb(db, collection):
    client = pm.MongoClient()
    database = client.db
    mongo_collection = database.collection
    print mongo_collection.distinct('retweet_count')
    #return mongo_collection.find()



#################
## MONGO TESTS ##
#################

def test_print(tweets, database, collection):
    client = pm.MongoClient()
    db = client[database]
    print db
#    coll = database[collection]
#    cursor = coll.find()
#    for document in cursor:
#        print document

#----------------------



if __name__ == '__main__':
    keys = parse_keys(sys.argv[1])
    query = sys.argv[2]
    write_db = sys.argv[3]
    handle = sys.argv[4]
    id_or_sn = sys.argv[5]

    twitter_api = oauth_login(keys)

    #firehose(twitter_api, write_db, query)

    harvester('test_firehose_write', 'tsa', 'tsa_network', 'ids')
