import pymongo, nltk
from nltk import tokenize
from nltk.corpus import stopwords
from pymongo import MongoClient
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.sentiment.util import *
client = MongoClient()
db = client.comment_corpus
react_lst = ['angry', 'sad', 'like', 'love', 'haha', 'wow']

def execute():
    print('\n\nscore_reacts: ', score_reacts(docs()))
    print('\nSentimentIntensityAnalyzer: ', score_senti(docs()))
    compare(docs(), docs())
    print('\n\nAverages: ', get_averages(docs()))
    evaluate(docs(), get_averages(docs()))

def compare(senti, react): #Compares the scores from SentimentIntensityAnalyzer and scores from score_reacts
    print('Compare:\n')
    sentiment_score = score_senti(senti)
    reaction_score = score_reacts(react)
    r1 = reaction_score['Negative score']
    n_diff = abs(sentiment_score['Negative score'] - reaction_score['Negative score'])
    p_diff = abs(sentiment_score['Positive score'] - reaction_score['Positive score'])
    neu_diff = abs(sentiment_score['Neutral score'] - reaction_score['Neutral score'])
    print('\n\nSentiment scores: ' + str(sentiment_score) + '\nReaction scores: ' + str(reaction_score))
    print ('\nNegative Difference: ' + str(round(n_diff, 3)) + '\nPositive Difference: ' + str(round(p_diff, 3)) + '\nNeutral Difference: ' + str(round(neu_diff, 3)))


def senti_score_dict(cursor): #Creates a dictionary between messages and polarity scores
    sentiment_dict = {}
    analyzer = SentimentIntensityAnalyzer()
    for document in cursor:
        try:
            message = get_message(document)
            s = comment_sentiment(message, analyzer)
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
                if r == 'like' or r == 'wow':
                    neu += count
                if r == 'angry' or r == 'sad':
                    n += count
                if r == 'love' or r == 'haha':
                    p += count
            except KeyError:
                print("KeyError: ", document['data']['id'])
        score_dict['negative'], score_dict['positive'], score_dict['neutral'] = n, p, neu
        score_dict['total'] = t
        react_dict[message] = score_dict
    cursor.close()
    react_dict = weight_sentiments(react_dict)
    return react_dict

def weight_sentiments(react_dict):  #Accounts for comments with overly negative/positive sentiments
    for key in react_dict.keys():
        if is_negative(key):
            react_dict[key]['negative'] = react_dict[key]['negative'] + react_dict[key]['positive']
            react_dict[key]['postive'] = 0
        if is_positive(key):
            react_dict[key]['positive'] = react_dict[key]['positive'] + react_dict[key]['negative']
            react_dict[key]['negative'] = 0
    return react_dict

def evaluate(cursor, averages): #Evaluates comments with reactions larger than average
    love, haha = averages['love'], averages['haha']
    wow, like = averages['wow'], averages['like']
    angry, sad = averages['angry'], averages['sad']
    avgs = [angry, sad, like, love, haha, wow]
    greater_than_avg = {}
    print('Comments with reaction number greater than the average:\n\n')
    for a in avgs:
        n = avgs.index(a)
        gr_cursor = react_operator(react_lst[n], num = a)
        new_cursor = react_operator(react_lst[n], num = a)
        greater_than_avg[react_lst[n]] = gr_cursor
        analyze_freqs(react_lst[n], new_cursor)
    for g in greater_than_avg.keys():
        cur = greater_than_avg[g]
        print(g + ' average:', avgs[react_lst.index(g)], '\n')
        print('Number of comments with greater averages: ', cur.count())
        print('\nAverage comment polarity scores', score_senti(cur), '\n')

def analyze_freqs(name, cursor):
    freq_dict = {}
    all_comments = ''
    for document in cursor:
        message = get_message(document)
        all_comments = all_comments + ' ' + message
    freq_dist = nltk.FreqDist(nltk.word_tokenize(all_comments))
    stop_words = set(stopwords.words('english'))
    pronouns = ('she','he', 'they', 'him', 'she', 'them', 'it')
    common = [(w,f) for (w,f) in freq_dist.most_common() if w.lower() not in stop_words and w.lower() not in pronouns
              and w.lower().isalpha()][:50]
    print('\n', name + ' most common 50 words: \n', common)

def score_reacts(cursor):   #Sums negative, positive, and total reactions in a dictionary and returns negative/total and positive/total as scores
    reaction_dict = react_score_dict(cursor)
    t, p, n, neu = 0, 0, 0, 0
    for value in reaction_dict.values():
        n += value['negative']
        p += value['positive']
        neu += value['neutral']
        t += value ['total']
    neg = round((n/t), 3)
    pos = round((p/t), 3)
    neu = round((neu/t), 3)
    ret_dict = {'Negative score': neg, 'Positive score': pos, 'Neutral score': neu}
    return ret_dict


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

                        #  Helper Methods

def get_message(document): #Finds and returns a comment from the object
    try:
        m = document['data']['message']
    except KeyError:
        m = 'error'
    return m


def comment_sentiment(comment, sid): #Return polarity scores of a string
    scores = sid.polarity_scores(comment)
    return scores


def is_negative(comment): #Returns if comment has a mostly negative sentiment
    sid = SentimentIntensityAnalyzer()
    pol_scores = comment_sentiment(comment, sid)
    if (pol_scores['neg']-(pol_scores['pos']+pol_scores['neu']) > 0):
        return True
    return False


def is_positive(comment): #Returns if comment has a mostly positive sentiment
    sid = SentimentIntensityAnalyzer()
    pol_scores = comment_sentiment(comment, sid)
    if (pol_scores['pos']-(pol_scores['neg']+ pol_scores['neu']) > 0):
        return True
    return False


def docs(): #Returns access to all documents in the database
    r = 'reactions.'
    path = '.summary.total_count'
    return db.comments.find(
                            {r + 'like' + path : {'$gt' : 30}, '$or':[{r + 'love' + path : {'$gt' : 4}},
                            {r + 'wow' + path : {'$gt' : 4}}, {r + 'haha' + path : {'$gt' : 4}},
                            {r + 'sad' + path : {'$gt' : 4}}, {r + 'angry' + path : {'$gt' : 4}}]})


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
