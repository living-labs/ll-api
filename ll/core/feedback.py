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

import datetime, pymongo
from db import db
from config import config
import doc, query, user
import json
from pprint import pprint

def add_feedback_from_json(json_file,mongodb_host, mongodb_port, mongodb_db, mongodb_user, mongodb_user_pw, mongodb_auth_db):
    with open(json_file,"r") as feedback_file:
        feedbacks = json.load(feedback_file)
        for feedback in feedbacks[:1]:
            print feedback
            
    #existing_feedback = db.feedback.find_one({"site_id": site_id, "_id": sid})
    #if existing_feedback is None:
        #raise LookupError("Session not found: sid = '%s'." % sid)
    #for doc in feedback["doclist"]:
        #doc_found = db.doc.find_one({"site_id": site_id,
                                     #"site_docid": doc["site_docid"]
                                     #})
        #if not doc_found:
            #raise LookupError("Document not found: site_docid = '%s'. Please"
                            #"only provide feedback for documents that are"
                            #"allowed for a query." % doc["site_docid"])
        #doc["docid"] = doc_found["_id"]

    #for k in feedback:
        #existing_feedback[k] = feedback[k]
    
    #existing_feedback["modified_time"] = datetime.datetime.now()
    #db.feedback.save(existing_feedback)
    #return existing_feedback

def add_feedback(site_id, sid, feedback):
    existing_feedback = db.feedback.find_one({"site_id": site_id, "_id": sid})
    if existing_feedback is None:
        raise LookupError("Session not found: sid = '%s'." % sid)
    for doc in feedback["doclist"]:
        doc_found = db.doc.find_one({"site_id": site_id,
                                     "site_docid": doc["site_docid"]
                                     })
        if not doc_found:
            raise LookupError("Document not found: site_docid = '%s'. Please"
                            "only provide feedback for documents that are"
                            "allowed for a query." % doc["site_docid"])
        doc["docid"] = doc_found["_id"]

    for k in feedback:
        existing_feedback[k] = feedback[k]
    
    existing_feedback["modified_time"] = datetime.datetime.now()
    db.feedback.save(existing_feedback)
    return existing_feedback


def add_historical_feedback(site_id, site_qid, feedback):
    query = db.query.find_one({"site_id": site_id, "site_qid": site_qid})
    if query is None:
        raise LookupError("Query not found: site_qid = '%s'." % site_qid)

    for doc in feedback["doclist"]:
        doc_found = db.doc.find_one({"site_id": site_id,
                                     "site_docid": doc["site_docid"]
                                     })
        if not doc_found:
            raise LookupError("Document not found: site_docid = '%s'. Please"
                              "only provide historical feedback for documents"
                              "that are allowed for a query."
                              % doc["site_docid"])
        doc["docid"] = doc_found["_id"]

    feedback["site_id"] = site_id
    feedback["site_qid"] = site_qid
    feedback["qid"] = query["_id"]
    feedback["creation_time"] = datetime.datetime.now()
    feedback["modified_time"] = datetime.datetime.now()

    db.historical.save(feedback)
    return feedback


def reset_feedback(userid=None, site_id=None, sid=None, qid=None):
    q = {}
    if userid:
        q["userid"] = userid
    if site_id:
        q["site_id"] = site_id
    if sid:
        q["sid"] = sid
    if qid:
        q["qid"] = qid
    db.feedback.remove(q)


def get_feedback(userid=None, site_id=None, sid=None, qid=None, runid=None):
    q = {"doclist": {"$exists": True}}
    if userid:
        q["userid"] = userid
    if site_id:
        q["site_id"] = site_id
    if sid:
        q["sid"] = sid
    if qid and qid.lower() != "all":
        q["qid"] = qid
    if runid:
        q["runid"] = runid

    if "qid" in q and "site_id" in q and "userid" in q:
        feedbacks = db.feedback.find(q).hint([("qid", pymongo.ASCENDING),
                                              ("site_id", pymongo.ASCENDING),
                                              ("userid", pymongo.ASCENDING)
                                              ])
    elif "site_id" in q and "userid" in q:
        feedbacks = db.feedback.find(q).hint([("site_id", pymongo.ASCENDING),
                                              ("userid", pymongo.ASCENDING)
                                              ])
    else:
        feedbacks = db.feedback.find(q)

    readyfeedback = []
    qid_types = {}
    for feedback in feedbacks:
        qid = feedback["qid"]
        if qid not in qid_types:
            query = db.query.find_one({"_id": qid})
            if query and "type" in query and query["type"] == "test":
                qid_types[qid] = "test"
            else:
                qid_types[qid] = "train"
        if qid_types[qid] == "train":
            readyfeedback.append(feedback)
    return readyfeedback


