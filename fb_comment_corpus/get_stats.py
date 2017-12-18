import pymongo, nltk
import json
from pymongo import MongoClient
from platform import system
from nltk import tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.sentiment.util import *
import os, re, sys, csv, json, ctypes

client = MongoClient()
db = client.comment_corpus
react_lst = ['angry', 'sad', 'like', 'love', 'haha', 'wow']

def execute():
    print('score_reacts: ', score_reacts(docs()))
    print('\nSentimentIntensityAnalyzer: ', score_senti(docs()))
    compare(docs(), docs())

def compare(senti, react): #Compares the scores from SentimentIntensityAnalyzer and scores from score_reacts
    sentiment_score = score_senti(senti)
    reaction_score = score_reacts(react)
    r1 = reaction_score['Negative score']
    n_diff = abs(sentiment_score['Negative score'] - reaction_score['Negative score'])
    p_diff = abs(sentiment_score['Positive score'] - reaction_score['Positive score'])
    print('Sentiment scores: ' + str(sentiment_score) + '\nReaction scores: ' + str(reaction_score))
    print ('Negative Difference: ' + str(round(n_diff, 3)) + '\nPositive Difference: ' + str(round(p_diff, 3)) )

def senti_score_dict(cursor): #Creates a dictionary between messages and polarity scores
    sentiment_dict = {}
    analyzer = SentimentIntensityAnalyzer()
    for document in cursor:
        try:
            message = get_message(document)
            s = analyzer.polarity_scores(message)
            sentiment_dict[message] = s
        except KeyError:
            print('KeyError: ', document['data']['id'])
    cursor.close()
    return sentiment_dict

def score_senti(cursor): #Sums polarity scores in dictionary and returns averages
    senti_dict = senti_score_dict(cursor)
    n = 0
    p = 0
    neu = 0
    for (message, sc) in senti_dict.items():
        n = n + sc['neg']
        p = p + sc['pos']
        neu = neu + sc['neu']
    negative_score = round(n/len(senti_dict.keys()), 3)
    positive_score = round(p/len(senti_dict.keys()), 3)
    neutral_score = round(neu/len(senti_dict.keys()), 3)
    ret_dict = {'Negative score': negative_score, 'Positive score': positive_score, 'Neutral score': neutral_score}
    return ret_dict

def react_score_dict(cursor):  #Creates a dictionary of messages to reactions, adding total, positive, and negative reactions as keys
    react_dict = {}
    for document in cursor:
        t = 0
        p = 0
        n = 0
        message = get_message(document)
        comment_reacts = document['reactions']
        score_dict = {}
        for r in react_lst:
            try:
                s = comment_reacts[r]['summary']['total_count']
                score_dict[r] = s
                t += s
                if r == 'angry' or r == 'sad':
                    n += s
                else:
                    p += s
            except KeyError:
                print("KeyError: ", document['data']['id'])
        score_dict['negative'] = n
        score_dict['positive'] = p
        score_dict['total'] = t
        react_dict[message] = score_dict
    cursor.close()
    return react_dict

def score_reacts(cursor):   #Sums negative, positive, and total reactions in a dictionary and returns negative/total and positive/total as scores
    reaction_dict = react_score_dict(cursor)
    cursor.close()
    n = 0
    p = 0
    t = 0
    for value in reaction_dict.values():
        n += value['negative']
        p += value['positive']
        t += value ['total']
    if t == 0:
        neg = 0
        pos = 0
    else:
        neg = round((n/t), 3)
        pos = round((p/t), 3)
    ret_dict = {'Negative score': neg, 'Positive score': pos}
    return ret_dict

def get_message(document): #Finds and returns a comment from the object
    try:
        m = document['data']['message']
    except KeyError:
        m = 'error'
    return m

def docs(): #Returns access to all documents in the database
    return db.comments.find()

def doc_count(): #Returns number of documents
    cursor = db.comments.find()
    return cursor.count()

def react_operator(react, num = 1, fun = '$gt'): #Returns access to documents with numbers of react that greater than or less than num (Default = greater than 1)
    if react in react_lst and (fun == '$gt' or fun == '$lt'):
        doc_path = 'reactions.' + react + '.summary.total_count'
        cursor = db.comments.find({doc_path: {fun: num}})
        cursor = cursor.sort(doc_path, pymongo.ASCENDING)
        return cursor
    else:
        print("Invalid react parameter.")

def react(react, num): #Returns access to documents with numbers of react that equals num
    if react in r:
        doc_path = 'reactions.' + react + '.summary.total_count'
        cursor = db.comments.find({doc_path: num})
        cursor = cursor.sort(doc_path, pymongo.ASCENDING)
        return cursor
    else:
        print("Invalid react parameter.")

execute()
