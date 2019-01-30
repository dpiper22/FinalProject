#David Piper

import unittest
import itertools
import collections
import facebook_info
import datetime
import csv
import json
import sqlite3
import requests
import facebook
import webbrowser
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
import plotly.plotly as py
import plotly.graph_objs as go


fb_id     = facebook_info.access_token
fb_secret = facebook_info.secret_token
facebook_session = False

CACHE_FNAME = "FinalProj206_cache.json"

#creates Cache file
try:
	cache_file = open(CACHE_FNAME, 'r') #attempts to open data from file
	cache_data = cache_file.read() #turns data to string
	cache_file.close() #closes file since we have string
	CACHE_DICTION = json.loads(cache_data) #puts data in dictionary
except:
	CACHE_DICTION = {}

#attempts to upload to cache information gathered from facebook on comments and posts

def get_facebook_data(user):
	fb_site = "https://graph.facebook.com/v2.8/" + fb_secret + "/comments" + "/posts" + "/feed"
	site_params = {}
	site_params["access_token"]= fb_id
	site_params["limit"] = 100
	if user in CACHE_DICTION:
		print('using cache data')
		facebook_data = CACHE_DICTION[user]
	else:
		print('getting data')
		facebook_data = requests.get(fb_site, params = site_params)
		CACHE_DICTION[user] = json.loads(facebook_data.text)
		json_dump = json.dumps(CACHE_DICTION)
		f = open(CACHE_FNAME, 'w')
		f.write(json.dump)
		f.closer
	return facebook_data




#Referenced from https://requests-oauthlib.readthedocs.io/en/latest/examples/facebook.html, used for oauth and allows user to either be directed to facebook for authorization or requests a confirmation link from facebook

def makeFacebookRequest(baseURL, params = {}):
    global facebook_session
    if not facebook_session:
        authorization_base_url = 'https://www.facebook.com/dialog/oauth'
        token_url = 'https://graph.facebook.com/oauth/access_token'
        redirect_uri = 'https://www.programsinformationpeople.org/runestone/oauth'

        scope = ['user_posts','pages_messaging', 'user_managed_groups','user_status','user_likes']
        facebook = OAuth2Session(fb_id, redirect_uri=redirect_uri, scope=scope)
        facebook_session = facebook_compliance_fix(facebook)
#directs user to facebook for authorization
        authorization_url, state = facebook_session.authorization_url(authorization_base_url)
        print('Opening browser to {} for authorization'.format(authorization_url))
        webbrowser.open(authorization_url)
#gets authorization code from callback url
        redirect_response = input('Paste the full redirect URL here: ')
        facebook_session.fetch_token(token_url, client_secret=fb_secret, authorization_response=redirect_response.strip())

    return facebook_session.get(baseURL, params=params)

fb_response = makeFacebookRequest("https://graph.facebook.com/me")
current_user = json.loads(fb_response.text)


#gets data on who has commented on my posts and who has liked them


class Post():
    """object representing status update"""
    def __init__(self, post_dict={}):
    	self.id = post_dict['id']
    	if 'message' in post_dict:
    		self.message = post_dict['message']
    	else:
    		self.message = ""
    	if 'comments' in post_dict:
    		self.comments = post_dict['comments']['data']
    		self.numb_comments = len(post_dict['comments']['data'])
    	else:
    		self.comments = []
    		self.numb_comments = 0
    	if 'likes' in post_dict:
    		self.likes = post_dict['likes']['data']
    		self.numb_likes = len(post_dict['likes']['data'])
    	else:
    		self.likes = []
    		self.numb_likes = 0

baseurl = 'https://graph.facebook.com/me/feed?fields=comments,likes,message,created_time'
get_url = makeFacebookRequest(baseurl,params = {'limit':100})
my_posts = json.loads(get_url.text)
post_insts = [Post(x) for x in my_posts['data']]

#creates a dictionary to track who has liked and commented on my posts and how many times
whoLikes = {}
whoCom = {}
for x in post_insts:
    #print(x.message + " gg")
    for y in x.likes:
        if y['name'] not in whoLikes:
            whoLikes[y['name']] = 1
        else:
            whoLikes[y['name']] += 1
    for z in x.comments:
        if z['from']['name'] not in whoCom:
            whoCom[z['from']['name'] ] = 1
        else:
            whoCom[z['from']['name'] ] += 1




#makes a list for both dictionaries to sort who has liked and commented the most
#used lists for my two visualizations

top_likers = sorted(whoLikes, key = lambda x: whoLikes[x], reverse = True)[:100]
likers_likes = sorted(whoLikes.values(), reverse = True)

top_thirty = top_likers[:99]
top_ty = likers_likes[:99]

top_commenters = sorted(whoCom, key = lambda x: whoCom[x], reverse = True)[:100]
commenters_comments = sorted(whoCom.values(), reverse = True)

top_hundred = top_commenters[:99]
top_hund = commenters_comments[:99]

#adds people to both dictionaries that have zero likes but some comments and vice versa
for x in whoCom.keys():
	if x not in whoLikes:
		whoLikes[x]= 0

for x in whoLikes.keys():
	if x not in whoCom:
		whoCom[x]= 0

#outfile.close()
conn = sqlite3.connect('FinalProj206.sqlite')
cur = conn.cursor()
cur.execute('DROP TABLE IF EXISTS Commenters')
cur.execute('CREATE TABLE Commenters (name TEXT, user_comments INTEGER, user_likes INTEGER, PRIMARY KEY(name))')
#created table to put data in
comm = whoCom.items()
for x in whoCom:
	cur.execute("INSERT INTO Commenters VALUES(?,?,?)", [x, int(whoCom[x]), int(whoLikes[x])])
conn.commit()

conn.close()

#created two visualizations. Both bar graphs to display who has liked my posts the most, and who has commented the most

trace = go.Bar( x = top_thirty, y = top_ty)
data = [trace]
py.iplot(data)
#https://plot.ly/~dpiper24/66.embed?share_key=XdO8OUDJjbTIjobgauAQaG

tr = go.Bar(x = top_hundred, y = top_hund)
dat = [tr]
py.iplot(dat)
#https://plot.ly/~dpiper24/68.embed?share_key=Y6ArGbMvGp865y1yLTAiRt
