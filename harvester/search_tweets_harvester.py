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


def get_twitter(query,location,before_id):
	if before_id == None:
		results = twitter.search(q=query,geocode = location,lang = 'en', count = 100)
	else:
		results = twitter.search(q=query,geocode = location,lang = 'en', count = 100, max_id = before_id)
	return results

before_id = 859087795066781700
#immigrat_topic = 'immigra OR emigra OR assimilat OR pluralism OR diversity OR naturalism OR persecution OR refugee OR visa ORquota system OR asylum ORnativism OR steerage OR deportation OR Asian OR Korean OR indian OR chinese'
query = ' '
# location of Australia
australia = '-28.849576,133.360839,1300mi'

couch = couchdb.Server('http://146.118.101.184:5984')
if 'australia' not in couch:
	db = couch.create('australia')
else:
	db = couch['australia']

while True:
	try:
		results = get_twitter(query,australia,before_id)
		for tweet in results['statuses']:
			tweet['_id'] = tweet['id_str']
			data = twtfilter.twitter_process(tweet)
			try:
				b.save(data)
			except Exception e:
				print 'duplicate data'
				pass
		#store data
		if len(results['statuses']) == 0:
			#finishing searching, no more tweets
			print 'finish searching'
			break
		before_id = results['statuses'][-1]['id'] -1
	except TwythonRateLimitError:
		print 'rate limit, please wait 15mins'
		time.sleep(60*15)
		continue

