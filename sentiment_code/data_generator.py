#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# To pre-process the training and testing set, then store the records into the .pkl files.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import cPickle as pickle

from tweetokenize.tokenizer import Tokenizer
# If don't need anything, just set the string empty
tokenizer = Tokenizer(lowercase=True, allcapskeep=True, normalize=3, usernames='USERNAME', urls='URL', hashtags=False,
        phonenumbers='PHONENUMBER', times='TIME', numbers='NUMBER', ignorequotes=False, ignorestopwords=False)
"""
    @type allcapskeep: C{bool}
        @param allcapskeep: If C{True}, maintains capitalization for words with
        all letters in capitals. Otherwise, capitalization for such words
        is dependent on C{lowercase}.
"""
data_size = 20000
SOURCEFILE_POS = 'pos_reviews'+ str(data_size) +'.txt'
SOURCEFILE_NEG = 'neg_reviews'+ str(data_size) +'.txt'
OUTPUT_FILE_POS = 'pos_reviews'+ str(data_size) +'.pkl'
OUTPUT_FILE_NEG = 'neg_reviews'+ str(data_size) +'.pkl'
current_source = SOURCEFILE_NEG
current_output = OUTPUT_FILE_NEG

def get_reviews(in_file):
    fp = open(in_file , 'r')
    result = []
    for lines in fp.readlines():
        line = lines.replace("\n", "")
        words = tokenizer.tokenize(line)
        result.append(words)
    fp.close()
    return result

list = get_reviews(current_source)  # Source file

with open(current_output,'wb') as f:  # Output file
    pickle.dump(list, f, pickle.HIGHEST_PROTOCOL)
f.close()

# f = open(current_output,'rb')
# pos_list = pickle.load(f)
# po = list(itertools.chain(*pos_list))
# print po[:10]
# print pos_list[:2]

# msg = ('hapi birfdai LESS 🔞#antics  #alessiogetoffthatroof @Little Pub http://t.co/xmeG89RoqH')
# print tokenizer.tokenize(msg)

# l1 = ['a','bqw','wrw']
# l2 = ['b','wty','etu']
# l = [l1,l2]
# po = list(itertools.chain(*l))
# print po