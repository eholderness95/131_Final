import sys
import time
import pickle
import requests
import nltk.tokenize

# Looks for extant 'visited' dictionary from prior attempt at program execution, otherwise initializes empty dict
try:
    visited = pickle.load(open("progress.pickle", "rb"))
except (OSError, IOError) as e:
    visited = {}
error_count = 0
tokenize = False

# Error handler and data returner for FB Graph API calls. All unaccounted errors (and most accounted for errors)
#  will return False. Retries 10 times before terminating
def fetch_request(url):
    try:
        data = requests.get(url).json()
        global error_count
        if 'error' in data and error_count < 10:
            print(data)
            error_count += 1
            if data['error']['code'] == 4 or data['error']['code'] == 341:
                print('Access limit reached for current token. Snoozing for 10 minutes.')
                time.sleep(600)
            # Some posts from .csv may have been deleted, or the privacy settings of the post do not permit API query
            # When parsing the feeds of certain pages (i.e. Justin Bieber), there are many posts that trigger this
            # error, so it isn't included in the error count
            elif data['error']['code'] == 100:
                error_count -= 1
            print('\nRetrying....')
            return False
        elif error_count >= 10:
            print('Too many retries. Exiting.')
            sys.exit()
        return data
    except requests.exceptions.ConnectionError:
        print("Connection refused. Will retry after timeout.")
        time.sleep(5)
        return fetch_request(url)
    except KeyError or ValueError:
        return False

# Pickle visited dict
def save_progress():
    pickle_out = open("progress.pickle", "wb")
    pickle.dump(visited, pickle_out)
    pickle_out.close()

def tokenizer(str):
    return nltk.tokenize.word_tokenize(str)

# Convert UTC string to dict for easier access and manipulation
def process_timestamp(str):
    timestamp = time.strptime(str.split('+')[0], "%Y-%m-%dT%H:%M:%S")
    t = {'year': timestamp[0], 'month': timestamp[1], 'day': timestamp[2], 'hr': timestamp[3], 'min': timestamp[4], 'sec': timestamp[5]}
    return t

def working_on(str):
    print('Working on ' + str + '....')
