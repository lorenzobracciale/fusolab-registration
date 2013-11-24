import urllib2
from urllib import quote, urlencode
from base64 import b64encode
import json
import re
import os

CONSUMER_KEY = "" #put the consumer key here
CONSUMER_SECRET = "" #put the consumer secret here

BEARER_TOKEN_URL = " https://api.twitter.com/oauth2/token"
SEARCH_URL = "https://api.twitter.com/1.1/search/tweets.json"
SEARCH_TERM = "fusolab"

def deleteURLs(text):
    return re.sub(r'https?:\/\/[^ ]*', '', text)

def removeRT(text):
    return re.sub(r'^RT:?', '', text)

def removeSpace(text):
    return text.strip()

def clean(text):
    return re.sub(r'[.(_)-]', '', text)

def duepuntozero(text):
    return re.sub(r'2.0', 'due punto zero', text)

def chiocciola(text):
    #return re.sub(r'@', 'chiocciola ', text)
    return re.sub(r'@', '', text)

def cancelletto(text):
    #return re.sub(r'#', 'cancelletto ', text)
    return re.sub(r'#', '', text)

def mittente(text, name):
    username = re.sub(r'[ .(_)-]', '', name)
    return "Tuit da %s. %s" % (username, text)

def removeunicode(text):
    return text.encode('ascii', errors='ignore')

def isEmpty(text):
    return len(text) == 0

quoted_ck = quote(CONSUMER_KEY) 
quoted_cs = quote(CONSUMER_SECRET)
bearertoken = b64encode(quoted_ck + ":" + quoted_cs)

#print quoted_ck, quoted_cs, bearertoken

request = urllib2.Request(BEARER_TOKEN_URL)
request.add_data(urlencode({'grant_type':'client_credentials'})) 
request.add_header('Authorization', "Basic %s" % bearertoken)
request.add_header('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')
f = urllib2.urlopen(request)
j = json.loads(f.read())
access_token = j['access_token']

#print access_token

request = urllib2.Request(SEARCH_URL + "?result_type=recent&q=" + quote(SEARCH_TERM)) 
request.add_header('Authorization', "Bearer %s" % access_token)
f = urllib2.urlopen(request)
j = json.loads(f.read())
for status in j['statuses']:
    text = status['text'] 
    text = deleteURLs(text)
    text = removeRT(text)
    text = duepuntozero(text)
    text = chiocciola(text)
    text = cancelletto(text)
    text = clean(text)
    text = removeSpace(text)
    text = removeunicode(text)
    text = clean(text)
    text = mittente(text, status['user']['name'])
    if isEmpty(text):
        continue
    print text
    os.system("echo %s | /usr/bin/festival --tts" % text)



