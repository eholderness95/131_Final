import os, sys, csv, re, requests

ACCESS_TOKEN = '?access_token=551947191811091|aWKc4qfL6ZaUh8TQopALlxlN2Fs'
URL = 'https://graph.facebook.com/'
error_count = 0

def fetch_request(url):
    try:
        data = requests.get(url).json()
        global error_count
        if 'error' in data and error_count < 10:
            print(data)
            if data['error']['code'] == 4 or data['error']['code'] == 341:
                print('Access limit reached for current token. Getting a new one')
                global current_token
                if current_token < len(ACCESS_TOKEN) - 1:
                    current_token += 1
                else:
                    print('Reached end of token list. Cycling back to top.')
                    current_token = 0
            elif data['error']['code'] == 100:
                print('ouch')
                error_count = 0
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
        data = fetch_request(data['paging']['next'])
        if not data:
            break


def parse_pages():
    reader, writer, pages, write_file = init_csv()
    for row in reader:
        if row[1] and row[1] != 'ID':
            page_id = row[1]
            data = fetch_request(URL + page_id + '/posts?limit=100' + ACCESS_TOKEN)
            print(row[0])
            fetch_posts(data, writer)
            with open('completed_pages.csv', 'a') as completed:
                writer2 = csv.writer(completed)
                writer2.writerow([row[1]])
                completed.close()
    write_file.close()


parse_pages()
