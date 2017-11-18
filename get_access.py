import requests
# r = requests.get('https://graph.facebook.com/oauth/access_token?grant_type=client_credentials&client_id=123&client_secret=XXX')
# access_token = r.text.split('=')[1]
# print access_token

ACCESS_TOKEN = '551947191811091|aWKc4qfL6ZaUh8TQopALlxlN2Fs'
post_id = '5281959998_10151388128894999'
test = requests.get('https://graph.facebook.com/'+post_id+'/comments?access_token='+ACCESS_TOKEN)
print(test)