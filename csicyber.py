from flask import Flask, render_template, request
import datetime
import time
import math
import flickrapi
import os
from instagram import client
import requests
from requests_oauthlib import OAuth1
import collections
import threading

access_token = "d0b0b05538324a10872e96838a6abcf7"
client_secret = "4957bf5869c64b8f83b06a324eda47c6"
api_key = u'9f540d9ff504c85b5671cba0633ed6a7'
api_secret = u'dadb5aec1d774c14'
api = client.InstagramAPI(client_id=access_token, client_secret=client_secret)
flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')

REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize?oauth_token="
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"

CONSUMER_KEY = "N97glwGwnbLam0Dk6ADu4CpjZ"
CONSUMER_SECRET = "nB1Gd62AnovBOSxT8di6fD6KdbgZCZ2qHtarXRDRPewmKESNQk"

OAUTH_TOKEN = "3052057706-INBNLbN3yBB0LClhW6EfeQtbUrT4tZxQwJJl5w5"
OAUTH_TOKEN_SECRET = "k6EmLPJTwNmgKBF1CULLuuJf9vrd6aw8kJfSenLM2UCTq"

app = Flask(__name__)


def convert(data):
    if isinstance(data, basestring):
        return str(data.encode('utf-8'))
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data


def get_oauth():
    oauth = OAuth1(CONSUMER_KEY,
                   client_secret=CONSUMER_SECRET,
                   resource_owner_key=OAUTH_TOKEN,
                   resource_owner_secret=OAUTH_TOKEN_SECRET)
    return oauth



def insta_target(count,lat,lon,distance,unix_start,unix_end,photos=[]):
    media_search = api.media_search(count=count, lat=lat, lng=lon, distance=distance, min_timestamp=unix_start,
                                        max_timestamp=unix_end)
    for media in media_search:
        item = {}
        item['image'] = media.get_standard_resolution_url()
        if item['image'].endswith('.mp4') == False:
            item['url'] = media.link
            photos.append(item)



def flickr_target(lat,lon,unix_start,unix_end,count,photos=[]):
    flickr_search = flickr.photos.search(lat=lat, lon=lon, min_taken_date=unix_start,
                                             max_taken_date=unix_end, per_page=count)
    for media in flickr_search['photos']['photo']:
        item = {}
        item['image'] = "https://farm%s.staticflickr.com/%s/%s_%s.jpg" % (
                media['farm'], media['server'], media['id'], media['secret'])
        item['url'] = "https://www.flickr.com/photos/%s/%s" % (media['owner'], media['id'])
        photos.append(item)


def twitter_target(lat,lon,start_date,end_date,photos=[]):
    print "enter twitter request"
    oauth = get_oauth()
    print "after oauth"
    request_url="https://api.twitter.com/1.1/search/tweets.json?q=twitpic.com%20OR%20yfrog.com%20OR%20photo&geocode="+lat+","+lon+","+"1mi&count=100&since="+start_date+"&until="+end_date
    print request_url
    r = requests.get(url=request_url, auth=oauth)
    print "after request"
    out_data=r.json()
    print out_data
    result=convert(out_data)
    print "after convert"
    for pic in result['statuses']:
        if('media' in pic['entities']):
            item={}
            item['image']=pic['entities']['media'][0]['media_url']
            item['url']=pic['entities']['media'][0]['expanded_url']
            photos.append(item)



def validate_date(start_date, end_date):
    try:
        print start_date
        datetime.datetime.strptime(start_date, "%Y-%m-%d")
        datetime.datetime.strptime(end_date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_time(start_time, end_time):
    try:
        print start_time
        time.strptime(start_time, '%H:%M')
        time.strptime(end_time, '%H:%M')
        return True
    except ValueError:
        return False


def validate_lat_lon(lat, lon):
    try:
        float(lat)
        float(lon)
        return True
    except ValueError:
        return False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search/', methods=["POST"])
def search():
    lat = request.form['latitude'].strip()
    lon = request.form['longitude'].strip()
    start_date = request.form['start_date'].strip()
    end_date = request.form['end_date'].strip()
    start_time = request.form['start_time'].strip()
    end_time = request.form['end_time'].strip()
    errors = ""
    print "before validation"
    if not lat or not lon or not start_date or not end_date or not start_time or not end_time:
        errors = "Please enter all the fields"
    if not errors:
        if not validate_date(start_date, end_date) or not validate_time(start_time, end_time) or not validate_lat_lon(
                lat, lon):
            errors = errors + "Please enter valid data"
            print "inside val functions"
    if not errors:
        print "pristine"
        string_start_date = start_date + " " + start_time
        print string_start_date
        string_end_date = end_date + " " + end_time
        print string_end_date
        sdt = datetime.datetime.strptime(string_start_date, "%Y-%m-%d %H:%M")
        print sdt
        edt = datetime.datetime.strptime(string_end_date, "%Y-%m-%d %H:%M")
        print edt
        unix_start = math.trunc(time.mktime(sdt.timetuple()))
        unix_end = math.trunc(time.mktime(edt.timetuple()))
        photos=[]
        t1 = threading.Thread(name='insta_service', target=insta_target(100,lat,lon,1000,unix_start,unix_end,photos))
        t2 = threading.Thread(name='flickr_service', target=flickr_target(lat,lon,unix_start,unix_end,100,photos))
        t3 = threading.Thread(name='twitter_service', target=twitter_target(lat,lon,start_date,end_date,photos))
        t1.start()
        t2.start()
        t3.start()
        return render_template('search.html', result=photos)
    else:
        return render_template('index.html', validations=errors)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
