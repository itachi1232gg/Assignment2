# -*- coding: utf-8 -*-  

import urllib
import nltk
import json as js
import preprocessor as p
import urllib2
from textblob import TextBlob

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from scipy.misc import imread
from os import path
import matplotlib.pyplot as plt
from boto.dynamodb.condition import NULL


def make_wordCloud(frequencies):
    d = path.dirname(__file__)
    # taken from http://jirkavinse.deviantart.com/art/quot-Real-Life-quot-Alice-282261010
    # set the background picture
    alice_coloring = imread(path.join(d, "alice_color.png"))

    wc = WordCloud(font_path='simsun.ttc',
                   background_color="white", 
                   mask=alice_coloring,#background picture
                   stopwords=STOPWORDS.add("said"),
                   max_font_size=40, 
                   random_state=42)
    # create the word cloud
    #wc.generate(text)
    wc.generate_from_frequencies(frequencies)
    # create color from the pic
    image_colors = ImageColorGenerator(alice_coloring)
    # show the picture
    plt.imshow(wc)
    plt.axis("off")
    # make word cloud
    plt.figure()
    plt.show()
    # save the picture
    wc.to_file(path.join(d,"australiaHotTopic.png"))
    
#transform Dictionary to the needed format    
def getFrequencies(wordCountDic):
    frequencies = []
    for z in wordCountDic:
        strf = urllib.unquote(str(z))
        numf = wordCountDic[z]
        frequencies.append([strf,numf])
    return frequencies

def postJson(wordCountDic):
    url = 'http://ec2-13-55-33-247.ap-southeast-2.compute.amazonaws.com:8080/cloud/location/australia'
    data = js.dumps(wordCountDic)
    req = urllib2.Request(url, data)
    f = urllib2.urlopen(req)
    response = f.read()
    f.close()

def getJsonArrayFromJsonFile(filename):
    #test with local json file
    f = file(filename,'r')
    fread = f.read()
    return js.loads(fread)

def getJsonArrayFromURL(URL):
    fjson = urllib2.urlopen(URL)
    s = fjson.read().replace('\r', '\\r').replace('\n', '\\n')
    sjson = unicode(s,errors = 'ignore')
    #sjson = fjson.read().encode('latin-1').decode('gbk').encode('utf-8')
    try:
        y = js.loads(sjson)
    except:
        #print "error ignore!" 
        #pass
        return NULL
    return y
    
def makeWordCountDicAdd(wordCountDic,jsonArray):
    text = ""
    lenJsonArray = len(jsonArray) #The length of the jsonArray
    for i in range(lenJsonArray):

        outstr = ''
        text = jsonArray[i-1]["value"].encode('utf8') #For URL model
        #text = jsonArray[i-1]["json"]["text"].encode('utf8') #For Json file model
        wordList = TextBlob(p.clean(text)).noun_phrases
        for word in wordList:
            for word2 in str(word.encode("GBK", 'ignore')).split():
                outstr += filter(str.isalpha,word2.encode('utf8').lower())
                outstr += ' '
        tokens = nltk.word_tokenize(urllib.unquote(str(outstr)).encode('utf8'))
        text2 = nltk.FreqDist(outstr.split())
        list(text2)
        #print text2
        for j in text2:     
            key = urllib.unquote(str(j)).encode('utf8')
            value = (text2[j])
            #if the word already exists in the dictionary,then add the value to the dictionary value
            if wordCountDic.has_key(key):
                wordCountDic[key] += value # update existing entry
                #else create the new word,and put the value in it
            else :
                wordCountDic[key] = value
    return wordCountDic

def makeWordCountDicInit(jsonArray):
    wordCountDic = dict()
    text = ""
    lenJsonArray = len(jsonArray) #The length of the jsonArray
    for i in range(lenJsonArray):

        outstr = ''
        text = jsonArray[i-1]["value"].encode('utf8') #For URL model
        #text = jsonArray[i-1]["json"]["text"].encode('utf8') #For Json file model
        wordList = TextBlob(p.clean(text)).noun_phrases
        for word in wordList:
            for word2 in str(word.encode("GBK", 'ignore')).split():
                outstr += filter(str.isalpha,word2.lower())
                outstr += ' '
        tokens = nltk.word_tokenize(urllib.unquote(str(outstr)).encode('utf8'))
        text2 = nltk.FreqDist(outstr.split())
        list(text2)
        #print text2
        for j in text2:     
            key = urllib.unquote(str(j)).encode('utf8')
            value = (text2[j])
            #if the word already exists in the dictionary,then add the value to the dictionary value
            if wordCountDic.has_key(key):
                wordCountDic[key] += value # update existing entry
                #else create the new word,and put the value in it
            else :
                wordCountDic[key] = value
    return wordCountDic

#delete the topics which appear less than num times from dictionary
def deleteOccasionalTopics(wordCountDic,num):
    sorted(wordCountDic.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
    for p in wordCountDic.keys():
        strf = urllib.unquote(str(p))
        if wordCountDic[p] < num:
            del wordCountDic[strf]
    return wordCountDic

def main():
    #filename = 'smallTwitter.json'
    URL = "http://ec2-13-55-33-247.ap-southeast-2.compute.amazonaws.com:8080/cloud/twitter/australia"
    #y = getJsonArrayFromJsonFile(filename)
    wordCountDic = dict()   
    #loop:
    while(True):
        y = getJsonArrayFromURL(URL)
        if y == NULL:
            continue
        #y = getJsonArrayFromJsonFile(filename)
        if y == None:
            print "Database is empty!Task finished!"
            break
        else: 
            #count the words of the twitters
            #wordCountDic = makeWordCountDic(wordCountDic,y)
            wordCountDic = makeWordCountDicInit(y)
            #print wordCountDic
            postJson(wordCountDic)
            #print wordCountDic
    #After loop: 
    #y2 = getJsonArrayFromURL(URL)
#     wordCountDic = makeWordCountDicInit(y)
#     print wordCountDic
    #wordCountDic = deleteOccasionalTopics(wordCountDic,5)
    #print wordCountDic
    #frequencies = getFrequencies(wordCountDic)
    #postJson(wordCountDic)
    #make_wordCloud(frequencies)

if __name__ == '__main__':
    main()
