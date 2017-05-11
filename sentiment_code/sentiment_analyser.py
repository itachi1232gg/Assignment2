#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: weixiaol
# Based on other's tokenizer(but also being modified by me), this program identifies the
# topic and the sentiment value of each tweet.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

############################  Initialize Tokenization ####################################
import urllib2
import json
import re
from tweetokenize.tokenizer import Tokenizer
"""
    @type allcapskeep: C{bool}
        @param allcapskeep: If C{True}, maintains capitalization for words with
        all letters in capitals. Otherwise, capitalization for such words
        is dependent on C{lowercase}.
"""
tokenizer = Tokenizer(lowercase=True, allcapskeep=False, normalize=2, usernames = 'USERNAME', urls= 'URL', hashtags=False,
        phonenumbers='', times='', numbers='', ignorequotes=False, ignorestopwords=False)

global response_list, topic_return_list
response_list = []
topic_return_list = []

health_file_path = 'Health&Wellness.txt'

immigrate_topic_keywords = ['immigrant','immigrate','migrator','immigrants','immigration','emigrant','emigrants',
                  'assimilate','pluralism','diversity','naturalism','persecution','refugee','migrators',
                  'visa','quota system','asylum','nativism','steerage','deportation','asian','korean',
                  'indian','chinese','refugees','subclass']
####################################  util functions  #################################
# After being processed by tokenizer, if this msg need to be further analysed by online algorithm, return True.
# Further online analysis is only available when the emoticon/emoji sentiment score is 0
def is_further_analysis_required(id, text, emoticons_sentiment_value):
    if emoticons_sentiment_value > 0:
        globals()['response_list'].append({"text": text, "id": id, "polarity": 4})
    elif emoticons_sentiment_value < 0:
        globals()['response_list'].append({"text": text, "id": id, "polarity": 0})
    else:
        return True # Further analysis needed
    return False # No need for further analysis

# Delete emoticons(unicode only) and return a str for further analysis.
def combine_without_U00xx(separated_list):
    s = ""
    for t in separated_list:
        try:
            str(t)
            s = s + " " + t
        except:
            continue
    return s

def key_word_filter(keywords, tweet):
    if re.findall(r"(?=("+'|'.join(keywords)+r"))",tweet):
        return True
    return False

def getHealthKeywords(in_file):
    fp = open(in_file , 'r')
    keywords_result = []
    for lines in fp.readlines():
        line = lines.replace("\n", "")
        keywords_result.append(line)
    return keywords_result
#########################  Receive data from database  ############################
http_str_root = 'http://ec2-13-55-33-247.ap-southeast-2.compute.amazonaws.com:8080/cloud/'
url_setting = http_str_root + ''
url_download = http_str_root + 'twitter/emotion'
url_upload = http_str_root + 'result/emotion'
topic_upload = http_str_root + 'result/topic'
health_keywords = getHealthKeywords(health_file_path)

while True:
    response = urllib2.urlopen(url_download)
    tweets_from_database = response.read() # 接收数据  变量tweets_r改成从数据库接收即可
    tweets_from_database = unicode( tweets_from_database, errors='ignore')
    tweets_from_database = json.loads(tweets_from_database)
    if len(tweets_from_database) == 0:
        continue
    else:
        #########################  Request sending #############################
        # Request must be a list of dics. Each dic must have a "test" field and other fields will be sent back identically,
        # That is, only "text" will be handled.

        globals()['response_list'] = []
        globals()['topic_return_list'] = []

        tweets_for_further = []
        for tweet_info in tweets_from_database:
            text = tweet_info[u'value'].lower()
            id = tweet_info[u'id']
            if key_word_filter(health_keywords,text):
                topic_dic = {"id": id, "topic": "health"}
                globals()['topic_return_list'].append(topic_dic)
            if key_word_filter(immigrate_topic_keywords,text):
                topic_dic = {"id": id, "topic": "immigration"}
                globals()['topic_return_list'].append(topic_dic)
            words_list, sen_value = tokenizer.tokenize(text)
            if is_further_analysis_required(id, text, sen_value):
                tweet_without_emoji = combine_without_U00xx(words_list)
                tweets_for_further.append({"text": tweet_without_emoji, "id": id})

        method = "bulkClassifyJson"
        http_str = 'http://www.sentiment140.com/api/' + method
        url1 = http_str

        params1 = {"appid": "xdxlwx@gmail.com",
                   "data": tweets_for_further}
        params = json.dumps(params1)

        response = urllib2.urlopen(url1, (params) )
        result_json =  response.read()

        #-----------------------------------------------------------------------------------
        """
        The form of received data：
         {"data":
              [
                  {"text": "I love Titanic.", "id":1234, "polarity": 4},
                  {"text": "I hate Titanic.", "id":4567, "polarity": 0}
              ]
         }
        """
        #------------------------------------------------------------------------------------

        dic = json.loads(result_json)
        result_list = dic["data"] + globals()['response_list']
        topic_result_list = globals()['topic_return_list']
        result_upload = []

        for result in result_list:
            result_dic = {"id": str(result[u'id']), "emotion": str(result[u'polarity'])}
            result_upload.append(result_dic)
        ##############################   Upload data to database   #####################################
        data_upload = json.dumps(topic_result_list)
        req = urllib2.Request(topic_upload, data_upload)
        f = urllib2.urlopen(req)
        response = f.read()

        data_upload = json.dumps(result_upload)
        req = urllib2.Request(url_upload, data_upload)
        f = urllib2.urlopen(req)
        response = f.read()
