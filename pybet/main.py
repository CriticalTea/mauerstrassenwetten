import praw
import json
import redditbets
import sys


settings_path = 'settings.json'
with open(settings_path, 'r') as f:
    settings = json.load(f)

reddit = praw.Reddit(
    client_id=settings['appid'],
    client_secret=settings['secret'],
    password=settings['password'],
    user_agent="testscript by u/Critical_Tea_1337",
    username=settings['username']
)

reddit.validate_on_submit = True

json_path = sys.argv[1]
redditbets.process_bets(reddit, json_path)