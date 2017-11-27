import requests
import os, sys, csv


ACCESS_TOKEN = '?access_token=302168603621143|gIhXZS2T0OJlKvLzp-KRMaMx0iM'
URL = 'https://graph.facebook.com/'
post_file = open('post_ids_test.csv', 'r')
reader = csv.reader(post_file)
n = 5

for post in reader:
     if post[2] and post[2] != 'id':
         post_id = post[2]
         write_file = open('comments_' + post_id + '.csv', 'a')
         writer = csv.writer(write_file)
         writer.writerow(['created_time','message','id'])
         comments = requests.get(URL + post_id + '/comments' + ACCESS_TOKEN)
         data = comments.json()
         count = 0
         while count <= 5:
             print(count)
             data = comments.json()
             count +=1
             for x in data['data']:
                 time = x['created_time']
                 comment = x['message']
                 comm_id = x['id']
                 d = [time, comment, comm_id]
                 writer.writerow(w for w in d)
             comments = requests.get(data['paging']['next'])


post_file.close()
write_file.close()
print("files closed")
