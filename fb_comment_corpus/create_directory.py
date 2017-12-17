import os
import re
import csv
import sys
import json
import errno
import atexit
import helpers

ACCESS_TOKEN = '<ADD APP (PREFERRED) OR USER ACCESS TOKEN HERE>'
URL = 'https://graph.facebook.com/'
# Currently using the single-post solution from
# https://stackoverflow.com/questions/36906590/getting-facebook-post-all-reactions-count-in-single-graph-api-request
# Planning to change to batch solution at some point.
REACTS = '&fields=reactions.type(LIKE).limit(0).summary(total_count).as(like),' + \
         'reactions.type(LOVE).limit(0).summary(total_count).as(love),' + \
         'reactions.type(HAHA).limit(0).summary(total_count).as(haha),' + \
         'reactions.type(WOW).limit(0).summary(total_count).as(wow),' + \
         'reactions.type(SAD).limit(0).summary(total_count).as(sad),' + \
         'reactions.type(ANGRY).limit(0).summary(total_count).as(angry)&limit=10'
URL_REGEX = '(?:https?:\/\/)?(?:www\.)?facebook\.com\/(?:.+\/)*([\w\.\-]+)'
error_count = 0
curr = ''

# Open .csv of FB pages, create write file, create reader and writer objects for csv
def init_csv(filename):
    pages = open(os.path.join(os.path.dirname(sys.argv[0]), filename))
    write_file = open('post_ids.csv', 'a', encoding='utf8')
    reader = csv.reader(pages)
    writer = csv.writer(write_file)
    writer.writerow(['created_time', 'message', 'id'])
    return reader, writer, pages, write_file

# Parses .csv file of FB pages
def parse_pages(filename):
    reader, writer, pages, write_file = init_csv(filename)
    for row in reader:
        if row[0] and re.match(r'^http', row[0]) and row[0] not in helpers.visited:
            page_id = re.findall(URL_REGEX, row[0])[0]
            data = helpers.fetch_request(URL + page_id + '/posts' + ACCESS_TOKEN + '&limit=100')
            # Error checking for bad request....
            if not data:
                continue
            # Fetch all posts from 1/2016 onwards for the given FB page
            else:
                helpers.working_on(page_id)
                fetch_posts(data, writer)
                helpers.visited[row[0]] = True
    write_file.close()
    parse_posts()

# Fetches posts from FB page and writes to .csv file
def fetch_posts(data, writer):
    while 'next' in data['paging'] and int(data['data'][0]['created_time'][:4]) > 2015:
        for post in data['data']:
            # Checking for posts without message content....
            try:
                writer.writerow(
                    [helpers.process_timestamp(post['created_time']), post['message'], post['id']])
            except KeyError:
                writer.writerow([helpers.process_timestamp(post['created_time']), '', post['id']])
        data = helpers.fetch_request(data['paging']['next'])
        if not data:
            break

def parse_posts():
    post_file = open('post_ids.csv', 'r')
    reader = csv.reader(post_file)
    # Loop through all posts in .csv file
    for post in reader:
        if post[2] and post[2] != 'id' and post[0] and post[2] not in helpers.visited:
            # Add to visited dict in case of program interruption requiring restart
            helpers.visited[post[2]] = True
            global curr
            if curr != post[2].split('_')[0]:
                curr = post[2].split('_')[0]
                helpers.visited[curr] = True
            post_id = post[2]
            post_dir = 'comments' + os.sep + curr + os.sep + post_id
            filename = os.path.join(os.getcwd(), post_dir)
            helpers.working_on(post_dir)
            # Create a subdirectory for each post and output a JSON object for the post's content, saved one directory up
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

# Fetch top 100 comments for each post, saving each as a separate JSON object in the post's directory
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

def prompt_for_continue():
    print('Corpus successfully created!')
    if repeat_until_bool('Would you like to populate a Mongo database with the data now? y/n\n'):
        if repeat_until_bool('Tokenize message content? y/n\n'):
            helpers.tokenize = True
        import populate_database
        populate_database.populate_database()
    else:
        sys.exit()

def repeat_until_bool(prompt):
    while True:
        reply = input(prompt).lower()
        if reply == 'y':
            return True
        elif reply == 'n':
            return False
        else:
            print('Invalid reply. Please enter y or n\n')

# Save progress in case of premature program termination due to error
atexit.register(helpers.save_progress)
