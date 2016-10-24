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
from flask import Flask, g, redirect
from flask.ext.restful import Api, abort
from flask_limiter import Limiter
from flask import got_request_exception
from apscheduler.schedulers.background import BackgroundScheduler

from .. import core
from apiutils import ApiResource, ContentField

from ll.core.db import db
from ll.core.config import config
from ll.core.user import send_email, get_user

import pickle

def db_cleanup():
    print "Database cleanup task started"
    # age_threshold is an absolute point in time
    age_threshold = datetime.datetime.now() - datetime.timedelta(days=config["RUN_AGE_THRESHOLD_DAYS"])
    # reactivation_period is relative
    reactivation_period = datetime.timedelta(days=config["REACTIVATION_PERIOD_DAYS"])

    # First delete runs, then notify outdated. Because there is overlap:
    # deletable runs is a subset of outdated runs
    deletable_runs_age, deletable_runs_doclist = core.run.get_deletable_runs()

    for run in deletable_runs_age:
        # Run is past reactivation period (reason: run older than threshold). Delete.
        run_user = get_user(run["userid"])
        run_user_id = run_user["_id"]
        run_email = run_user["email"]
        run_teamname = run_user["teamname"]


        # Look up query the deletable run belongs to
        q = db.query.find_one({"_id": run["qid"]})
        q_runs = q["runs"]
        # Delete reference to the run from this query, and save
        # Actual run is not removed
        del q_runs[run_user_id]
        q["runs"] = q_runs
        db.query.save(q)
        if config["SEND_EMAIL_RUN_DELETED"]:
            send_email({'email': run_email, 'teamname': run_teamname},
                       "Your outdated run " + run["runid"] + " is past the reactivation period and has been deleted.",
                       "Run deleted")

    for run in deletable_runs_doclist:
        # Run is past reactivation period (reason: run older than doclist). Delete.
        run_user = get_user(run["userid"])
        run_email = run_user["email"]
        run_teamname = run_user["teamname"]

        # Look up query the deletable run belongs to
        q = db.query.find_one({"_id": run["qid"]})
        q_runs = q["runs"]
        # Delete reference to the run from this query, and save
        # Actual run is not removed
        del q_runs[run_user]
        q["runs"] = q_runs
        db.query.save(q)
        if config["SEND_EMAIL_RUN_DELETED"]:
            send_email({'email': run_email, 'teamname': run_teamname},
                   "Your run " + run["runid"] + " is past the reactivation period (document list obsolete) and has been be deleted.",
                   "Run deleted")

    outdated_runs_age, outdated_runs_doclist = core.run.get_outdated_runs()

    for run in outdated_runs_age:
        if config["SEND_EMAIL_RUN_OUTDATED"]:
            # Only send outdated notification if no new notification has been sent
            if "notification_sent_time" not in run or run["notification_sent_time"] < run["creation_time"]:
                # Run older than threshold, send e-mail
                run_user = get_user(run["userid"])
                run_email = run_user["email"]
                run_teamname = run_user["teamname"]

                send_email({'email': run_email, 'teamname': run_teamname},
                           "Your run " + run["runid"] + " is older than the set age threshold of " + str(config["RUN_AGE_THRESHOLD_DAYS"]) + " days. The run will be deleted in " + str(config["REACTIVATION_PERIOD_DAYS"]) + " days. If this run is valuable, you can reactivate it via " +
                           str(config[
                               "URL_REACTIVATION"]) + " inside the reactivation period. After " + str(config["REACTIVATION_PERIOD_DAYS"]) + " days, it is not possible to reactivate anymore.",
                           "Outdated run")

                # Add time of notification to run, so no new notification is sent immediately
                run["notification_sent_time"] = datetime.datetime.now()
                db.run.save(run)

    for run in outdated_runs_doclist:
        if config["SEND_EMAIL_RUN_OUTDATED"]:
            # Only send outdated notification if no new notification has been sent
            if "notification_sent_time" not in run or run["notification_sent_time"] < run["creation_time"]:
                run_user = get_user(run["userid"])
                run_email = run_user["email"]
                run_teamname = run_user["teamname"]
                send_email({'email': run_email, 'teamname': run_teamname},
                           "Your run " + run["runid"] + " is older than the corresponding document list, it will be deactivated in " + str(config["REACTIVATION_PERIOD_DAYS"]) + " days. If this run is valuable, you can reactivate it via " +
                           config[
                               "URL_REACTIVATION"] + " inside the reactivation period. After " + str(config["REACTIVATION_PERIOD_DAYS"]) + " days, it is not possible to reactivate anymore.",
                           "Outdated run")

                # Add time of notification to run, so no new notification is sent immediately
                run["notification_sent_time"] = datetime.datetime.now()
                db.run.save(run)


