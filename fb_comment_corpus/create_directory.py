import os, csv, sys, errno, json, helpers, atexit

ACCESS_TOKEN = helpers.ACCESS_TOKEN
URL = helpers.URL
POST_FILE = open('post_ids.csv', 'r')
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
        parent_dir = 'comments' + os.sep + curr + os.sep + post_id
        for x in comments['data']:
            if 'created_time' in x:
                x['created_time'] = helpers.process_timestamp(x['created_time'])
            comm_id = x['id']
            comm_dir = parent_dir + os.sep + comm_id
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

def parse_posts():
    for post in reader:
        if post[2] and post[2] != 'id' and post[0] and post[2] not in helpers.visited:
            helpers.visited[post[2]] = True
            global curr
            if curr != post[2].split('_')[0]:
                curr = post[2].split('_')[0]
                helpers.visited[curr] = True
            post_id = post[2]
            post_dir = 'comments' + os.sep + curr + os.sep + post_id
            filename = os.path.join(os.getcwd(), post_dir)
            helpers.working_on(post_dir)
            if not os.path.isdir(filename):
                try:
                    reactions = helpers.fetch_request(URL + post_id + ACCESS_TOKEN + REACTS)
                    post = {'created_time': post[0], 'id': post[2], 'message': post[1]}
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
    prompt_for_continue()

def prompt_for_continue():
    print('Corpus successfully created!')
    while True:
        reply = input('Would you like to populate a Mongo database with the data now? y/n\n').lower()
        if reply == 'y':
            while True:
                reply = input('Tokenize message content? y/n\n').lower()
                if reply == 'y' or reply == 'n':
                    if reply == 'y':
                        helpers.tokenize = True
                    break
                else:
                    print('Invalid reply. Please enter y or n\n')
            import populate_database
            populate_database.populate_database()
        elif reply.lower() == 'n':
            sys.exit()
        else:
            print('Invalid reply. Please enter y or n\n')

atexit.register(helpers.save_progress)
