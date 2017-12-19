import pymongo, nltk
import json
from pymongo import MongoClient
from platform import system
from nltk import tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.sentiment.util import *


client = MongoClient()
db = client.comment_corpus
react_lst = ['angry', 'sad', 'like', 'love', 'haha', 'wow']

def execute():
    #print('score_reacts: ', score_reacts(docs()))
    #print('\nSentimentIntensityAnalyzer: ', score_senti(docs()))
    #compare(docs(), docs())
    #print(get_averages(react_operator('angry')))
    print('score_reacts: ', score_reacts(react_operator('angry')))

def compare(senti, react): #Compares the scores from SentimentIntensityAnalyzer and scores from score_reacts
    sentiment_score = score_senti(senti)
    reaction_score = score_reacts(react)
    r1 = reaction_score['Negative score']
    n_diff = abs(sentiment_score['Negative score'] - reaction_score['Negative score'])
    p_diff = abs(sentiment_score['Positive score'] - reaction_score['Positive score'])
    neu_diff = abs(sentiment_score['Neutral score'] - reaction_score['Neutral score'])
    print('Sentiment scores: ' + str(sentiment_score) + '\nReaction scores: ' + str(reaction_score))
    print ('Negative Difference: ' + str(round(n_diff, 3)) + '\nPositive Difference: ' + str(round(p_diff, 3)) + '\nNeutral Difference: ' + str(round(neu_diff, 3)))

def comment_sentiment(comment):
    sid = SentimentIntensityAnalyzer()
    scores = sid.polarity_scores(comment)
    return scores

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
    total = len(senti_dict.keys())
    n, p, neu = 0, 0, 0
    for (message, sc) in senti_dict.items():
        n = n + sc['neg']
        p = p + sc['pos']
        neu = neu + sc['neu']
    negative_score = round(n/total, 3)
    positive_score = round(p/total, 3)
    neutral_score = round(neu/total, 3)
    ret_dict = {'Negative score': negative_score, 'Positive score': positive_score, 'Neutral score': neutral_score}
    return ret_dict


def react_score_dict(cursor):  #Creates a dictionary of messages to reactions, adding total, positive, and negative reactions as keys
    react_dict = {}
    for document in cursor:
        t, p, n, neu = 0, 0, 0, 0
        message = get_message(document)
        comment_reacts = document['reactions']
        score_dict = {}
        for r in react_lst:
            try:
                count = comment_reacts[r]['summary']['total_count']
                score_dict[r] = count
                t += count
                if is_negative(message):
                    if r == 'like' or r == 'wow':
                        neu += count
                    else:
                        p = 0
                        n += count
                if is_positive(message):
                    if r == 'like' or r == 'wow':
                        neu += count
                    else:
                        n = 0
                        p += count
                else:
                    if r == 'angry' or r == 'sad':
                        n += count
                    if r == 'like' or r == 'wow':
                        neu += count
                    else:
                        p += count
            except KeyError:
                print("KeyError: ", document['data']['id'])
        score_dict['negative'] = n
        score_dict['positive'] = p
        score_dict['neutral'] = neu
        score_dict['total'] = t
        react_dict[message] = score_dict
    cursor.close()
    return react_dict

def is_negative(comment):
    pol_scores = comment_sentiment(comment)
    if (pol_scores['neg']-pol_scores['pos'] > 0.5):
        return True
    return False

def is_positive(comment):
    pol_scores = comment_sentiment(comment)
    if (pol_scores['pos'] - pol_scores['neg'] > 0.5):
        return True
    return False

def score_reacts(cursor):   #Sums negative, positive, and total reactions in a dictionary and returns negative/total and positive/total as scores
    reaction_dict = react_score_dict(cursor)
    t, p, n, neu = 0, 0, 0, 0
    for value in reaction_dict.values():
        n += value['negative']
        p += value['positive']
        neu += value['neutral']
        t += value ['total']
    if t == 0:
        neg, pos, neu = 0, 0, 0
    else:
        neg = round((n/t), 3)
        pos = round((p/t), 3)
        neu = round((neu/t), 3)
    ret_dict = {'Negative score': neg, 'Positive score': pos, 'Neutral score': neu}
    return ret_dict

#Helper Methods
def get_message(document): #Finds and returns a comment from the object
    try:
        m = document['data']['message']
    except KeyError:
        m = 'error'
    return m


def get_averages(cursor): #Returns averages of reacts in a group of documents
    reacts = react_score_dict(cursor)
    total = len(reacts.keys())
    like, love, haha, wow, angry, sad = 0, 0, 0, 0, 0, 0
    for key in reacts.keys():
        value_dict = reacts[key]
        love += value_dict['love']
        like += value_dict['like']
        haha += value_dict['haha']
        wow += value_dict['wow']
        angry += value_dict['angry']
        sad += value_dict['sad']
    averages = {'love': round(love/total, 3), 'like': round(like/total, 3), 'haha': round(haha/total, 3), 'wow': round(wow/total, 3), 'angry': round(angry/total, 3), 'sad': round(sad/total, 3)}
    return averages


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
