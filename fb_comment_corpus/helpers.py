import requests, pickle, json, nltk.tokenize, sys, time

ACCESS_TOKEN = '?access_token=551947191811091|aWKc4qfL6ZaUh8TQopALlxlN2Fs'
URL = 'https://graph.facebook.com/'
try:
    visited = pickle.load(open("progress.pickle", "rb"))
except (OSError, IOError) as e:
    visited = {}
error_count = 0
tokenize = False


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
    except KeyError or json.decoder.JSONDecodeError:
        return False

def save_progress():
    pickle_out = open("progress.pickle","wb")
    pickle.dump(visited, pickle_out)
    pickle_out.close()

def tokenizer(str):
    return nltk.tokenize.word_tokenize(str)

def process_timestamp(str):
    timestamp = time.strptime(str.split('+')[0], "%Y-%m-%dT%H:%M:%S")
    t = {'year': timestamp[0], 'month': timestamp[1], 'day': timestamp[2], 'hr': timestamp[3], 'min': timestamp[4], 'sec': timestamp[5]}
    return t

def working_on(str):
    print('Working on ' + str + '....')
