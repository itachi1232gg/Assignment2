#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This program has been modified from Internet resource.
# Partial source code can be found at http://www.360doc.com/content/16/0725/19/15165994_578332920.shtml
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
from tweetokenize.tokenizer import Tokenizer
# If don't need anything, just set the string empty
tokenizer = Tokenizer(lowercase=True, allcapskeep=True, normalize=3, usernames='USERNAME', urls='URL', hashtags=False,
        phonenumbers='PHONENUMBER', times='TIME', numbers='NUMBER', ignorequotes=False, ignorestopwords=False)

data_size = 20000 # 积极或消极数据的数量

DATA_PATH = 'comparison_data/'
POSFILE = DATA_PATH + 'pos_reviews'+ str(data_size) +'.pkl'
NEGFILE = DATA_PATH + 'neg_reviews'+ str(data_size) +'.pkl'

def bag_of_words(words):
    return dict([(word, True) for word in words])

from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist
import pickle
import itertools
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from random import shuffle

def bigram(words, score_fn=BigramAssocMeasures.chi_sq, n=1000):
    bigram_finder = BigramCollocationFinder.from_words(words)  #把文本变成双词搭配的形式
    bigrams = bigram_finder.nbest(score_fn, n) #使用了卡方统计的方法，选择排名前1000的双词
    return bag_of_words(bigrams)

def bigram_words(words, score_fn=BigramAssocMeasures.chi_sq, n=1000):
    bigram_finder = BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(score_fn, n)
    return bag_of_words(words + bigrams)  #所有词和（信息量大的）双词搭配一起作为特征

def create_word_scores():
    posWords = pickle.load(open(POSFILE, 'rb'))
    negWords = pickle.load(open(NEGFILE, 'rb'))

    posWords = list(itertools.chain(*posWords))  # 把多维数组解链成一维数组
    negWords = list(itertools.chain(*negWords))  # 同理

    word_fd = FreqDist()  # 可统计所有词的词频
    cond_word_fd = ConditionalFreqDist()  # 可统计积极文本中的词频和消极文本中的词频
    for word in posWords:
        word_fd[word] += 1
        cond_word_fd['pos'][word] += 1
    for word in negWords:
        word_fd[word] += 1
        cond_word_fd['neg'][word] += 1

    pos_word_count = cond_word_fd['pos'].N()  # 积极词的数量
    neg_word_count = cond_word_fd['neg'].N()  # 消极词的数量
    total_word_count = pos_word_count + neg_word_count

    word_scores = {}
    for word, freq in word_fd.iteritems():
        pos_score = BigramAssocMeasures.chi_sq(cond_word_fd['pos'][word], (freq, pos_word_count),
                                               total_word_count)  # 计算积极词的卡方统计量，这里也可以计算互信息等其它统计量
        neg_score = BigramAssocMeasures.chi_sq(cond_word_fd['neg'][word], (freq, neg_word_count),
                                               total_word_count)  # 同理
        word_scores[word] = pos_score + neg_score  # 一个词的信息量等于积极卡方统计量加上消极卡方统计量

    return word_scores  # 包括了每个词和这个词的信息量


def create_word_bigram_scores():
    posWords = pickle.load(open(POSFILE, 'rb'))
    negWords = pickle.load(open(NEGFILE, 'rb'))

    posWords = list(itertools.chain(*posWords))  # 把多维数组解链成一维数组
    negWords = list(itertools.chain(*negWords))  # 同理

    bigram_finder = BigramCollocationFinder.from_words(posWords)
    posBigrams = bigram_finder.nbest(BigramAssocMeasures.chi_sq, 5000)
    bigram_finder = BigramCollocationFinder.from_words(negWords)
    negBigrams = bigram_finder.nbest(BigramAssocMeasures.chi_sq, 5000)

    pos = posWords + posBigrams  # 词和双词搭配
    neg = negWords + negBigrams

    word_fd = FreqDist()
    cond_word_fd = ConditionalFreqDist()
    for word in pos:
        word_fd[word] += 1
        cond_word_fd['pos'][word] += 1
    for word in neg:
        word_fd[word] += 1
        cond_word_fd['neg'][word] += 1

    pos_word_count = cond_word_fd['pos'].N()
    neg_word_count = cond_word_fd['neg'].N()
    total_word_count = pos_word_count + neg_word_count

    word_scores = {}
    for word, freq in word_fd.iteritems():
        pos_score = BigramAssocMeasures.chi_sq(cond_word_fd['pos'][word], (freq, pos_word_count), total_word_count)
        neg_score = BigramAssocMeasures.chi_sq(cond_word_fd['neg'][word], (freq, neg_word_count), total_word_count)
        word_scores[word] = pos_score + neg_score

    return word_scores

def find_best_words(word_scores, number):
    best_vals = sorted(word_scores.iteritems(), key=lambda (w, s): s, reverse=True)[:number] #把词按信息量倒序排序。number是特征的维度，是可以不断调整直至最优的
    best_words = set([w for w, s in best_vals])
    return best_words

word_scores = create_word_scores()
word_scores_bi = create_word_bigram_scores()

best_words = find_best_words(word_scores_bi, 1500) #选择信息量最丰富的1500个的特征
def best_word_features(words):
    return dict([(word, True) for word in words if word in best_words])


pos_review = pickle.load(open(POSFILE, 'rb'))
neg_review = pickle.load(open(NEGFILE, 'rb'))

shuffle(pos_review) #把积极文本的排列随机化
pos = pos_review
neg = neg_review

def pos_features(feature_extraction_method):
    posFeatures = []
    for i in pos:
        posWords = [feature_extraction_method(i),'pos'] #为积极文本赋予"pos"
        posFeatures.append(posWords)
    return posFeatures

def neg_features(feature_extraction_method):
    negFeatures = []
    for j in neg:
        negWords = [feature_extraction_method(j),'neg'] #为消极文本赋予"neg"
        negFeatures.append(negWords)
    return negFeatures

posFeatures = pos_features(best_word_features)
negFeatures = neg_features(best_word_features)

test_size = data_size/10

trainSet = posFeatures[:-test_size] + negFeatures[:-test_size] #使用了更多数据
testSet = posFeatures[-test_size:] + negFeatures[-test_size:]
test, tag_test = zip(*testSet)

def final_score(classifier):
    classifier = SklearnClassifier(classifier)
    classifier.train(trainSet)
    pred = classifier.classify_many(test)
    return accuracy_score(tag_test, pred)

print 'BernoulliNB`s accuracy is %f' %final_score(BernoulliNB())
print 'MultinomiaNB`s accuracy is %f' %final_score(MultinomialNB())
print 'Maxent`s accuracy is %f' %final_score(LogisticRegression())
print 'SVC`s accuracy is %f' %final_score(SVC())
