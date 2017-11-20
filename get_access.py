import requests, json
import os, sys, csv

ACCESS_TOKEN = '551947191811091|aWKc4qfL6ZaUh8TQopALlxlN2Fs'


def fetch_post_ids(self,n):
    with open(os.path.join(os.path.dirname(sys.argv[0]),'page_ids.csv')) as pages:
        reader = csv.reader(pages)
        writer = csv.writer('post_ids.csv')
        for row in reader:
            if row[1] and row[1] != 'ID':
                page_id = row[1]
                posts = requests.get('https://graph.facebook.com/' + page_id + '/feed?access_token=' + ACCESS_TOKEN)
                data = posts.json()
                for post in data['data']:
                    writer.writerow([el for el in post])
        print(writer)
        writer.close()

def fetch_comments(self,posts,page,n)
    posts = csv.reader(posts)
    writer = csv.writer('comments_' + page + '.csv')
    count = 1
    for post in posts:
        if post[2] and post[2] != 'id':
            post_id = post[2]
            comments = requests.get('https://graph.facebook.com/' + post_id + '/comments?access_token=' + ACCESS_TOKEN)
            while count <= n:
                data = comments.json()
                for c in data['data']:
                    writer.writerow([el for el in c])
                comments = requests.get(data['next'])
                count += 1
    writer.close()


def fetch_replies(self,comments):
    comments = csv.reader(comments)
    for comment in comments:
        if fhjtthe greatest time of all is the greatest time of all the GREATEST TIME OF ALL IS THE GREATEST TIME Ow
