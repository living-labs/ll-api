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

import slugify
from db import db
from config import config
import random
import pymongo
import datetime
import site
import user
import query
import feedback

def get_ranking(site_id, site_qid):
    query = db.query.find_one({"site_id": site_id, "site_qid": site_qid})
    if query is None:
        raise LookupError("Query not found: site_qid = '%s'. Only rankings "
                          "for existing queries can be expected." % site_qid)
    if "runs" not in query or not query["runs"]:
        raise LookupError("No rankings available for query: site_qid = '%s'. "
                          "Participants will have to submit runs first. "
                          "Sites should be able to handle such errors."
                          % site_qid)
    allruns = query["runs"].items()
    random.shuffle(allruns)
    for userid, runid_pair in allruns:
        # Check if runid is paired with a timestamp (new format)
        if isinstance(runid_pair, list):
            runid, run_modified_time = runid_pair
        else:
            # Not paired with timestamp, only runid present (old format)
            runid = runid_pair
        runs = db.run.find({"runid": runid,
                            "site_qid": site_qid,
                            "userid": userid
                            }).hint([("runid", pymongo.ASCENDING),
                                     ("site_qid", pymongo.ASCENDING),
                                     ("userid", pymongo.ASCENDING)
                                     ])
        run = runs[0]
        if len(run["doclist"]) > 0:
            break
    sid = site.next_sid(site_id)
    feedback = {
        "_id": sid,
        "site_qid": site_qid,
        "site_id": site_id,
        "qid": query["_id"],
        "runid": run["runid"],
        "userid": run["userid"],
        "creation_time": datetime.datetime.now(),
    }
    db.feedback.save(feedback)
    run["sid"] = sid
    return run


def add_run(key, qid, runid, doclist):
    q = db.query.find_one({"_id": qid})
    if not q:
        raise LookupError("Query does not exist: qid = '%s'" % qid)

    in_test_period = False
    for test_period in config["TEST_PERIODS"]:
        if test_period["START"] < datetime.datetime.now() < test_period["END"]:
            in_test_period = True
            break

    if in_test_period and "type" in q and q["type"] == "test" \
            and "runs" in q and key in q["runs"]:
        raise ValueError("For test queries you can only upload a run once "
                         "during a test period.")
    sites = user.get_sites(key)
    if q["site_id"] not in sites:
        raise LookupError("First sign up for site %s." % q["site_id"])
    if len(doclist) == 0:
        raise ValueError("The doclist should contain documents.")
    for doc in doclist:
        doc_found = db.doc.find_one({"_id": doc["docid"]})
        if not doc_found:
            raise LookupError("Document not found: docid = '%s'. Only submit "
                              "runs with existing documents." % doc["docid"])
        doc["site_docid"] = doc_found["site_docid"]

    creation_time = datetime.datetime.now()
    run = {
        "userid": key,
        "qid": qid,
        "site_qid": q["site_qid"],
        "site_id": q["site_id"],
        "runid": runid,
        "doclist": doclist,
        "creation_time": creation_time,
    }
    db.run.remove({"runid": runid,
                   "qid": qid,
                   "userid": key})
    db.run.save(run)
    if "runs" in q:
        runs = q["runs"]
    else:
        runs = {}
    runs[key] = (runid, creation_time)

    q["runs"] = runs
    db.query.save(q)
    return run


def get_run(key, qid):
    q = db.query.find_one({"_id": qid})
    if not q:
        raise LookupError("Query does not exist: qid = '%s'" % qid)

    if "runs" not in q or key not in q["runs"]:
        raise LookupError("No run for this query: qid = '%s'" % qid)

    runid = q["runs"][key][0]

    run = db.run.find_one({"userid": key,
                           "qid": qid,
                           "runid": runid})
    return run


def get_trec_run(runs, periodname, teamname):
    runname = slugify.slugify(unicode("%s %s" % (periodname, teamname)))
    trec = []
    for qid in sorted(runs.keys()):
        ndoc = len(runs[qid]["doclist"])
        for rank, d in enumerate(runs[qid]["doclist"]):
            trec.append("%s Q0 %s %d %d %s" % (qid, d["docid"], rank,
                                               ndoc - rank, runname))
    return {"trec": "\n".join(trec),
            "name": runname}


