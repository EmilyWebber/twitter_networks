
import sys
import pymongo
import functools
from main import *



def get_cursor_contents(cursor, key, component):
    rv = {}
    rv['peeps'] = []
    for data in cursor:
         rv['peeps'].append(data[key][component])
    return rv


def get_from_mongodb(db, collection):
    client = pymongo.MongoClient()
    database = client[db]
    mongo_collection = database[collection]
    #print mongo_collection.distinct('retweet_count')
    return mongo_collection.find()


def print_cursor_contents(cursor, key, component):
    for data in cursor:
        print data[key][component]



if __name__ == '__main__':
    db = sys.argv[1]
    collection = sys.argv[2]
    key = sys.argv[3]
    component = sys.argv[4]
    write_db = sys.argv[5]
    write_collection = sys.argv[6]

    cursor = get_from_mongodb(db, collection)

    #print_cursor_contents(cursor, key, component)
    save_to_mongo(get_cursor_contents(cursor, key, component),
                  write_db, write_collection)

    for data in get_from_mongodb(write_db, write_collection):
        print data
    
