# # Load twython library
import json  # Teach python JSON
from twython import Twython, TwythonError, TwythonStreamer, TwythonRateLimitError # Load libraries for twitter API
import couchdb
import time
import twitter_filter
#import pymongo # Teach python to talk to MongoDB
 
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
#openfile = open('/Users/cancui/Downloads/Twitter.json','r+')



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


def get_twitter(query,location,before_id):
	if before_id == None:
		results = twitter.search(q=query,geocode = location,lang = 'en', count = 100)
	else:
		results = twitter.search(q=query,geocode = location,lang = 'en', count = 100, max_id = before_id)
	return results

def get_twitter_all():
	before_id = None
#	word_list = ['china']
	user_id_list = []
	australia = '-28.849576,133.360839,1300mi'
	query = "abo OR abbo OR boong OR chinaman OR chink OR gin OR nigga OR nigger OR niger OR gook OR jap OR nip"
	query1 ='chink'
	query2 = ""
	slurs = [ 'chinaman','chink', 'nigga', 'nigger', 'niger']
	#connnect to database
	couch = couchdb.Server('http://130.56.255.77:5984')
	if 'racist' not in couch:
		db = couch.create('racist')
	else:
		db = couch['racist']

	while True:
		try:
			results = get_twitter(query2,australia,before_id)
						#store data
			if len(results['statuses']) == 0:
				#finishing searching, no more tweets
				print 'finish searching'
				break
			else:
				new_list = twitter_filter.key_word_filter(slurs, results['statuses'])
				for tweet in new_list:
					if 'user' in tweet:
						print tweet['text']
						user_id = tweet['user']['id']
						if user_id not in user_id_list:
							user_id_list.append(user_id)
							user_tweets = {
								"user":tweet['user'],
								"_id":str(user_id),
								"tweets":get_user_tweets_all(user_id)
							}

							data = json.dumps(user_tweets)
							try:
								db.save(json.loads(data))
							except:
								print 'error'
							# try:
							# 	db.save(user_tweets)
							# except:
							# 	print 'error'
				before_id = results['statuses'][-1]['id'] -1
		except TwythonRateLimitError:
			print 'rate limit, please wait 15mins'
			time.sleep(60*15)
			continue

get_twitter_all()