def get_trec_qrel(feedbacks, periodname, rawcount=False):
    periodname = slugify.slugify(unicode(periodname))
    trec = []

    for qid in sorted(feedbacks.keys()):
        click_stat = {}
        count = 0
        for feedback in feedbacks[qid]:
            for d in feedback["doclist"]:
                if not d["docid"] in click_stat:
                    click_stat[d["docid"]] = [0, 0]
                if "clicked" in d and (d["clicked"] is True or
                                           (isinstance(d["clicked"], list) and
                                                    len(d["clicked"]) > 0)):
                    click_stat[d["docid"]][0] += 1
                click_stat[d["docid"]][1] += 1
            count += 1
        ctrs = []
        for d in click_stat:
            if rawcount:
                ctrs.append((click_stat[d][0], d))
            else:
                ctrs.append((float(click_stat[d][0]) / count, d))
        for ctr, d in sorted(ctrs, reverse=True):
            if rawcount:
                trec.append("%s 0 %s %d" % (qid, d, ctr))
            else:
                trec.append("%s 0 %s %.6f" % (qid, d, ctr))

    return {"trec": "\n".join(trec),
            "name": periodname}


def get_trec(site_id):
    trec_runs = []
    trec_qrels = []
    trec_qrels_raw = []
    queries = query.get_query(site_id)
    participants = user.get_participants()
    for test_period in config["TEST_PERIODS"]:
        if datetime.datetime.now() < test_period["END"]:
            continue
        for participant in participants:
            userid = participant["_id"]
            participant_runs = {}
            for q in queries:
                if "type" not in q or not q["type"] == "test":
                    continue
                qid = q["_id"]
                runs = db.run.find({"userid": userid,
                                    "qid": qid})
                if not runs:
                    continue
                testrun = None
                testrundate = datetime.datetime(2000, 1, 1)
                for run in runs:
                    if testrundate < run["creation_time"] < test_period["END"]:
                        testrundate = run["creation_time"]
                        testrun = run
                if not testrun:
                    continue
                participant_runs[qid] = testrun

            if participant_runs:
                trec_runs.append(get_trec_run(participant_runs,
                                              test_period["NAME"],
                                              participant["teamname"]))
        test_period_feedbacks = {}
        for q in queries:
            if "type" not in q or not q["type"] == "test":
                continue
            qid = q["_id"]
            feedbacks = feedback.get_test_feedback(site_id=site_id, qid=qid)
            test_period_feedbacks[qid] = [f for f in feedbacks if (test_period["START"] <
                                                                   f["modified_time"] <
                                                                   test_period["END"])]
        trec_qrels.append(get_trec_qrel(test_period_feedbacks,
                                        test_period["NAME"]))
        trec_qrels_raw.append(get_trec_qrel(test_period_feedbacks,
                                            test_period["NAME"],
                                            rawcount=True))
    return trec_runs, trec_qrels, trec_qrels_raw


# Remove all runs submitted by a certain participant
def remove_runs_user(key):
    q = {"deleted": {"$ne": True}}
    queries = [query for query in db.query.find(q)]
    # print "Before"
    # print queries
    for query in queries:
        if "runs" in query:
            runs = query["runs"]
            if key in runs:
                print "Removing runid " + runs[key]
                del runs[key]

            # Update runs list
            query["runs"] = runs
            db.query.save(query)
    # print "After"
    # print [query for query in db.query.find(q)]

    # Return resulting query list, with removed runs
    return [query for query in db.query.find(q)]


# Get all runs by a certain user
def get_runs(key):
    q = {"deleted": {"$ne": True}}
    queries = [query for query in db.query.find(q)]
    runs_user = []
    for query in queries:
        if "runs" in query:
            runs = query["runs"]
            if key in runs:
                runs_user.append(runs[key])
    return runs_user

