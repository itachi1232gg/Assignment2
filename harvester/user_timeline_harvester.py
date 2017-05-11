# # Load twython library
import json  # Teach python JSON
from twython import Twython, TwythonError, TwythonStreamer, TwythonRateLimitError # Load libraries for twitter API
import couchdb
import time
import twtfilter
 
# Setup Authentificaion Settings
APP_KEY = 'T79jrUVDmeWCcb4nCzOP4cLSi' # Consumer key
APP_SECRET = 'LL0b1eMXpERVnVIDLdUSyp9kKrT8RRNdvdTvScAf77ctwTUlGg' # Consumer secret
 
OAUTH_TOKEN = '4277808732-g7uKDySjF7tXy8DRO6N9RVlC6dK8XR8DDSyIvQo'  # Access token
OAUTH_TOKEN_SECRET = 'bZfS1sfH66iGzD9SmJBDbRJbtJVVTsC6nYwWMUGVZd3HJ'  # Access tocen secret
 
# Obtain an OAuth 2 Access Token
twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
ACCESS_TOKEN = twitter.obtain_access_token()
 
# Use the Access Token
twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)



def get_user_tweets(user_id,before_id):
	if before_id == None:
		results = twitter.get_user_timeline(user_id = user_id, count = 200)
	else:
		results = twitter.get_user_timeline(user_id = user_id, count = 200, max_id = before_id)
	return results

def get_user_tweets_all(user_id):
	user_tweets_list = []
	before_id = None
	while True:
		try:
			results = get_user_tweets(user_id,before_id)
			if len(results) != 0:
				# for result in results:
				# 	print result['text']
				user_tweets_list.extend(results)
				before_id = user_tweets_list[-1]['id'] - 1
			else:
				#no more tweets sent from this user
				#print 'break'
				break
		except TwythonRateLimitError:
			print 'exceed twitter rate limit, please wait 15mins'
			time.sleep(15*60)
			continue

	return user_tweets_list


couch = couchdb.Server('http://130.56.255.77:5984')
db = couch['australia']
user_list = []


for id in db:
	tweet = db[id]
	print tweet
	user_id = tweet['user']['id']
	if user_id not in user_list:
		user_list.append(user_id)
		user_tweets = get_user_tweets_all(user_id)
		for data in user_tweets:
			data['_id'] = data['id_str']
			data = twtfilter.twitter_process(data)
			try:
				db.save(data)
				print data['_id']
			except:
				print 'error'







