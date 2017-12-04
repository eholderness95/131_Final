import os, sys, csv, errno, json, requests


ACCESS_TOKENS = ['?access_token=551947191811091|aWKc4qfL6ZaUh8TQopALlxlN2Fs','?access_token=111232235573698|mDUr_4FyHHf8bm_P_EWgeWlOfuA','?access_token=113833041974764|3WqmvxXXMoGKQ5sRrtes4N_nu8Y','?access_token=271153104453|QPBw85IEHpEiOXFkIzhtvONQitE']
URL = 'https://graph.facebook.com/'
POST_FILE = open('post_ids.csv', 'r',encoding = "ISO-8859-1")
REACTS = '&fields=reactions.type(LIKE).limit(0).summary(total_count).as(like),reactions.type(LOVE).limit(0).summary(total_count).as(love),reactions.type(HAHA).limit(0).summary(total_count).as(haha),reactions.type(WOW).limit(0).summary(total_count).as(wow),reactions.type(SAD).limit(0).summary(total_count).as(sad),reactions.type(ANGRY).limit(0).summary(total_count).as(angry)&limit=10'
reader = csv.reader(POST_FILE)
error_count = 0
current_token = 0
curr = ''


def fetch_request(url):
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
        print("Connection refused")
        from time import sleep
        sleep(5)
        return fetch_request(url)


def build_comments(comments, post_id):
    count = 0
    while count <= 3:
        count += 1
        for x in comments['data']:
            comm_id = x['id']
            comm_dir = curr + os.sep + post_id + os.sep + comm_id
            filename = os.path.join(os.getcwd(), comm_dir)
            reactions = fetch_request(URL + comm_id + ACCESS_TOKENS[current_token] + REACTS)
            replies = fetch_request(URL + comm_id + '/comments' + ACCESS_TOKENS[current_token])
            if not reactions or not replies:
                continue
            del reactions['id']
            content = {'data': x, 'replies': replies['data'], 'reactions': reactions}
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            with open(filename + '.json', 'w') as obj:
                json.dump(content, obj, indent=4, sort_keys=True)
        try:
            comments = fetch_request(comments['paging']['next'])
        except KeyError:
            break
        except False:
            break


def parse_posts(reader):
    for post in reader:
        if post[2] and post[2] != 'id':
            global curr
            if curr != post[2].split('_')[0]:
                curr = post[2].split('_')[0]
            post_id = post[2]
            post_dir = curr + os.sep + post_id
            filename = os.path.join(os.getcwd(), post_dir)
            print(filename)
            if not os.path.isdir(filename):
                try:
                    reactions = fetch_request(URL + post_id + ACCESS_TOKENS[current_token] + REACTS)
                    post = fetch_request(URL + post_id + ACCESS_TOKENS[current_token])
                    comments = fetch_request(URL + post_id + '/comments' + ACCESS_TOKENS[current_token])
                    if not reactions or not post or not comments:
                        continue
                    del reactions['id']
                    post_data = {'data': post, 'reactions': reactions}
                    os.makedirs(filename)
                    with open(filename + '.json', 'w') as post_obj:
                        json.dump(post_data, post_obj, indent=4, sort_keys=True)
                    build_comments(comments, post_id)
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise


parse_posts(reader)