# Get outdated runs which are past the reactivation period and can be deleted.
# With argument: get runs for specific user. Without argument: get all deletable runs
def get_deletable_runs(selected_user=None):
    age_threshold = datetime.datetime.now() - datetime.timedelta(days=config["RUN_AGE_THRESHOLD_DAYS"])
    reactivation_period = datetime.timedelta(days=config["REACTIVATION_PERIOD_DAYS"])

    # Get list of all queries
    q = {"deleted": {"$ne": True}}
    queries = [query for query in db.query.find(q)]
    deletable_runs_age = []
    deletable_runs_doclist = []
    for query in queries:
        allruns = query.get("runs", {}).items()
        for userid, runid_pair in allruns:
            print userid
            print selected_user
            # If selected_user == None, no specific user is specified, and all outdated runs will be added
            # If a user is selected, only outdated runs for this user will be added
            if selected_user == None or userid == selected_user:
                # Check if runid is paired with a timestamp (new format)
                if isinstance(runid_pair, list):
                    runid, run_modified_time = runid_pair
                    if 'doclist_modified_time' in query:
                        print "Run modified time: " + str(run_modified_time)
                        print "Doclist modified time: " + str(query['doclist_modified_time'])
                        if run_modified_time < (query['doclist_modified_time'] - reactivation_period):
                            print("Run older than latest doclist")
                            # Look up full run and append this to deletable runs list
                            full_run = db.run.find_one({"runid": runid,
                                                        "qid": query['_id'],
                                                        "userid": userid})
                            deletable_runs_doclist.append(full_run)

                            continue
                    if run_modified_time < (age_threshold - reactivation_period):

                        print "Run older than threshold + reactivation period."
                        print "Run modified time: " + str(run_modified_time)
                        print "Age threshold - reaction period: " + str(age_threshold - reactivation_period)
                        # Look up full run and append this to deletable runs list
                        full_run = db.run.find_one({"runid": runid,
                                                    "qid": query['_id'],
                                                    "userid": userid})
                        deletable_runs_age.append(full_run)

                        continue
                else:
                    print("Run not paired with timestamp, not able to clean up")
                    continue

    return (deletable_runs_age, deletable_runs_doclist)


# Get all outdated runs: runs which are older than their doclist or older than a threshold
# With argument: get runs for specific user. Without argument: get all outdated runs
def get_outdated_runs(selected_user=None):
    age_threshold = datetime.datetime.now() - datetime.timedelta(days=config["RUN_AGE_THRESHOLD_DAYS"])

    # Get list of all queries
    q = {"deleted": {"$ne": True}}
    queries = [query for query in db.query.find(q)]
    outdated_runs_age = []
    outdated_runs_doclist = []
    for query in queries:
        allruns = query.get("runs", {}).items()
        for userid, runid_pair in allruns:
            print userid
            print selected_user
            # If selected_user == None, no specific user is specified, and all outdated runs will be added
            # If a user is selected, only outdated runs for this user will be added
            if selected_user == None or userid == selected_user:
                # Check if runid is paired with a timestamp (new format)
                if isinstance(runid_pair, list):
                    runid, run_modified_time = runid_pair
                    if 'doclist_modified_time' in query:
                        print "Run modified time: " + str(run_modified_time)
                        print "Doclist modified time: " + str(query['doclist_modified_time'])
                        if run_modified_time < query['doclist_modified_time']:
                            print("Run older than latest doclist")
                            # Look up full run and append this to outdated runs list
                            full_run = db.run.find_one({"runid": runid,
                                                        "qid": query['_id'],
                                                        "userid": userid})
                            outdated_runs_doclist.append(full_run)

                            continue
                    if run_modified_time < age_threshold:
                        print("Run older than threshold")
                        # Look up full run and append this to outdated runs list
                        full_run = db.run.find_one({"runid": runid,
                                                    "qid": query['_id'],
                                                    "userid": userid})
                        outdated_runs_age.append(full_run)

                        continue
                else:
                    print("Run not paired with timestamp, not able to clean up")
                    continue

    return (outdated_runs_age, outdated_runs_doclist)

# Reactivate designated outdated runs
def reactivate_runs(runs):
    reactivated_runs = []
    for run in runs:
        # Run dict is encoded as json string, decode

        new_creation_time = datetime.datetime.now()
        new_run = dict(run) # copy of current run
        new_run["creation_time"] = new_creation_time

        db.run.remove(run)
        db.run.save(new_run)

        qid = run["qid"]
        userid = run["userid"]
        q = db.query.find_one({"_id": qid})
        runid = run["runid"]

        if not q:
            raise LookupError("Query does not exist: qid = '%s'" % qid)
        if "runs" in q:
            runs = q["runs"]
        else:
            runs = {}
        runs[userid] = (runid, new_creation_time)

        q["runs"] = runs
        db.query.save(q)
        print "Updated run"
        print new_run
        print "Updated query runs"
        print runs

        reactivated_runs += new_run
    return reactivated_runs
