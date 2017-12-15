import os, csv, errno, json, nltk.tokenize, helpers

ACCESS_TOKEN = helpers.ACCESS_TOKEN
URL = helpers.URL
POST_FILE = open('post_ids.csv', 'r',encoding = "ISO-8859-1")
REACTS = '&fields=reactions.type(LIKE).limit(0).summary(total_count).as(like),' + \
         'reactions.type(LOVE).limit(0).summary(total_count).as(love),' + \
         'reactions.type(HAHA).limit(0).summary(total_count).as(haha),' + \
         'reactions.type(WOW).limit(0).summary(total_count).as(wow),' + \
         'reactions.type(SAD).limit(0).summary(total_count).as(sad),' + \
         'reactions.type(ANGRY).limit(0).summary(total_count).as(angry)&limit=10'
reader = csv.reader(POST_FILE)
error_count = 0
curr = ''

def build_comments(comments, post_id):
    count = 0
    while count <= 3:
        count += 1
        for x in comments['data']:
            if 'message' in x:
                x['message'] = nltk.tokenize.word_tokenize(x['message'])
            comm_id = x['id']
            comm_dir = curr + os.sep + post_id + os.sep + comm_id
            filename = os.path.join(os.getcwd(), comm_dir)
            reactions = helpers.fetch_request(URL + comm_id + ACCESS_TOKEN + REACTS)
            replies = helpers.fetch_request(URL + comm_id + '/comments' + ACCESS_TOKEN)
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
            comments = helpers.fetch_request(comments['paging']['next'])
        except KeyError or False:
            break

def parse_posts(reader):
    for post in reader:
        if post[2] and post[2] != 'id' and post[0] and int(post[0][:4]) > 2015:
            global curr
            if curr != post[2].split('_')[0]:
                curr = post[2].split('_')[0]
            post_id = post[2]
            post_dir = 'comments' + os.sep + curr + os.sep + post_id
            filename = os.path.join(os.getcwd(), post_dir)
            print(filename)
            if not os.path.isdir(filename):
                try:
                    reactions = helpers.fetch_request(URL + post_id + ACCESS_TOKEN + REACTS)
                    post = helpers.fetch_request(URL + post_id + ACCESS_TOKEN)
                    comments = helpers.fetch_request(URL + post_id + '/comments' + ACCESS_TOKEN)
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
