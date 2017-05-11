import re
import couchdb
import json



def key_word_filter(keywords, tweets):
	new_list = []
	for tweet in tweets:
		if 'text' in tweet:
			text = tweet['text']
			if re.findall(r"(?=("+'|'.join(keywords)+r"))",text):
				new_list.append(tweet)
	return new_list



