class fetch(object):

    def fetch_request(self,url):
        try:
            data = requests.get(url).json()
            global error_count
            if 'error' in data and error_count < 10:
                print(data)
                if data['error']['code'] == 4 or data['error']['code'] == 341:
                    print('Access limit reached for current token. Getting a new one')
                    global current_token
                    if current_token < len(ACCESS_TOKENS) - 1:
                        current_token += 1
                    else:
                        print('Reached end of token list. Cycling back to top.')
                        current_token = 0
                error_count += 1
                print('\nRetrying....')
                return False
            elif error_count >= 5:
                print('Too many retries. Exiting.')
                sys.exit()
            return data
        except requests.exceptions.ConnectionError:
            print("Connection refused. Will retry after timeout.")
            from time import sleep
            sleep(5)
            return fetch_request(url)
        except KeyError:
            return False
