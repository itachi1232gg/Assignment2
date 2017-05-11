import re
import json
import io


cities = ["Melbourne","Sydney","Adelaide","Perth","Brisbane"]

def location_filter(data):
	if data['place'] != None:
		for city in cities:
			if city in json.dumps(data['place']):
				data['didian'] = city
				break
	else:
		for city in cities:
			if city in json.dumps(data['user']):
				data['didian'] = city
				break
	if 'didian' not in data:
		data['didian'] = 'Australia'
	return data



def topic_filter(data):
	if 'topic' not in data:
		data['topic'] = ""
	return data
def emotion_filter(data):
	if 'emotion' not in data:
		data['emotion'] = ""
	return data

def twitter_process(data):
	data = location_filter(data)
	data = topic_filter(data)
	data = emotion_filter(data)
	return data


