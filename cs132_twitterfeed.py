import json
import math
import os
import platform
import random
import signal
import socketserver
import subprocess


# took from PromptUtils for portability
GREEN = '\033[92m'
RED = '\033[91m'
END = '\033[0m'


def print_green(msg):
    """
    Print a pretty green message to stdout

    Args:
        msg: A string to print in color
    Returns:
        None
    """
    print("%s%s%s" % (GREEN, msg, END))


def print_red(msg):
    """
    Print a pretty red message to stdout

    Args:
        msg: A string to print in color
    Returns:
        None
    """
    print("%s%s%s" % (RED, msg, END))


# Install dependencies
DEV_NULL = open(os.devnull, 'w')


def install_if_not_exists(package_name):
    if subprocess.call(["pip3", "show", package_name], stdout=DEV_NULL):
        print_green("[OK] installing %s" % package_name)
        subprocess.call(["pip3", "install", "--upgrade", package_name])
    else:
        print_green("[OK] %s has been installed" % package_name)


install_if_not_exists("setuptools")
install_if_not_exists("wheel")
install_if_not_exists("bs4")
install_if_not_exists("selenium")



import sys
import threading
import urllib.parse
from collections import deque
from http.server import BaseHTTPRequestHandler

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# Fetch tweets
tweets = deque(maxlen=10000)
tweets_ids = set()

topic = 'pizza'
twitter_url = 'https://twitter.com/'
request_url = 'https://twitter.com/search?q=%s'


argc = len(sys.argv)

if argc == 1:
    print_green("[OK] Topic default to %s" % topic)
elif argc == 2:
    topic = sys.argv[1]

    if topic.strip() == "-h":
        print_red("Usage: cs132_twitterfeed <topic>")
        sys.exit(0)
else:
    print_red("ERROR: Correct Usage: cs132_twitterfeed <topic>")
    sys.exit(1)
print_green("[OK] Pulling tweets about %s" % topic)


def determine_os():
    os = platform.system().lower()

    if os == 'linux':
        return 'linux'
    elif os == 'darwin':
        return 'mac'
    else:
        sys.exit('unsupported os type %s' % os)

chromedriver_path = "%s/chromedriver_%s" % (os.getcwd(), determine_os())


def make_soup(quiet=True):
    options = Options()
    options.headless = quiet
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
    driver.implicitly_wait(10)
    driver.get(request_url % urllib.parse.quote_plus(topic))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    return soup


def cook_soup(soup):
    return [parse_tweet(tweet_html) for tweet_html in soup.find_all('div', class_='tweet')]


def user_url(user_screen_name):
    return twitter_url + user_screen_name


def parse_tweet(tweet_html):
    """
    each tweet is in class tweet
    properties:
        created_at: a.tweet_timestamp title; span._timestamp data-time
        id: div.tweet data-item-id
        id_str: str(id)
        text: p.tweet-text
        user: a.account-group
        entities
    """
    tweet = {}
    user = {}
    created_at_hr = tweet_html.select('a.tweet-timestamp')[0]['title'] # human readable
    created_at_htc = tweet_html.select('span._timestamp')[0]['data-time']
    id_str = tweet_html['data-item-id']
    id = int(id_str)
    text_section = tweet_html.select('p.tweet-text')[0]
    text = text_section.text
    text_with_html_tags = ''.join(str(tag) for tag in text_section.contents)

    user_id_str = tweet_html['data-user-id']
    user_id = int(user_id_str)
    user_name = tweet_html['data-name']
    user_screen_name = tweet_html['data-screen-name']
    user_profile_image_url_https = tweet_html.select('img.avatar')[0]['src']

    tweet['created_at'] = created_at_hr
    tweet['id'] = id
    tweet['id_str'] = id_str
    tweet['text'] = text
    tweet['tagged_text'] = text_with_html_tags
    tweet['user'] = user

    user['id'] = user_id
    user['id_str'] = user_id_str
    user['name'] = user_name
    user['screen_name'] = user_screen_name
    user['profile_image_url_https'] = user_profile_image_url_https
    user['url'] = user_url(user_screen_name)

    return tweet


def pull_tweets():
    count = 0

    for tweet in cook_soup(make_soup()):
        tid = tweet['id']

        if tid not in tweets_ids:
            tweets_ids.add(tid)
            tweets.append(tweet)
            count += 1
    print_green("[OK] %s new tweets has been pulled" % count)


def pack_tweets(num_tweets=26):  # enter the number of tweets you want
    desired_repeats = math.ceil(num_tweets / 10)
    picked_tweets = random.sample(tweets, min(num_tweets - desired_repeats, len(tweets)))
    picked_tweets.extend(random.sample(picked_tweets, desired_repeats))
    picked_tweets.sort(key=lambda tweet: tweet["created_at"])

    return json.dumps(picked_tweets)


fridge_dft = os.path.join(os.getcwd(), 'twitterfeed.json')


def packing(fridge=fridge_dft):
    defrost(fridge)
    autoload()


def stop_packing(fridge=fridge_dft):
    t.cancel()
    print_green("[OK] stop making new soup")
    refridge(fridge)


def refridge(fridge=fridge_dft):
    with open(fridge, 'w+') as fdg:
        json.dump(list(tweets), fdg)
        print_green("[OK] soup has been put inside the fridge")


def defrost(fridge=fridge_dft):
    if os.path.isfile(fridge):
        print_green("[OK] defrost soup")

        if os.stat(fridge).st_size:
            with open(fridge, 'r') as fgd:
                tweets.extendleft(json.load(fgd))
    else:
        print_green("[OK] no soup in fridge, make fresh soup instead")


t = None


def autoload():
    global t
    pull_tweets()
    t = threading.Timer(10, autoload)
    t.daemon = True
    t.start()


class TweetsFeeder(BaseHTTPRequestHandler):
    def do_GET(self):
        print("<----- Request Start ----->")
        print("request_path :", self.path)
        print("self.headers :", self.headers)
        print("<----- Request End ------->\n")

        if self.path == '/feed/start':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            print_green("[OK] sending a pack of tweets")
            self.wfile.write(pack_tweets().encode())


def stop_server(sig, frame):
    # stop pulling new tweets
    stop_packing()
    signal.signal(signal.SIGINT, orig_sigint_handler)
    # shutdown the server
    print_green("[OK] server stopped")
    sys.exit(0)


# allow new tweets to be received
packing()

portnum = 8082
# try:
#     pid = subprocess.check_output(["lsof", "-t", "-i:%d" % portnum])
#     subprocess.call(["kill", pid])
#     print_green("[OK] Cleared process %d on %d" % (pid, portnum))
# except subprocess.CalledProcessError:
#     print_green("[OK] No process on %s" % portnum)

# start the server
print_green("[OK] Starting the server")
httpd = socketserver.TCPServer(("", portnum), TweetsFeeder)
print_green("[OK] Type CTRL-C to stop server")
orig_sigint_handler = signal.signal(signal.SIGINT, stop_server)
print_green("[OK] Server has been started")
print_green("[OK] Server is listening to http://localhost:%s/feed/start" % portnum)
httpd.serve_forever()
