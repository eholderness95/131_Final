import requests
import os, sys, csv, re, create_directory

ACCESS_TOKEN = '?access_token=551947191811091|aWKc4qfL6ZaUh8TQopALlxlN2Fs'
URL = 'https://graph.facebook.com/'
reader, writer, pages, write_file


def init_csv():
    global reader, writer, pages, write_file
    pages = open(os.path.join(os.path.dirname(sys.argv[0]), 'page_ids.csv'))
    write_file = open('post_ids.csv', 'a')
    reader = csv.reader(pages)
    writer = csv.writer(write_file)
    writer.writerow(['created_time', 'message', 'id'])


def fetch_posts(data):
    while 'next' in data['paging'] and not re.match(r'\b2015-10', data['data'][0]['id']):
        for post in data['data']:
            try:
                writer.writerow(
                    [post['created_time'].encode('utf-8'), post['message'].encode('utf-8'), post['id'].encode('utf-8')])
            except Exception as inst:
                writer.writerow([post['created_time'].encode('utf-8'), '', post['id'].encode('utf-8')])
        posts = requests.get(data['paging']['next'])
        data = posts.json()


def parse_pages():
    init_csv()
    for row in reader:
        if row[1] and row[1] != 'ID':
            page_id = row[1]
            data = create_directory.fetch_request(URL + page_id + '/feed?limit=100' + ACCESS_TOKEN)
            print(row[0])
            fetch_posts(data)
            with open('completed_pages.csv', 'a') as completed:
                writer2 = csv.writer(completed)
                writer2.writerow([row[1]])
                completed.close()
    write_file.close()


parse_pages()
