#!/usr/bin/env python

# Uses python2
import cPickle as pickle
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

now = datetime.now(tzlocal()).replace(microsecond=0)
day = timedelta(days=1)
# END datetime setup

FLAGS = gflags.FLAGS
APPNAME = "timeleft"
VERSION = "0.1"

FLOW = OAuth2WebServerFlow(
        client_id=settings.client_id,
        client_secret=settings.client_secret,
        scope='https://www.googleapis.com/auth/calendar.readonly',
        user_agent="{app}/{ver}".format(app=APPNAME,ver=VERSION),
        )

FLAGS.auth_local_webserver = False

def fetch():
    storage = Storage('calendar.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid == True:
        credentials = run(FLOW, storage)

    http = httplib2.Http()
    http = credentials.authorize(http)

    service = build(serviceName='calendar', version='v3', http=http,
            developerKey=settings.devkey)

    # Open previous calendar data if any
    prevtime = response = None
    try:
        with open(settings.events_file) as f:
            prevtime, response = pickle.load(f)
            
    except FileNotFoundError:
        pass

    # resync if it's been longer than a week, or nonexistent
    event_query = service.events().list(
            calendarId="theawesomenator@gmail.com",
            timeMin=now.isoformat(),
            timeMax=(now + 7*day).isoformat(),
            fields="items(end,start,summary)",
            maxResults=settings.numevents,
            singleEvents="true",
            )

    response = event_query.execute()
    

    return response
