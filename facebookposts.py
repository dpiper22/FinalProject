import facebook
import requests
import unittest
import json
import sqlite3
from datetime import datetime
import collections
import itertools
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import facebook_info

#facebook_info file includes access token, secret token, and facebook id required for getting data from Facebook


#David Piper

fbaccess_token = facebook_info.user_token
fb_profile = facebook_info.facebook_id



CACHE_FNAME = "FinalProjposts206_cache.json"


try:
	cache_file = open(CACHE_FNAME, 'r') #attempts to open data from file
	cache_data = cache_file.read() #turns data to string
	cache_file.close() #closes file since we have string
	CACHE_DICTION = json.loads(cache_data) #puts data in dictionary
except:
	CACHE_DICTION = {}

#finding data on my last 100 posts on facebook

fb_site = "https://graph.facebook.com/v2.11/" + fb_profile + "/posts"
url_params = {}
url_params['access_token'] = fbaccess_token
url_params['limit'] = 100


def get_user_posts(user):
	if user in CACHE_DICTION:
		print('using cache data')
		posts = CACHE_DICTION[user] #gets data from facebook
	else:
		print('getting data')
		posts = requests.get(fb_site, params= url_params)
		CACHE_DICTION[user] = json.loads(posts.text)
		json_dump = json.dumps(CACHE_DICTION)
		f = open(CACHE_FNAME, 'w')
		f.write(json_dump)
		f.close()#opens file, writes to it, and closes it
	return posts
#returns the data retrieved from facebook

my_posts = get_user_posts(fb_profile)



conn = sqlite3.connect('FinalProjPosts.sqlite')
cur = conn.cursor()
cur.execute('DROP TABLE IF EXISTS Posts')
cur.execute('CREATE TABLE Posts (day_of_week TEXT, time_of_day TEXT, created_time DATETIME)')
#creates table to put in data on what day of week and time of day that my posts are at
post_time = {}
post_time['Middle_of_night'] = 0
post_time['Morn'] = 0
post_time['after'] = 0
post_time['nt'] = 0
#create dictionary to count most popular time to post to facebook. Used for my visualization

for post in my_posts["data"]:
	times = post['created_time']#used to access the data and find time of posts
	times = datetime.strptime(times, "%Y-%m-%dT%H:%M:%S%z")#converts the data to datetime format
	day_of_the_week = datetime.strftime(times, "%A")#finds weekday from the data
	time_during_day = int(datetime.strftime(times, '%H%M'))#changes time to integer to split up time by time of day
	which_time = ""
	if time_during_day >=0 and time_during_day <= 359:#adds to table if the time is between midnight and 3:59am
		which_time = "Middle of Night"
		post_time['Middle_of_night'] += 1#counts to dictionary based on time range
	elif time_during_day >= 359 and time_during_day <= 1159:
		which_time = "Morning"
		post_time['Morn'] += 1
	elif time_during_day >= 1200 and time_during_day <= 1899:
		which_time = "Afternoon"
		post_time['after'] += 1
	else:
		which_time = "Night"
		post_time['nt'] += 1
	cur.execute("INSERT INTO Posts (day_of_week, time_of_day, created_time) VALUES (?,?,?)", (day_of_the_week, which_time, times))#indexes the data and adds information to the table based on what time of day posts were at 
conn.commit()

#visulatization 1: creates a bar graph to easily display my most popular time to make facebook posts (Middle_of_night)
trace = go.Bar( x = ["Middle of Night","Morning", "Afternoon", "Night"], y = [post_time['Middle_of_night'], post_time['Morn'], post_time['after'], post_time['nt']])
data = [trace]
py.iplot(data)

#https://plot.ly/~dpiper24/72.embed?share_key=My9cvhg4W1wsaJtQ6EqIRO
