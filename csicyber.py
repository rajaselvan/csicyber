from flask import Flask, render_template, request
import datetime
import time
import math
import flickrapi
from instagram import client

access_token = "d0b0b05538324a10872e96838a6abcf7"
client_secret = "4957bf5869c64b8f83b06a324eda47c6"
api_key = u'9f540d9ff504c85b5671cba0633ed6a7'
api_secret = u'dadb5aec1d774c14'
api = client.InstagramAPI(client_id=access_token, client_secret=client_secret)
flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')

app = Flask(__name__)


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
        media_search = api.media_search(count=100, lat=lat, lng=lon, distance=1000, min_timestamp=unix_start,
                                        max_timestamp=unix_end)
        photos = []
        for media in media_search:
            item = {}
            item['image'] = media.get_standard_resolution_url()
            if item['image'].endswith('.mp4') == False:
                item['url'] = media.link
                photos.append(item)

        flickr_search = flickr.photos.search(lat=lat, lon=lon, min_taken_date=unix_start,
                                             max_taken_date=unix_end, per_page='100')
        for media in flickr_search['photos']['photo']:
            item = {}
            item['image'] = "https://farm%s.staticflickr.com/%s/%s_%s.jpg" % (
                media['farm'], media['server'], media['id'], media['secret'])
            item['url'] = "https://www.flickr.com/photos/%s/%s" % (media['owner'], media['id'])
            photos.append(item)

        return render_template('search.html', result=photos)
    else:
        return render_template('index.html', validations=errors)


if __name__ == '__main__':
    app.run()
