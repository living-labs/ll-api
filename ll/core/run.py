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
import pymongo
import datetime
import site
import user


def get_ranking(site_id, site_qid):
    query = db.query.find_one({"site_id": site_id, "site_qid": site_qid})
    if query is None:
        raise LookupError("Query not found: site_qid = '%s'. Only rankings "
                          "for existing queries can be expected." % site_qid)
    if "runs" not in query or not query["runs"]:
        raise LookupError("No runs available for query.")
    runid = query["runs"][random.choice(query["runs"].keys())]
    run = db.run.find_one({"runid": runid})
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
        raise Exception("Query does not exist: qid = '%s'" % qid)
    sites = user.get_sites(key)
    if not q["site_id"] in sites:
        raise Exception("First sign up for site %s." % q["site_id"])

    qdoclist = [d["doc_id"] for d in q["doclist"]]
    for doc in doclist:
        if doc["docid"] not in qdoclist:
            raise LookupError("Document not in doclist for this query. "
                              "You may have to update the doclist. "
                              "docid = '%s', qid = '%s'" % (doc["docid"], qid))
        doc_found = db.doc.find_one({"_id": doc["docid"]})
        if not doc_found:
            raise LookupError("Document not found: docid = '%s'. Only submit "
                              "runs with existing documents." % doc["docid"])
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
    if "runs" in q:
        runs = q["runs"]
    else:
        runs = {}
    runs[key] = runid
    q["runs"] = runs
    db.query.save(q)
    return run