def get_test_feedback(userid=None, site_id=None, qid=None, qtype=None, runid=None):
    q = {"doclist": {"$exists": True}}
    if userid:
        q["userid"] = userid
    if site_id:
        q["site_id"] = site_id

    if qid and qid.lower() != "all":
        q["qid"] = qid

    if runid:
        q["runid"] = runid

    if "qid" in q and "site_id" in q and "userid" in q:
        feedbacks = db.feedback.find(q).hint([("qid", pymongo.ASCENDING),
                                              ("site_id", pymongo.ASCENDING),
                                              ("userid", pymongo.ASCENDING)
                                              ])
    elif "site_id" in q and "userid" in q:
        feedbacks = db.feedback.find(q).hint([("site_id", pymongo.ASCENDING),
                                              ("userid", pymongo.ASCENDING)
                                              ])
    else:
        feedbacks = db.feedback.find(q)

    if qtype is not None:
        if qtype == "test":
            qtype_qids = set([q["_id"] for q in query.get_query(site_id=site_id)
                              if "type" in q and q["type"] == "test"])
        else:
            qtype_qids = set([q["_id"] for q in query.get_query(site_id=site_id)
                              if ("type" in q and q["type"] != "test") or "type" not in q])

    readyfeedback = []
    for f in feedbacks:
        if qtype is not None:
            if f["qid"] in qtype_qids:
                readyfeedback.append(f)
        else:
            readyfeedback.append(f)
    return readyfeedback


def get_comparison(userid=None, site_id=None, qtype=None, qid=None):
    def get_outcome(feedback):
        participant_wins = 0
        site_wins = 0
        for d in feedback["doclist"]:
            if "clicked" in d and (d["clicked"] is True or
                                   (isinstance(d["clicked"], list) and
                                    len(d["clicked"]) > 0)):
                if "team" in d and d["team"] == "participant":
                    participant_wins += 1
                elif "team" in d and d["team"] == "site":
                    site_wins += 1
        return 1 if participant_wins > site_wins else -1 \
            if participant_wins < site_wins else 0

    def get_outcomes(feedbacks, outcomes, test_period=None,
                     return_outcome=False):
        if test_period and datetime.datetime.now() < test_period["END"]:
            return

        nr_wins = 0
        nr_losses = 0
        nr_ties = 0
        for f in feedbacks:
            if test_period and not (test_period["START"] <
                                    f["modified_time"] <
                                    test_period["END"]):
                continue

            outcome = get_outcome(f)
            if outcome > 0:
                nr_wins += 1
            elif outcome < 0:
                nr_losses += 1
            else:
                nr_ties += 1

        agg_outcome = float(nr_wins) / (nr_wins + nr_losses) if nr_wins + nr_losses > 0 else 0
        impressions = nr_wins + nr_losses + nr_ties
        if impressions > 0 or return_outcome:
            outcome_struct = {"qid": qid,
                              "type": qtype,
                              "site_id": site_id,
                              "outcome": agg_outcome,
                              "wins": nr_wins,
                              "losses": nr_losses,
                              "ties": nr_ties,
                              "impressions": impressions}
            if test_period:
                outcome_struct["test_period"] = test_period
            outcomes.append(outcome_struct)

    if site_id is not None:
        site_ids = [site_id]
    else:
        site_ids = user.get_sites(userid)
        if not site_ids:
            raise Exception("First signup for sites.")

    if qtype is not None:
        qtypes = [qtype]
        return_outcome = True
    else:
        qtypes = ["test", "train"]
        return_outcome = False

    if qid is None:
        qid = "all"

    outcomes = []
    for site_id in site_ids:
        for qtype in qtypes:
            feedbacks = get_test_feedback(userid=userid, site_id=site_id,
                                          qtype=qtype, qid=qid)
            if qtype == "test":
                for test_period in config["TEST_PERIODS"]:
                    get_outcomes(feedbacks, outcomes,
                                 test_period=test_period,
                                 return_outcome=return_outcome)
            else:
                get_outcomes(feedbacks, outcomes,
                             return_outcome=return_outcome)
    return outcomes


def get_historical_feedback(site_id=None, qid=None, site_qid=None):
    q = {}
    if site_id:
        q["site_id"] = site_id
    if site_qid and site_qid.lower() != "all":
        q["site_qid"] = site_qid
    if qid and qid.lower() != "all":
        q["qid"] = qid
    return db.historical.find(q)
