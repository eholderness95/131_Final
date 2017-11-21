import requests
import os, sys, csv

ACCESS_TOKEN = '?access_token=551947191811091|aWKc4qfL6ZaUh8TQopALlxlN2Fs'
URL = 'https://graph.facebook.com/'


with open(os.path.join(os.path.dirname(sys.argv[0]),'page_ids.csv')) as pages, open('post_ids.csv','a') as write_file:
    reader = csv.reader(pages)
    writer = csv.writer(write_file)
    writer.writerow(['created_time','message','id'])
    for row in reader:
        if row[1] and row[1] != 'ID':
            page_id = row[1]
            posts = requests.get(URL + page_id + '/feed' + ACCESS_TOKEN)
            data = posts.json()
            print(row[0])
            cursor = 1
            while cursor <= 30 and 'next' in data['paging']:
                for post in data['data']:
                    try:
                        writer.writerow([post['created_time'].encode('utf-8'),post['message'].encode('utf-8'),post['id'].encode('utf-8')])
                    except Exception as inst:
                        writer.writerow([post['created_time'].encode('utf-8'),'',post['id'].encode('utf-8')])
                cursor += 1
                posts = requests.get(data['paging']['next'])
                data = posts.json()
            with open('completed_pages.csv', 'a') as completed:
                writer2 = csv.writer(completed)
                writer2.writerow([row[1]])
                completed.close()
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
