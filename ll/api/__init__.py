# This file is part of Living Labs Challenge, see http://living-labs.net.
#
# Living Labs Challenge is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Living Labs Challenge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Living Labs Challenge. If not, see <http://www.gnu.org/licenses/>.

import os
import time
import rollbar
import rollbar.contrib.flask
import atexit
import datetime
from flask import Flask, g
from flask.ext.restful import Api, abort
from flask_limiter import Limiter
from flask import got_request_exception
from apscheduler.schedulers.background import BackgroundScheduler

from .. import core
from apiutils import ApiResource, ContentField

from ll.core.db import db
from ll.core.config import config
from ll.core.user import send_email,get_user

def db_cleanup():
   print "Database cleanup task started"
   age_threshold = datetime.datetime.now() - datetime.timedelta(days=config["RUN_AGE_THRESHOLD_DAYS"])

   # Get list of all queries
   q = {"deleted": {"$ne": True}}
   queries = [query for query in db.query.find(q)]

   for query in [queries]:
       allruns = query["runs"].items()
       for userid, runid_pair in allruns:
           # Check if runid is paired with a timestamp (new format)
           if isinstance(runid_pair,list):
               runid, run_modified_time = runid_pair
               if 'doclist_modified_time' in query:
                   print "Run modified time: " + str(run_modified_time)
                   print "Doclist modified time: " + str(query['doclist_modified_time'])
                   if run_modified_time < query['doclist_modified_time'] :
                       print("Run older than latest doclist, send email: ", runid, run_modified_time)
                       run_user = get_user(userid)
                       run_email = run_user["email"]
                       run_teamname = run_user["teamname"]
                       send_email({'email':run_email,'teamname':run_teamname}, "Your run " + runid + " is older than the corresponding doclist.", "Old run")

                       continue
               if run_modified_time < age_threshold:
                   print("Run older than threshold, send e-mail: ", runid, run_modified_time)
                   run_user = get_user(userid)
                   run_email = run_user["email"]
                   run_teamname = run_user["teamname"]
                   send_email({'email':run_email,'teamname':run_teamname}, "Your run " + runid + " is older than the set threshold.", "Old run")
                   continue
           else:
               print("Run not paired with timestamp, not able to clean up")
               continue

app = Flask(__name__)
api = Api(app, catch_all_404s=True)

cron = BackgroundScheduler()
cron.add_job(db_cleanup, 'interval', id='job1', hours=config["CLEANUP_INTERVAL_HOURS"])


@app.before_first_request
def limit_request():
    if app.debug:
        return
    Limiter(app, global_limits=["300/minute", "10/second"],
            headers_enabled=True)

@app.before_first_request
def init_rollbar():
    """init rollbar module"""
    if app.debug:
        return
    rollbar.init(
        # access token for the demo app: https://rollbar.com/demo
        core.config.config["ROLLBAR_API_KEY"],
        # environment name
        core.config.config["ROLLBAR_ENV"],
        # server root directory, makes tracebacks prettier
        root=os.path.dirname(os.path.realpath(__file__)),
        # flask already sets up logging
        allow_logging_basic_config=False)

    # send exceptions from `app` to rollbar, using flask's signal system.
    got_request_exception.connect(rollbar.contrib.flask.report_exception, app)


@app.before_request
def before_request():
    g.start = time.time()


@app.after_request
def after_request(response):
    try:
        diff = int((time.time() - g.start) * 1000)
        response.headers.add('X-Execution-Time', str(diff))
    except:
        pass
    return response
