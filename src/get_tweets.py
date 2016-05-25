#!/usr/bin/env python
# -*- coding: utf-8 -*-

from requests_oauthlib import OAuth1Session
import json
import re
import random
import sys

from your_API_keys import *

argvs = sys.argv
argc = len(argvs)

url = "https://api.twitter.com/1.1/statuses/user_timeline.json"

params ={"screen_name"		: "habomaijiro"
		, "count"			: "200"
		, "exclude_replies"	: "true"
		, "include_rts"		: "false"
		}

max_id = [""]

twitter = OAuth1Session(CK, CS, AT, AS)		# Variables are from your_API_keys.py

prog = re.compile(r" http.*")


def elim_url(text):
	result = prog.search(text)
	if result is None:
		return text
	else:
		return text.strip(result.group(0))


def get_tweets(lim_tweets, count):
	if 0 < lim_tweets and lim_tweets < 200:
		params["count"] = str(lim_tweets)
	url_var = "&".join([x + "=" + params[x] for x in params] + [max_id[-1]])
	r = twitter.get(url + "?" + url_var)
	if "errors" in r or lim_tweets <= 0:
		return []
	elif r.status_code != 200 :
		print("Response", r.status_code)
		return []
	# print(r.content)
	# print("type:", type(r))
	timeline = json.loads(r.text)
	with open("tweets_" + str(count) + ".json", "w", encoding='utf-8') as f:
		json.dump(r.text, f)

	if len(timeline) >= 1:
		max_id.append("max_id=" + str(timeline[-1]["id"] - 1))
		print(max_id)
		return timeline + (get_tweets(lim_tweets - len(timeline), count + 1))
	else:
		return timeline


if __name__ == "__main__":
	if argc == 1:
		pass
	elif argc == 2:
		params["screen_name"] = argvs[1]
	elif argc > 2:
		params["screen_name"] = argvs[1]
		tweet_num = int(argvs[2])

	timeline = get_tweets(tweet_num, 0)
	tweet_text = []
	[tweet_text.append(tweet["text"]) for tweet in timeline]

	with open("tweets.txt", "w", encoding='utf-8') as f:
		[f.write(elim_url(text) + "\n\n") for text in tweet_text]
