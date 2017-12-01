import requests
import os, sys, csv, errno, json

ACCESS_TOKEN = '?access_token=551947191811091|aWKc4qfL6ZaUh8TQopALlxlN2Fs'
URL = 'https://graph.facebook.com/'
post_file = open('post_ids.csv', 'r')
REACTS = '&fields=reactions.type(LIKE).limit(0).summary(total_count).as(like),reactions.type(LOVE).limit(0).summary(total_count).as(love),reactions.type(HAHA).limit(0).summary(total_count).as(haha),reactions.type(WOW).limit(0).summary(total_count).as(wow),reactions.type(SAD).limit(0).summary(total_count).as(sad),reactions.type(ANGRY).limit(0).summary(total_count).as(angry)&limit=10'
reader = csv.reader(post_file)
curr = ''

for post in reader:
    if post[2] and post[2] != 'id':
        if curr != post[2].split('_')[0]:
            curr = post[2].split('_')[0]
        post_id = post[2]
        reactions = requests.get(URL + post_id + ACCESS_TOKEN + REACTS).json()
        del reactions['id']
        post_data = {'data':requests.get(URL + post_id + ACCESS_TOKEN).json(),'reactions':reactions}
        post_dir = curr + os.sep + post_id + '.json'
        filename = os.path.join(os.getcwd(),post_dir)
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(filename, 'w') as post_obj:
            json.dump(post_data,post_obj,indent=4,sort_keys=True)
        comments = requests.get(URL + post_id + '/comments' + ACCESS_TOKEN)
        data = comments.json()
        count = 0
        while count <= 5:
            data = comments.json()
            count += 1
            for x in data['data']:
                comm_id = x['id']
                comm_dir = curr + os.sep + post_id + os.sep + comm_id
                filename = os.path.join(os.getcwd(),comm_dir)
                reactions = requests.get(URL + comm_id + ACCESS_TOKEN + REACTS).json()
                del reactions['id']
                content = {'data':x,'replies':requests.get(URL + comm_id + '/comments' + ACCESS_TOKEN).json()['data'],'reactions':reactions}
                if not os.path.exists(os.path.dirname(filename)):
                    try:
                        os.makedirs(os.path.dirname(filename))
                    except OSError as exc:  # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise
                with open(filename + '.json','w') as obj:
                    json.dump(content,obj,indent=4,sort_keys=True)
            comments = requests.get(data['paging']['next'])
