#David Piper


import unittest
import itertools
import collections
import facebook_info
import json
import sqlite3
import requests
import facebook

fb_id     = facebook_info.access_token
fb_secret = facebook_info.secret_token


CACHE_FNAME = "FinalProj206.json"


try:
	cache_file = open(CACHE_FNAME, 'r') #attempts to open data from file
	cache_data = cache_file.read() #turns data to string
	cache_file.close() #closes file since we have string
	CACHE_DICTION = json.loads(cache_data) #puts data in dictionary
except:
	CACHE_DICTION = {}

fb_site = "https://graph.facebook.com/v2.8/" + fb_secret + "/comments"
site_params = {}
site_params["access_token"]= fb_id


