import os, sys, csv, re, helpers, atexit

ACCESS_TOKEN = helpers.ACCESS_TOKEN
URL = helpers.URL
error_count = 0

def init_csv():
    pages = open(os.path.join(os.path.dirname(sys.argv[0]), 'page_ids.csv'))
    write_file = open('post_ids.csv', 'a')
    reader = csv.reader(pages)
    writer = csv.writer(write_file)
    writer.writerow(['created_time', 'message', 'id'])
    return reader, writer, pages, write_file

def fetch_posts(data, writer):
    while 'next' in data['paging'] and not re.match(r'^2016-01', data['data'][0]['id']):
        for post in data['data']:
            try:
                writer.writerow(
                    [post['created_time'].encode('utf-8'), post['message'].encode('utf-8'), post['id'].encode('utf-8')])
            except Exception as inst:
                writer.writerow([post['created_time'].encode('utf-8'), '', post['id'].encode('utf-8')])
        data = helpers.fetch_request(data['paging']['next'])
        if not data:
            break

def parse_pages():
    reader, writer, pages, write_file = init_csv()
    for row in reader:
        if row[0] and re.match(r'^http', row[0] and row[0] not in helpers.visited):
            page_id = re.search('(?:https?:\/\/)?(?:www\.)?facebook\.com\/(?:.+\/)*([\w\.\-]+)', row[0])
            data = helpers.fetch_request(URL + page_id + '/posts?limit=100' + ACCESS_TOKEN)
            print('Fetching posts for ' + page_id)
            fetch_posts(data, writer)
            helpers.visited[row[0]] = True
    write_file.close()

atexit.register(helpers.save_progress)

parse_pages()
