#!/bin/python
 
# Load twython library
import json  # Teach python JSON
from twython import Twython, TwythonError, TwythonStreamer # Load libraries for twitter API
import couchdb
import twtfilter
#import pymongo # Teach python to talk to MongoDB
 
# Setup Authentificaion Settings
APP_KEY = 'T79jrUVDmeWCcb4nCzOP4cLSi' # Consumer key
APP_SECRET = 'LL0b1eMXpERVnVIDLdUSyp9kKrT8RRNdvdTvScAf77ctwTUlGg' # Consumer secret
 
OAUTH_TOKEN = '4277808732-g7uKDySjF7tXy8DRO6N9RVlC6dK8XR8DDSyIvQo'  # Access token
OAUTH_TOKEN_SECRET = 'bZfS1sfH66iGzD9SmJBDbRJbtJVVTsC6nYwWMUGVZd3HJ'  # Access tocen secret

# Define a class to handle the stream
class MyStreamer(TwythonStreamer):
    
    def on_success(self, data):
        
        if 'text' in data:
            data['_id'] = data['id_str']
            data = twtfilter.twitter_process(data)
            try:
                db.save(data)
                print data['_id']
            except Exception e:
                pass
    def on_error(self, status_code, data):
        print status_code, data
 
# Start the stream
# Requires Authentication as of Twitter API v1.1
if __name__ == "__main__":
    # Obtain an OAuth 2 Access Token
    twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
    ACCESS_TOKEN = twitter.obtain_access_token()
 
    # Use the Access Token
    twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
    
    couch = couchdb.Server()
    db_name = 'australia'
    if db_name in couch:
        db = couch['australia']#existing this table
    else:
        db = couch.create('australia')#creating new table

    stream = MyStreamer(APP_KEY, APP_SECRET,
                    OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    #the longitude and latitudde of australia
    australia = ['113.09, -43.38', '153.38, -10.41']
    #stream filter
    stream.statuses.filter(locations = australia)