def calculate_statistics():
    print "Calculate statistics"

    # Calculate site statistics
    sites = core.site.get_sites()
    for site in sites:
        site_id = site["_id"]
        feedbacks = core.db.db.feedback.find({"site_id": site_id})
        clicks = 0

        stats = {
                 "query": core.db.db.query.find({"site_id": site_id}).count(),
                 "doc": core.db.db.doc.find({"site_id": site_id}).count(),
                 "impression": feedbacks.count(),
                 "click": clicks,
        }
        stats_file = "stats_site_" + site_id + ".p"
        pickle.dump(stats,open(stats_file,"wb"))

    # Calculate participant statistics
    participants = core.user.get_participants()
    for participant in participants:
        participant_id = participant["_id"]
        feedbacks = core.feedback.get_feedback(userid=participant_id)

        stats = {
             "run": core.db.db.run.find({"userid": participant_id}).count(),
             "impression": len(feedbacks),
             #"click": clicks,
             "sites": [s["name"] for s in core.site.get_sites()
                       if s["_id"] in core.user.get_sites(participant_id)],
        }
        stats_file = "stats_participant_" + participant_id + ".p"
        pickle.dump(stats,open(stats_file,"wb"))

    # Calculate site statistics for a specific participant
    for participant in participants:
        participant_id = participant["_id"]
        participant_sites = [s for s in core.site.get_sites() if s["_id"] in core.user.get_sites(participant_id)]
        for site in participant_sites:
            site_id = site["_id"]
            feedbacks = core.db.db.feedback.find({"site_id": site_id,
                                              "userid": participant_id})

            clicks = 0
            for feedback in feedbacks:
                if "doclist" not in feedback:
                    continue
                clicks += len([d for d in feedback["doclist"]
                               if "clicked" in d and d["clicked"]])

            stats = {"run": core.db.db.run.find({"site_id": site_id,
                                             "userid": participant_id}).count(),
                 "query": core.db.db.query.find({"site_id": site_id}).count(),
                 "doc": core.db.db.doc.find({"site_id": site_id}).count(),
                 "impression": feedbacks.count(),
                 "click": clicks,
                }
            stats_file = "stats_participant_site_" + participant_id + "_" + site_id + ".p"
            pickle.dump(stats,open(stats_file,"wb"))

    # Calculate admin statistics
    queries = core.query.get_query()
    sites = [s for s in core.site.get_sites()]
    active_participants = set()
    site_participants = {}
    site_queries = {}
    
    for query in queries:
        if not query["site_id"] in site_participants:
            site_participants[query["site_id"]] = [set(), set()]
        if not query["site_id"] in site_queries:
            site_queries[query["site_id"]] = [0, 0]
        if "type" in query and query["type"] == "test":
            site_queries[query["site_id"]][1] += 1
        else:
            site_queries[query["site_id"]][0] += 1
        if "runs" in query:
            for u in query["runs"]:
                active_participants.add(u)
                if "type" in query and query["type"] == "test":
                    site_participants[query["site_id"]][1].add(u)
                else:
                    site_participants[query["site_id"]][0].add(u)

    stats_admin = {"participants": {"verified":  len([u for u in participants
                                                        if u["is_verified"]]),
                                      "all":  len(participants),
                                      "active":  len(active_participants)
                                      },
                     "sites": {"runs": len(site_participants),
                               "all": len(sites),
                               "active": len([s for s in sites if s["enabled"]])},
                     "queries": len(queries),
                     "per_site": {site["_id"]: {"participants": {"train": len(site_participants[site["_id"]][0]), "test":len(site_participants[site["_id"]][1])} if site["_id"] in site_participants else {"train":0, "test":0},
                                                "queries": {"train": site_queries[site["_id"]][0], "test":site_queries[site["_id"]][1]} if site["_id"] in site_queries else {"train":0, "test":0}
                                            } for site in sites
                                  }
                     }
    stats_admin_file = "stats_admin.p"
    pickle.dump(stats_admin,open(stats_admin_file,"wb"))



app = Flask(__name__)
api = Api(app, catch_all_404s=True)

cron = BackgroundScheduler()
#cron.add_job(db_cleanup, 'interval', id='cleanjob', hours=config["CLEANUP_INTERVAL_HOURS"])
cron.add_job(calculate_statistics, 'interval', id='statjob', hours=config["CALC_STATS_INTERVAL_HOURS"])


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

@app.route("/")
def hello():
    return redirect(core.config.config["URL_DOC"])
