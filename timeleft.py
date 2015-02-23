#!/usr/bin/env python

# Uses python2
import gflags
import httplib2

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

import settings

# START datetime setup
from datetime import datetime, timedelta, tzinfo
from dateutil import parser
from dateutil.tz import *
class UTC(tzinfo):
    def utcoffset(self, dt):
        return timedelta(0)
    def dst(self, dt):
        return timedelta(0)
    def tzname(self,dt):
        return "UTC"

now = datetime.now(tzlocal()).replace(microsecond=0)
day = timedelta(days=1)
# END datetime setup

# START Google API service setup
FLAGS = gflags.FLAGS

appname = "timeleft"
version = "0.1"

FLOW = OAuth2WebServerFlow(
        client_id=settings.client_id,
        client_secret=settings.client_secret,
        scope='https://www.googleapis.com/auth/calendar.readonly',
        user_agent="{app}/{ver}".format(app=appname,ver=version),
        )

FLAGS.auth_local_webserver = False

storage = Storage('calendar.dat')
credentials = storage.get()
if credentials is None or credentials.invalid == True:
    credentials = run(FLOW, storage)

http = httplib2.Http()
http = credentials.authorize(http)

service = build(serviceName='calendar', version='v3', http=http,
        developerKey=settings.devkey)
# END Google API service setup


event_query = service.events().list(
        calendarId=settings.calendarID,
        timeMin=now.isoformat(),
        timeMax=(now + day).isoformat(),
        fields="items(end,start,summary)",
        maxResults="100",
        singleEvents="true",
        )

events = event_query.execute()
events = events['items'] if 'items' in events else None

if len(events) > 0:
    # sort the events by start time
    events = sorted(events, key=lambda item: item["start"]["dateTime"]) 
    nearest = events[0]
    start = parser.parse(nearest["start"]["dateTime"])
    end = parser.parse(nearest["end"]["dateTime"])
    nearest_time = start
    if start < now:
        nearest_time = end

    timeleft = nearest_time - now
    print("{time} until {event}".format(time=timeleft, event=nearest["summary"]))
else:
    print("No upcoming events")
    

