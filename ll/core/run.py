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

from db import db
import random
import datetime
import site


def get_ranking(site_id, site_qid):
    query = db.query.find_one({"site_id": site_id, "site_qid": site_qid})
    if query == None:
        raise LookupError("Query not found: site_qid = '%s'. Only rankings for"
                        "existing queries can be expected." % site_qid)
    run = get_run(query["_id"])
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


def get_run(qid):
    runs = db.run.find({"qid": qid})
    if not runs.count():
        raise LookupError("No runs available for query.")
    participants = set()
    for run in runs:
        participants.add(run["userid"])
    participant = random.choice(list(participants))
    last = None
    selectedrun = None
    runs = db.run.find({"qid": qid,
                        "userid": participant})
    for run in runs:
        if last == None or run["creation_time"] > last:
            last = run["creation_time"]
            selectedrun = run
    return selectedrun


def add_run(key, qid, runid, doclist):
    #run = db.run.find(userid=key, qid=qid, runid=runid)
    #if run.count():
    #    raise Exception("You can not upload a run for for a query twice (you "
    #                    "can increment the runid): qid = '%s', runid = '%s'."
    #                    % (qid, runid))
    q = db.query.find_one({"_id": qid})
    if not q:
        raise Exception("Query does not exit: qid = '%s'" % qid)

    for doc in doclist:
        doc_found = db.doc.find_one({"_id": doc["docid"]})
        if not doc_found:
            raise LookupError("Document not found: docid = '%s'. Add "
                            "only submit runs with existing documents."
                            % doc["docid"])
        doc["site_docid"] = doc_found["site_docid"]
    run = {
        "userid": key,
        "qid": qid,
        "site_qid": q["site_qid"],
        "runid": runid,
        "doclist": doclist,
        "creation_time": datetime.datetime.now(),
        }
    db.run.save(run)
    return run