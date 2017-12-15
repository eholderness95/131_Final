import requests, pickle, json, sys

ACCESS_TOKEN = '?access_token=551947191811091|aWKc4qfL6ZaUh8TQopALlxlN2Fs'
URL = 'https://graph.facebook.com/'
try:
    visited = pickle.load(open("progress.pickle", "rb"))
except (OSError, IOError) as e:
    visited = {}


def fetch_request(url):
    try:
        data = requests.get(url).json()
        global error_count
        if 'error' in data and error_count < 10:
            print(data)
            error_count += 1
            if data['error']['code'] == 4 or data['error']['code'] == 341:
                print('Access limit reached for current token. ')
                # TODO: Deal with this.
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
        from time import sleep
        sleep(5)
        return fetch_request(url)
    except KeyError or json.decoder.JSONDecodeError:
        return False

def save_progress():
    pickle_out = open("progress.pickle","wb")
    pickle.dump(visited, pickle_out)
    pickle_out.close()