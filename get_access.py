import requests, json
import os, sys, csv

ACCESS_TOKEN = '?access_token=EAAH1ZCjhNfBMBAFFvwhTRZAljgYCfrZBuPZCalNdauhyBFMfUEWAMiYMYIzhBdWZBE2GwJpECBMG0ICHZA9FZChGq3ZAlbXvy9RfLncZBF2K66LIH15hzOqzkJwJj4m4waCrKQKZAmdUW7GaqRefpSUbqFYgZCEFCyuCORgBmj1jOdFSaqJyJqklLQLxx3eejZBTFfYZD'
URL = 'https://graph.facebook.com/'

# def fetch_post_ids(self,n):

with open(os.path.join(os.path.dirname(sys.argv[0]),'page_ids.csv')) as pages:
    with open('post_ids.csv','w') as write_file:
        reader = csv.reader(pages)
        writer = csv.writer(write_file)
        for row in reader:
            if row[1] and row[1] != 'ID':
                page_id = row[1]
                posts = requests.get(URL + page_id + '/feed' + ACCESS_TOKEN)
                cursor = 1
                while cursor <= 30:
                    data = posts.json()
                    for post in data['data']:
                        writer.writerow([el for el in post])
                    cursor += 1
                    posts = requests.get(data['paging']['next'])
        write_file.close()


# def fetch_comments(self,posts,page,n)
#     posts = csv.reader(posts)
#     writer = csv.writer('comments_' + page + '.csv')
#     count = 1
#     for post in posts:
#         if post[2] and post[2] != 'id':
#             post_id = post[2]
#             comments = requests.get(URL + post_id + '/comments' + ACCESS_TOKEN)
#             while count <= n:
#                 data = comments.json()
#                 for c in data['data']:
#                     writer.writerow([el for el in c])
#                 comments = requests.get(data['next'])
#                 count += 1
#     writer.close()
#
#
# def fetch_replies(self,comments):
#     comments = csv.reader(comments)
#     for comment in comments:
#
