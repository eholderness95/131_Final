import os, sys, csv, re, helpers, atexit

ACCESS_TOKEN = helpers.ACCESS_TOKEN
URL = helpers.URL
URL_REGEX = '(?:https?:\/\/)?(?:www\.)?facebook\.com\/(?:.+\/)*([\w\.\-]+)'
error_count = 0

def init_csv(filename):
    pages = open(os.path.join(os.path.dirname(sys.argv[0]), filename))
    write_file = open('post_ids.csv', 'a', encoding='utf8')
    reader = csv.reader(pages)
    writer = csv.writer(write_file)
    writer.writerow(['created_time', 'message', 'id'])
    return reader, writer, pages, write_file

def fetch_posts(data, writer):
    while 'next' in data['paging'] and int(data['data'][0]['created_time'][:4]) > 2015:
        for post in data['data']:
            try:
                writer.writerow(
                    [helpers.process_timestamp(post['created_time']), post['message'], post['id']])
            except Exception as inst:
                writer.writerow([helpers.process_timestamp(post['created_time']), '', post['id']])
        data = helpers.fetch_request(data['paging']['next'])
        if not data:
            break

def parse_pages(filename):
    reader, writer, pages, write_file = init_csv(filename)
    for row in reader:
        if row[0] and re.match(r'^http', row[0]) and row[0] not in helpers.visited:
            page_id = re.findall(URL_REGEX, row[0])[0]
            data = helpers.fetch_request(URL + page_id + '/posts' + ACCESS_TOKEN + '&limit=100')
            if not data:
                continue
            else:
                helpers.working_on(page_id)
                fetch_posts(data, writer)
                helpers.visited[row[0]] = True
    write_file.close()
    import create_directory
    create_directory.parse_posts()

atexit.register(helpers.save_progress)
